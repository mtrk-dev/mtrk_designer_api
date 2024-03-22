################################################################################
### mtrk project - Transition from backend to UI                             ###
### Version 1.0.0                                                            ###
### Anais Artiges and the mtrk project team at NYU - 01/31/2024              ###
################################################################################  

import json
import jsbeautifier
import re
import ast
from pprint import pprint
from devtools import debug
from numpy import add
from sdlFileCreator import *

#############################################################
### Creating SDL file from web-based UI
#############################################################

def create_sdl_from_ui_inputs(boxes, block_structure, configurations, events):
    # Initialize SDL file
    # TO DO - need to intialize without loading file
    print("+-+-+ block_structure " + str(block_structure))
    with open('C:/Users/artiga02/mtrk_seq/examples/miniflash.mtrk') as sdlFile:
        sdlData = json.load(sdlFile)
        sequence_data = PulseSequence(**sdlData)
    sdlInitialize(sequence_data)

    updateSDLFile(sequence_data, boxes, configurations)
    
    ### writing of json schema to SDL file with formatting options
    with open('output.mtrk', 'w') as sdlFileOut:
        options = jsbeautifier.default_options()
        options.indent_size = 4
        data_to_print = jsbeautifier.beautify(\
                     json.dumps(sequence_data.model_dump(mode="json")), options)
        sdlFileOut.write(re.sub(r'}, {', '},\n            {', data_to_print)) 
        #purely aesthetic

def updateSDLFile(sequence_data, boxes, configurations):
    keys = boxes.keys()
    for boxKey in keys:
        boxList = boxes[boxKey]
        # if boxKey == "Main":
        #     pass
        # else:
        instructionName = boxKey
        addInstruction(sequence_data, instructionName)
        instructionInformationList = getInstructionInformation(
                                                boxes = boxList,
                                                instructionName = \
                                                     instructionName)
        completeInstructionInformation(sequence_data = sequence_data, 
                                       instructionInformationList = \
                                                     instructionInformationList)
    fileInformationList = getFileInformation(configurations = configurations)
    completeFileInformation(sequence_data = sequence_data, 
                            fileInformationList = fileInformationList)
    settingsInformationList = getSequenceSettingsInformation(
                                                configurations = configurations)
    completeSequenceSettings(sequence_data = sequence_data, 
                             settingsInformationList = settingsInformationList)
    sequenceInfoInformationList = getSequenceInfoInformation(
                                                configurations = configurations)
    completeSequenceInformation(
                      sequence_data = sequence_data, 
                      sequenceInfoInformationList = sequenceInfoInformationList)

        
#############################################################
### Functions to get new values from the web-based UI
#############################################################

def getFileInformation(configurations):
    formatInfo = configurations["file"]["format"]
    versionInfo = configurations["file"]["version"]
    measurementInfo = configurations["file"]["measurement"]
    systemInfo = configurations["file"]["system"]
    fileInformationList = [formatInfo, versionInfo, measurementInfo, 
                           systemInfo]
    return fileInformationList

def getSequenceSettingsInformation(configurations):
    readoutOsInfo = configurations["settings"]["readout"]
    settingsInformationList = [readoutOsInfo]
    return settingsInformationList    

def getSequenceInfoInformation(configurations):
    descriptionInfo = configurations["info"]["description"]
    slicesInfo = configurations["info"]["slices"]
    fovInfo = configurations["info"]["fov"]
    ## TO DO complete pe lines from UI
    # pelinesInfo = configurations["info"]["pe_lines"]
    pelinesInfo = "42"
    seqstringInfo = configurations["info"]["seqstring"]
    reconstructionInfo = configurations["info"]["reconstruction"]
    sequenceInfoInformationList = [descriptionInfo, slicesInfo, fovInfo, 
                                   pelinesInfo, seqstringInfo, 
                                   reconstructionInfo]
    return sequenceInfoInformationList

def getInstructionInformation(boxes, instructionName):
    # TO DO add "message" to the dictionnary
    # printMessageInfo = box["message"]
    printMessageInfo = "dummy_message"
    # TO DO add "print_counter_on_off" to the dictionnary
    # printCounterInfo = box["print_counter_on_off"]
    printCounterInfo = "off"
    allStepInformationLists = []
    for box in boxes:
        stepInformationList = getStepInformation(box)
        allStepInformationLists.append(stepInformationList)
    instructionInformationList = [instructionName, printMessageInfo,\
                                  printCounterInfo, allStepInformationLists]
    return instructionInformationList
            
