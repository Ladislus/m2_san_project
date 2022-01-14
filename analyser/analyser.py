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
STRING_TYPE: str = 'Ljava/lang/String;'


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
        self._lastWasInvokeKindOrFillNewArray: bool = False

    def analyse(self, instruction: Instruction):
        exitError('Method `analyse()` from base class Analyser shoudn\'t be called', ExitCode.BASE_CLASS_CALL)

    def reportMethod(self):
        exitError('Method `reportMethod()` from base class Analyser shoudn\'t be called', ExitCode.BASE_CLASS_CALL)

    # FIXME
    def _isSubclass(self, _className: str, _superclassName: str) -> bool:
        """
        Method to find if a class is a subclass of another one
        :param _className: The subclass name
        :param _superclassName: The superclass name
        :return: boolean
        """

        # If the two parameters dosen't have the trailing ';', add it
        if not _className.endswith(';'):
            _className += ';'
        if not _superclassName.endswith(';'):
            _superclassName += ';'

        # If the superclass is Object, return True (all classes implement Object)
        if _superclassName == 'Ljava/lang/Object;':
            return True

        # If the _className is the same as the _superclassName, return true
        if _className == _superclassName:
            return True

        # Get the analysis of _className
        currentParentAnalysis = self._analysis.get_class_analysis(_className)
        # If we couldn't retrieve the analysis of the current class, error
        if currentParentAnalysis is None:
            exitError(f'Couldn\'t find class analysis for class {_className}', ExitCode.ANALYSIS_NOT_FOUND)
        # Retrieve the extended object
        currentParentClass = currentParentAnalysis.extends
        while currentParentClass is not None:
            # If the extended object is the _superclassName, return true$$
            if currentParentClass == _superclassName:
                return True
            # Else, propagate to the next parent
            currentParentAnalysis = self._analysis.get_class_analysis(currentParentClass)
            # If we couldn't retrieve the analysis of the current class, this means the parent class is Object
            if currentParentAnalysis is None:
                exitError(f'Couldn\'t find class analysis for parent class {currentParentClass}', ExitCode.ANALYSIS_NOT_FOUND)
            # Retrieve the extended object
            currentParentClass = currentParentAnalysis.extends
        # If we went through all parents without finding the correct name, return false (Can't be
        exitError(f'Shouldn\'t reached the end of the while in "_isSubclass({_className}, {_superclassName})', ExitCode.UNREACHABLE)

    def _registerContent(self, _registerName: str) -> str | bool:
        return self._mem[self._registerNameToIndex(_registerName)]

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
            f'\tSize: {_instruction.get_length()}'
        )

    def _printMemory(self):
        print(f'\tMemory:')
        [print(f'\t\tv{x}: {self._mem[x]}') for x in range(len(self._mem))]

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
    def _classFromMethodCall(string: str) -> str:
        return string.split('->')[0]

    @staticmethod
    def _methodFromMethodCall(string: str) -> str:
        return string.split('->')[1].split('(')[0]

    @staticmethod
    def _parametersTypeFromMethodCall(string: str) -> list[str]:
        """
        Decompose a method call into its parameters types.
        :param string: The method call string
        :return: list[str] containing types
        """
        # Initialise memory
        candidate: list[str] = []
        # Retrieve pameters into a list
        params = string.split('(')[1].split(')')[0]
        # Split by ';' (to separate objects)
        params = [p.strip() for p in params.split(';')]
        for param in params:

            # If it's an object, add it to the parameters types list
            if param.startswith('L'):
                candidate.append(param.strip() + ';')
            # Else
            else:
                # Decompose the parameters into single elements
                while len(param) > 0:
                    if param.startswith('L'):
                        candidate.append(param.strip() + ';')
                        break
                    else:
                        extracted = param[0]
                        candidate.append(extracted)
                        param = param[1:]
        # Return the parameters types list
        return candidate

    @staticmethod
    def _returnTypeFromMethodCall(string: str) -> str:
        return string.split(')')[1]

    def _decomposeMethodCall(self, string: str) -> (str, str, list[str], str):
        """
        Method that decompose a call methode (ex: Lcom/example/ex2test/MainActivity;->findViewById(I)Landroid/view/View;)
        into 4 separated components: (Class, Method name, list of parameters type, return type)
        :param string: The method call string
        :return: A tuple containing the 4 components (Class: str, Method name: str, parameters type: list[str], return type: str)
        """
        return self._classFromMethodCall(string), self._methodFromMethodCall(string), self._parametersTypeFromMethodCall(string), self._returnTypeFromMethodCall(string)

    # ERRORS #

    @staticmethod
    def _Error_invalidRegisterNumber(_instruction: Instruction, _register: int):
        exitError(f'Instruction {_instruction} uses invalid register number {_register}', ExitCode.INVALID_REGISTER_NUMBER)
