from androguard.core.analysis.analysis import Analysis
from androguard.core.bytecodes.dvm import ClassDefItem, EncodedMethod, Instruction21t, Instruction22t, Instruction30t, \
    Instruction20t, Instruction10t, Instruction, Instruction10x, Instruction11x
from analyser.analyse1 import Analyse1
from analyser.analyse2 import Analyse2
from analyser.analyse3 import Analyse3
from tools import APKInfos, extractInfosFromMethod, MethodInfos, exitError, ExitCode, getOffsetFromGoto, \
    getOffsetFromIf, printAPKInfos, APKKeys

FlowType: type = dict[Instruction, list[Instruction]]
StackType: type = list[Instruction]


def _buildFlowFromMethod(_method: EncodedMethod) -> (StackType, FlowType):
    candidate: FlowType = {}
    offset: int = 0
    stack: StackType = []
    for inst in _method.get_instructions():
        match inst:
            # Case 'GOTO'
            case Instruction10t() | Instruction20t() | Instruction30t() as _currentInstruction:
                # Add the instruction of the method
                if len(stack) == 0:
                    stack.append(_currentInstruction)
                nextInstructionOffset: int = offset + (getOffsetFromGoto(_currentInstruction) * 2)
                successorGoto: Instruction = _method.get_instruction(0, off=nextInstructionOffset)
                candidate[_currentInstruction] = [successorGoto]
            # Case 'IF'
            case Instruction21t() | Instruction22t() as _currentInstruction:
                # Add the instruction of the method
                if len(stack) == 0:
                    stack.append(_currentInstruction)
                nextInstructionOffset: int = offset + _currentInstruction.get_length()
                successorFallthrough: Instruction = _method.get_instruction(0, off=nextInstructionOffset)
                ifInstructionOffset: int = offset + (getOffsetFromIf(_currentInstruction) * 2)
                successorIf: Instruction = _method.get_instruction(0, off=ifInstructionOffset)
                candidate[_currentInstruction] = [successorFallthrough, successorIf]
            # Case 'RETURN-VOID'
            case Instruction10x() as _currentInstruction if _currentInstruction.get_op_value() == 0xe:
                # Add the instruction of the method
                if len(stack) == 0:
                    stack.append(inst)
                candidate[_currentInstruction] = []
            # CASE 'RETURN-kind' or 'THROW'
            case Instruction11x() as _currentInstruction if _currentInstruction.get_op_value() in [0xf, 0x10, 0x11, 0x27]:
                # Add the instruction of the method
                if len(stack) == 0:
                    stack.append(_currentInstruction)
                candidate[_currentInstruction] = []
            # Else
            case _ as _currentInstruction:
                # Add the instruction of the method
                if len(stack) == 0:
                    stack.append(_currentInstruction)
                nextInstructionOffset: int = offset + _currentInstruction.get_length()
                successor: Instruction = _method.get_instruction(0, off=nextInstructionOffset)
                candidate[_currentInstruction] = [successor]
        offset += inst.get_length()

    return stack, candidate


def analyse(_classDefItem: ClassDefItem, _flag: int, _apkInfos: APKInfos, _analysis: Analysis, _inputFile: str | None, _verbose: bool):
        match _flag:
            case 1:
                # Extract all the methods from the class
                methods: list[EncodedMethod] = _classDefItem.get_methods()
                for currentMethod in methods:
                    # Load the method infos if not already loaded
                    currentMethod.load()

                    # Extract the method infos for the instruction analysis
                    methodInfos: MethodInfos = extractInfosFromMethod(currentMethod)
                    analyser: Analyse1 = Analyse1(_apkInfos, methodInfos, _analysis, _verbose)
                    if _verbose:
                        currentMethod.show()
                    stack, flow = _buildFlowFromMethod(currentMethod)

                    while len(stack) != 0:
                        currentInstruction: Instruction = stack.pop(0)
                        predecessors: list[Instruction] = [key for key, values in flow.items() if currentInstruction in values]
                        if analyser.analyse(currentInstruction, predecessors=predecessors):
                            stack.extend(flow[currentInstruction])

                    # analyser.reportMethod()
            case 2:
                # Extract all the methods from the class
                methods: list[EncodedMethod] = _classDefItem.get_methods()
                for currentMethod in methods:
                    # Load the method infos if not already loaded
                    currentMethod.load()

                    # Extract the method infos for the instruction analysis
                    methodInfos: MethodInfos = extractInfosFromMethod(currentMethod)
                    analyser: Analyse2 = Analyse2(_apkInfos, methodInfos, _analysis, _verbose)
                    if _verbose:
                        currentMethod.show()
                    stack, flow = _buildFlowFromMethod(currentMethod)

                    while len(stack) != 0:
                        currentInstruction: Instruction = stack.pop(0)
                        predecessors: list[Instruction] = [key for key, values in flow.items() if currentInstruction in values]
                        if analyser.analyse(currentInstruction, predecessors=predecessors):
                            stack.extend(flow[currentInstruction])
            case 3:
                # Extract all the methods from the class
                methods: list[EncodedMethod] = _classDefItem.get_methods()
                _collectedIntents: list[str] = []
                for currentMethod in methods:
                    # Load the method infos if not already loaded
                    currentMethod.load()

                    # Extract the method infos for the instruction analysis
                    methodInfos: MethodInfos = extractInfosFromMethod(currentMethod)
                    analyser: Analyse3 = Analyse3(_apkInfos, methodInfos, _analysis, _verbose)
                    if _verbose:
                        currentMethod.show()

                    for instruction in currentMethod.get_instructions():
                        analyser.analyse(instruction)
                    _collectedIntents.extend(analyser.collect())
                printAPKInfos(_apkInfos)
                print('Intents:')
                [print(f'\t{intent}') for intent in _collectedIntents]
            case _:
                exitError(f'Unknown flag {_flag} in engine.analyse()', ExitCode.UNHANDLED_CASE)