def getStepInformation(box):
    actionName = box["type"]
    stepInformationList = [actionName]
    match actionName:
        case "Block":
            pass
        case "run_block":
            # TO DO add "block_name" to the dictionnary
            # allStepInformationLists = box["block_name"]
            blockName = "dummy_block_name"
            blockInformationList = getInstructionInformation(blockName)
            stepInformationList.extend([blockName, blockInformationList])

        case "loop":
            # TO DO add "counter_number" to the dictionnary
            # allStepInformationLists = box["counter_number"]
            counterInfo = 1
            # TO DO add "counter_range" to the dictionnary
            # allStepInformationLists = box["counter_range"]
            rangeInfo = 1
            # TO DO add "all_step_info_lists" to the dictionnary
            # allStepInformationLists = box["all_step_info_lists"]
            # TO DO We need to decide either giving directly the 
            # all_step_info_lists or giving a list of step information from 
            # which it is extracted. 
            allStepInformationLists = []
            for stepInformationList in allStepInformationLists:
                newStepInformationList = getStepInformation()
                allStepInformationLists.append(newStepInformationList)
            stepInformationList.extend([counterInfo, rangeInfo, 
                                        allStepInformationLists])  
            
        case "calc":
            # TO DO add "type" to the dictionnary
            typeInfo = box["type"]
            # typeInfo = "dummy_type"
            # TO DO add "float" to the dictionnary
            floatInfo = box["float"]
            # floatInfo = 0.0
            # TO DO add "increment" to the dictionnary
            incrementInfo = box["increment"]
            # incrementInfo = 0
            stepInformationList.extend([typeInfo, floatInfo, incrementInfo]) 

        case "init":
            # TO DO add "gradient_mode" to the dictionnary
            # allStepInformationLists = box["gradient_mode"]
            gradientInfo = "dummy_gradient_mode"
            stepInformationList.extend([gradientInfo]) 

        case "sync":
            # TO DO add "object_name" to the dictionnary
            # allStepInformationLists = box["object_name"]
            objectInfo = "dummy_object_name"
            objectInformationList = getObjectInformation(actionName)
            # TO DO add "time" to the dictionnary
            # allStepInformationLists = box["time"]
            timeInfo = 0
            stepInformationList.extend([objectInfo, objectInformationList, 
                                        timeInfo]) 
            
        case "grad":
            axisInfo = box["axis"]
            objectInfo = box["name"]
            objectInformationList = getObjectInformation(typeInfo = actionName, 
                                                         box = box)
            timeInfo = int(float(box["start_time"]))
            stepInformationList.extend([axisInfo, objectInfo, 
                                        objectInformationList, timeInfo]) 
            # TO DO add "amplitude_flip" to the dictionnary
            # if(box["amplitude_flip"]=="true"):
            #     flipAmplitudeInfo = "flip"
            #     stepInformationList.extend([flipAmplitudeInfo])
            if(box["variable_amplitude"]=="true"):
                amplitudeTypeInfo = "equation"
                # TO DO add "equation_name" to the dictionnary
                # amplitudeEquationNameInfo = box["equation_name"]
                amplitudeEquationNameInfo = "dummy_eq_name"
                stepInformationList.extend([amplitudeTypeInfo, 
                                            amplitudeEquationNameInfo])
                # TO DO add "equation_expression" to the dictionnary
                # equationInfo = box["equation_expression"]
                equationInfo = "dummy_equation_expression"
                stepInformationList.extend([equationInfo])

        case "rf":
            objectInfo= box["name"]
            objectInformationList = getObjectInformation(typeInfo = actionName, 
                                                         box = box)
            timeInfo = int(float(box["start_time"]))
            addedPhaseTypeInfo = box["rf_added_phase_type"]
            addedPhaseTypeInfo = "dummy_phase_type"
            addedPhaseFloatInfo = box["rf_added_phase_float"]
            addedPhaseFloatInfo = 0.0
            stepInformationList.extend([objectInfo, objectInformationList, \
                                        timeInfo, addedPhaseTypeInfo, \
                                        addedPhaseFloatInfo])
        
        case "adc":
            objectInfo = box["name"]
            objectInformationList = getObjectInformation(typeInfo = actionName, 
                                                         box = box)
            timeInfo = int(float(box["start_time"]))
            # TO DO add "frequency" to the dictionnary
            # frequencyInfo = box["frequency"]
            frequencyInfo = 0
            # TO DO add "phase" to the dictionnary
            # phaseInfo = box["phase"]
            phaseInfo = 0
            addedPhaseTypeInfo = box["adc_added_phase_type"]
            addedPhaseTypeInfo = "dummy_phase"
            addedPhaseFloatInfo = box["adc_added_phase_float"]
            addedPhaseFloatInfo = 0.0
            # TO DO add "header" to the dictionnary
            # mdhInfoList = box["header"]
            mdhInfoList = []
            #### TO DO !!! complete mdhInfoList
            ## WARNING: the above TO DO is true for all codes for now (02/07/24)
            print("passed for now") 
            ### end: not used for now
            stepInformationList.extend([objectInfo, objectInformationList, \
                                        timeInfo, frequencyInfo, phaseInfo,\
                                        addedPhaseTypeInfo,addedPhaseFloatInfo,\
                                        mdhInfoList])
            
        case "mark":
            # TO DO add "time" to the dictionnary
            # mdhInfoList = box["time"]
            timeInfo = 0.0
            stepInformationList.extend([timeInfo])

        case "submit":
            pass
        
        case _:
            print("The type " + actionName + " could not be identified.")
    return stepInformationList
            
