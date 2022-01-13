from androguard.core.analysis.analysis import Analysis
from androguard.core.bytecodes.dvm import Instruction

from tools import APKInfos, MethodInfos, exitError, ExitCode, MethodKeys

# Type alias for better lisibility
Analyse1MemoryType = list[None | str]
Analyse1StackType = list[str]

# TODO
Analyse2MemoryType = list[None | bool]
Analyse2StackType = list[str]

# Type union
AnalyseMemoryType = Analyse1MemoryType | Analyse2MemoryType
AnalyseStackType = Analyse1StackType | Analyse2StackType


PRIMITIVE_TYPES_STR: list[str] = ["V", "Z", "B", "S", "C", "I", "J", "F", "D"]


class Analyser:
    _mem: AnalyseMemoryType
    _stack: AnalyseStackType
    _apkInfos: APKInfos
    _methodInfos: MethodInfos
    _analysis: Analysis
    _verbose: bool

    def __init__(self, memory: AnalyseMemoryType, stack: AnalyseStackType, apkInfos: APKInfos, methodInfos: MethodInfos, analysis: Analysis, verbose: bool):
        self._mem = memory
        self._stack = stack
        self._apkInfos = apkInfos
        self._methodInfos = methodInfos
        self._analysis = analysis
        self._verbose = verbose

    def analyse(self, instruction: Instruction):
        exitError('Method `analyse()` from base class Analyser shoudn\'t be called', ExitCode.BASE_CLASS_CALL)

    def reportMethod(self):
        exitError('Method `reportMethod()` from base class Analyser shoudn\'t be called', ExitCode.BASE_CLASS_CALL)

    def _validRegisterNumber(self, _registerNumber: int) -> bool:
        """
        Method to check if a register number is valid.
        :param _registerNumber: The register number
        :return: Boolean
        """
        return _registerNumber < self._methodInfos[MethodKeys.LOCALREGISTERCOUNT] + self._methodInfos[MethodKeys.PARAMETERCOUNT]

    @staticmethod
    def _unhandled(_instruction: Instruction) -> None:
        """
        Method called when an instruction is not handled.
        :param _instruction: The instruction that isn't handled
        """
        exitError(f'Unhandled instruction type {type(_instruction)}', ExitCode.UNHANDLED_INSTRUCTION)

    def _useless(self, _instruction: Instruction) -> None:
        """
        Method called when an instruction shouldn't be analysed.
        :param _instruction: The instruction
        """
        if self._verbose:
            print(f'Instruction {_instruction.get_name()} (OP: {hex(_instruction.get_op_value())}) shouldn\'t be analysed')

    @staticmethod
    def _printInstruction(_instruction: Instruction) -> None:
        """
        Method to print an instruction.
        :param _instruction: The instruction to print
        """
        print(
            'Instruction: \n'
            f'\tName: {_instruction.get_name()}\n'
            f'\tOP: {hex(_instruction.get_op_value())}\n'
            f'\tOperands: {_instruction.get_operands()}\n'
            f'\tOutput: {_instruction.get_output()}\n'
            f'\tRaw: {_instruction.get_raw()}\n'
            f'\tSize: {_instruction.get_length()}\n'
            f'\tLiterals {_instruction.get_literals()}'
        )

    def _validLocalRegisterNumber(self, _registerNumber: int) -> bool:
        """
        Method to check if a register number is valid.
        :param _registerNumber: The register number
        :return: Boolean
        """
        return _registerNumber < self._methodInfos[MethodKeys.LOCALREGISTERCOUNT]

    @staticmethod
    def _findOperand(_instruction: Instruction, _index: int) -> str:
        return str(_instruction.get_output().split(', ')[_index])

    @staticmethod
    def _registerNameToIndex(_registerName: str) -> int:
        try:
            return int(_registerName[1:])
        except ValueError as e:
            exitError(f'Cannot convert {_registerName[1:]} to int ({e})', ExitCode.CAST_ERROR)

    @staticmethod
    def _returnTypeFromMethodString(string: str) -> str:
        return string.split(')')[-1]

    # ERRORS #

    @staticmethod
    def _Error_invalidRegisterNumber(_instruction: Instruction, _register: int):
        exitError(f'Instruction {_instruction} uses invalid register number {_register}', ExitCode.INVALID_REGISTER_NUMBER)
