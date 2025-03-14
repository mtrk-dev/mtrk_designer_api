import mtrkPulpy as mpp
import matplotlib.pyplot as plt
import numpy
from SDL_read_write.pydanticSDLHandler import *

# fov (float): imaging field of view in cm.
# n (int): # of pixels (square). N = etl*nl, where etl = echo-train-len
#     and nl = # leaves (shots). nl default 1.
# etl (int): echo train length.
# dt (float): sample time in s.
# gamp (float): max gradient amplitude in mT/m.
# gslew (float): max slew rate in mT/m/ms.
# offset (int): used for multi-shot EPI goes from 0 to #shots-1
# dirx (int): x direction of EPI -1 left to right, 1 right to left
# diry (int): y direction of EPI -1 bottom-top, 1 top-bottom

def add_epi_train(base_sequence, insertion_block, previous_block, n, etl, gamp, gslew, offset=0, dirx=-1, diry=1):

    fov = round(base_sequence.infos.fov * 1e-4, 6)  # Is the FOV in the right unit now?
    dt = 1e-5

    blocks = mpp.mtrk_epi(fov, n, etl, dt, gamp, gslew, offset, dirx, diry)
    for instruction in base_sequence.instructions.keys():
        if instruction == insertion_block:
            updated_insertion_block = insertion_block
            break
        else:
            updated_insertion_block = "main"
    if updated_insertion_block == "main":
        print("block not found: " + insertion_block + ". main block will be used instead.")
    insertion_block = updated_insertion_block
    if updated_insertion_block == "main":
        print("block not found: " + insertion_block + ". main block will be used instead.")
    insertion_block = updated_insertion_block

    ## Inserting block_epi after the previous block
    target_runblock = RunBlock(action='run_block', block=previous_block)
    previous_block_index = None
    for i, obj in enumerate(base_sequence.instructions[insertion_block].steps):
        if isinstance(obj, RunBlock) and obj.block == target_runblock.block:
            previous_block_index = i
    base_sequence.instructions[insertion_block].steps.insert(int(previous_block_index) + 1, RunBlock(action = "run_block", block = "block_epi"))

    ## Creating a main loop

    string_instructions = str(base_sequence.instructions)

    ## Counting the number of loops in the instructions to determine next counter
    start = 0
    counter_index = 1
    while True:
        start = string_instructions.find("Loop(", start)
        if start == -1:
            break
        counter_index += 1
        start += len("Loop(")  # Move past the last found word

    # epiLoop = Loop(counter = counter_index, range = 1, 
    #                 steps = [])
    # counter_index += 1
    base_sequence.instructions.update({"block_epi" : {}})
    block = Instruction(print_counter = "on",
                        print_message = "Running EPI echo train",
                        steps = [])
    base_sequence.instructions["block_epi"].update(block)
    # base_sequence.instructions["block_epi"]["steps"].append(epiLoop)
    
    ## Initializing the main block
    init = Init(gradients="logical")
    base_sequence.instructions["block_epi"]["steps"].append(init)

    ## Looping over blocks
    for block_index in range(0, len(blocks)):
        ## Creating loops (only if the iteration number is greater than 1)
        loop_iterations = blocks[block_index][0]
        block = Instruction(print_counter = "on",
                            print_message = "Running block " + str(block_index),
                            steps = [])
        
        base_sequence.instructions.update({"block_" + str(block_index) : {}})
        base_sequence.instructions["block_" + str(block_index)].update(block)
        if loop_iterations > 1:
            loop = Loop(counter = counter_index, 
                        range = loop_iterations, 
                        steps = [Step(action = "run_block", 
                                      block = "block_" + str(block_index))])
            counter_index += 1
            base_sequence.instructions["block_epi"]["steps"].append(loop)
        else:
            step = Step(action = "run_block", 
                        block = "block_" + str(block_index))
            base_sequence.instructions["block_epi"]["steps"].append(step)

        ## Initializing the block
        init = Init(gradients="logical")
        base_sequence.instructions["block_" + str(block_index)]["steps"].append(init)

        ## Looping over block instructions
        for index in range(1, len(blocks[block_index])):
            ## Combined index to identify instructions, objects and arrays
            combined_index = str(block_index) + "_" + str(index)

            ## Creating gradient events, along with their respective arrays and objects
            if blocks[block_index][index][2] == "read" or blocks[block_index][index][2] == "slice" or blocks[block_index][index][2] == "phase":
                ## Creating gradient arrays
                data = blocks[block_index][index][0]
                size = blocks[block_index][index][1]
                if blocks[block_index][index][0][-1] != 0.0:
                    data = numpy.append(blocks[block_index][index][0], 0.0)
                    size = blocks[block_index][index][1] + 1
                grad_array = GradientTemplate(encoding = "text", 
                                              type = "float",
                                              size = size,
                                              data = data)
                ## Checking if the array already exists in the arrays section
                if dict(grad_array) in base_sequence.arrays.values():
                    array_name = [key for key, value in base_sequence.arrays.items() if value == dict(grad_array)][0] 
                else:
                    array_name = "grad_array_" + combined_index
                    base_sequence.arrays.update({array_name: {}})
                    base_sequence.arrays[array_name].update(grad_array)

                ## Creating gradient objects
                grad_object = GradientObject(duration = blocks[block_index][index][1] * 10, 
                                             array = array_name, 
                                             tail = 0, 
                                             amplitude = blocks[block_index][index][3])
                ## Checking if the gradient already exists in the gradients section
                if dict(grad_object) in base_sequence.objects.values():
                    object_name = [key for key, value in base_sequence.objects.items() if value == dict(grad_object)][0] 
                else:
                    object_name = "grad_object_" + combined_index
                    base_sequence.objects.update({object_name: {}})
                    base_sequence.objects[object_name].update(grad_object)

                ## Creating gradient instructions
                gradient = Grad(axis = blocks[block_index][index][2], 
                                object = object_name, 
                                time = int(blocks[block_index][index][4]*1e5))
                base_sequence.instructions["block_" + str(block_index)]["steps"].append(gradient)

            ## Creating ADC events, along with their respective objects       
            elif blocks[block_index][index][2] == "adc":
                print("ADC CREATION")
                ## Creating ADC objects
                adc_object = AdcReadout(duration = blocks[block_index][index][1]*10, 
                                        samples = blocks[block_index][index][1], 
                                        dwelltime = 10000)

                ## Checking if the ADC object already exists in the objects section
                if dict(adc_object) in base_sequence.objects.values():
                    object_name = [key for key, value in base_sequence.objects.items() if value == dict(adc_object)][0] 
                else:
                    object_name = "adc_object_" + combined_index
                    base_sequence.objects.update({object_name: {}})
                    base_sequence.objects[object_name].update(adc_object)

                ## Creating ADC instructions
                mdhOptionsDict = { "line": MdhOption(type = "counter", counter = block_index), 
                                   "first_scan_slice": MdhOption(type = "counter", counter = block_index, target = 0),
                                   "last_scan_slice": MdhOption(type = "counter", counter = block_index, target = loop_iterations-1)}
                adc = Adc(object = object_name, 
                          time = int(blocks[block_index][index][4]*1e5), 
                          frequency = 0, 
                          phase = 0, 
                          added_phase = AddedPhase(type = "float", 
                                                   float = 0.0), 
                          mdh = mdhOptionsDict)
                base_sequence.instructions["block_" + str(block_index)]["steps"].append(adc)
        
        ## Closing the block
        submit =  Submit()
        base_sequence.instructions["block_" + str(block_index)]["steps"].append(submit)

    ## Closing the main block
    submit =  Submit()
    base_sequence.instructions["block_epi"]["steps"].append(submit)

    return base_sequence

def block_duration(base_sequence, block):
    latest_start_time = 0
    for step in block.steps:
        if step.action == "grad":
            if step.time > latest_start_time:
                latest_start_time = step.time

    longest_duration = 0
    for step in block.steps:
        if step.action == "grad" and step.time == latest_start_time:
            if base_sequence.objects[step.object].duration > longest_duration:
                longest_duration = base_sequence.objects[step.object].duration

    return latest_start_time + longest_duration