def getObjectInformation(typeInfo, box):
    durationInfo = len(box["array_info"]["array"])*10
    objectInformationList = [typeInfo, durationInfo]
    match typeInfo:
        case "rf":
            # durationInfo = box["rf_duration"]
            arrayInfo = typeInfo + "_default_array"
            arrayInformationList = getArrayInformation(box = box)
            # TO DO add "init_phase" to the dictionnary
            # initPhaseInfo = box["init_phase"]
            initPhaseInfo = 0
            # TO DO add "thickness" to the dictionnary
            # thicknessInfo = box["thickness"]
            thicknessInfo = 0
            # TO DO add "flip_angle" to the dictionnary
            # flipAngleInfo = box["flip_angle"]
            flipAngleInfo = 0
            # TO DO add "purpose" to the dictionnary
            # purposeInfo = box["purpose"]
            purposeInfo = "dummy_purpose"
            objectInformationList.extend([arrayInfo, arrayInformationList, \
                                          initPhaseInfo, thicknessInfo, \
                                          flipAngleInfo, purposeInfo])
            
        case "grad":
            arrayName = typeInfo + "_default_array"
            arrayInformationList = getArrayInformation(box = box)
            # TO DO add "tail" to the dictionnary
            # tailInfo = box["tail"]
            tailInfo = 0
            amplitudeInfo = box['amplitude']
            objectInformationList.extend([arrayName, arrayInformationList, \
                                          tailInfo, amplitudeInfo])
            
        case "adc":
            # TO DO add "samples" to the dictionnary
            # samplesInfo = box["samples"]
            samplesInfo = 0
            # TO DO add "dwell_time" to the dictionnary
            # dwelltimeInfo = box["dwell_time"]
            dwelltimeInfo = 0
            objectInformationList.extend([samplesInfo, dwelltimeInfo])

        case "sync":
            # TO DO add "event" to the dictionnary
            # eventInfo = box["event"]
            eventInfo = "dummy_event"
            objectInformationList.extend([eventInfo])

        case _:
            print("The type " + typeInfo + " could not be identified.")

    return objectInformationList
            
def getArrayInformation(box):
    # TO DO add "encoding" to the dictionnary
    # encodingInfo = box["encoding"]
    encodingInfo = "text"
    # TO DO add "type" to the dictionnary
    # typeInfo = box["type"]
    typeInfo = "float"
    array = box["array_info"]["array"]
    sizeInfo = len(array)
    dataInfoList = array
    arrayInformationList = [encodingInfo, typeInfo, sizeInfo, dataInfoList]
    return arrayInformationList