from androguard.core.analysis.analysis import Analysis
from androguard.core.bytecodes.dvm import ClassDefItem, EncodedMethod, Instruction21t, Instruction22t, Instruction30t, \
    Instruction20t, Instruction10t, Instruction, Instruction10x, Instruction11x
from tools import APKInfos, extractInfosFromMethod, MethodInfos, exitError, ExitCode, getOffsetFromGoto, getOffsetFromIf
from .analyse1 import Analyse1

# Type aliases
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
    # Extract all the methods from the class
    methods: list[EncodedMethod] = _classDefItem.get_methods()

    for currentMethod in methods:
        # Load the method infos if not already loaded
        currentMethod.load()

        # Extract the method infos for the instruction analysis
        methodInfos: MethodInfos = extractInfosFromMethod(currentMethod)

        match _flag:
            case 1:
                analyser: Analyse1 = Analyse1(_apkInfos, methodInfos, _analysis, _verbose)
                if _verbose:
                    currentMethod.show()
                stack, flow = _buildFlowFromMethod(currentMethod)

                while len(stack) != 0:
                    currentInstruction: Instruction = stack.pop(0)
                    analyser.analyse(currentInstruction)
                    stack.extend(flow[currentInstruction])

                # analyser.reportMethod()
            case 2:
                exitError(f'Analyse {_flag} not implemented in engine.analyse()', ExitCode.ANALYSE_NOT_IMPLEMENTED)
            case 3:
                exitError(f'Analyse {_flag} not implemented in engine.analyse()', ExitCode.ANALYSE_NOT_IMPLEMENTED)
            case _:
                exitError(f'Unknown flag {_flag} in engine.analyse()', ExitCode.UNHANDLED_CASE)
