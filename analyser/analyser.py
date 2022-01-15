from androguard.core.analysis.analysis import Analysis
from androguard.core.bytecodes.dvm import Instruction, Instruction3rc, Instruction35c, ClassManager
from tools import APKInfos, MethodInfos, exitError, ExitCode, MethodKeys

# Type aliases for analysis
Analyse1MemoryType: type = list[None or str]
Analyse1StackType: type = list[str]
Analyse2MemoryType: type = list[None or bool]
Analyse2StackType: type = list[str]

# Type union
AnalyseMemoryType: type = Analyse1MemoryType or Analyse2MemoryType
AnalyseStackType: type = Analyse1StackType or Analyse2StackType

# Type aliases for utility methods
InvokeType: type = Instruction35c or Instruction3rc
MethodCallInfosType: type = tuple[str, str, list[str], str]


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

    # CHECKERS

    def _isValidRegisterNumber(self, _registerIndex: int) -> bool:
        """
        Method to check if a register number is valid.
        :param _registerIndex: The register number
        :return: Boolean
        """
        return _registerIndex < self._methodInfos[MethodKeys.LOCALREGISTERCOUNT] + self._methodInfos[MethodKeys.PARAMETERCOUNT]

    def _isValidLocalRegisterNumber(self, _registerIndex: int) -> bool:
        """
        Method to check if a register number is valid.
        :param _registerIndex: The register number
        :return: Boolean
        """
        return _registerIndex < self._methodInfos[MethodKeys.LOCALREGISTERCOUNT]

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

    # GETTERS

    def _getRegisterContent(self, _registerIndex: int) -> str | None:
        """
        Return the content of a register given it's index
        :param _registerIndex: The index of the register
        :return: A string representing the type of content, None if empty
        """
        if not self._isValidRegisterNumber(_registerIndex):
            exitError(f'Invalid register index {_registerIndex}', ExitCode.INVALID_REGISTER_INDEX)
        return self._mem[_registerIndex]

    # ANALYSIS

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

    # DEBUG

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

    # UTILS

    # TODO
    @staticmethod
    def _findOperand(_instruction: Instruction, _index: int) -> str:
        return str(_instruction.get_output().split(', ')[_index])

    @staticmethod
    def _getParametersTypeFromString(string: str) -> list[str]:
        """
        Decompose a method call into its parameters types.
        :param string: The string representing the parameters type
        :return: list[str] containing types
        """
        # Remove parenthesis
        parametersString = string[1:-1]
        # Split by ' '
        return parametersString.split(' ')

    def _decomposeInvoke(self, _instruction: InvokeType) -> MethodCallInfosType:
        """
        Method that decompose a call methode (ex: Lcom/example/ex2test/MainActivity;->findViewById(I)Landroid/view/View;)
        into 4 separated components: (Class, Method name, list of parameters type, return type)
        :param _instruction: The instruction to decompose
        :return: A tuple containing the 4 components (Class: str, Method name: str, parameters type: list[str], return type: str)
        """
        calledMethodInformations = _instruction.cm.get_method(_instruction.BBBB)
        return calledMethodInformations[0], calledMethodInformations[1], self._getParametersTypeFromString(calledMethodInformations[2][0]), calledMethodInformations[2][1]

    # ERRORS

    @staticmethod
    def _Error_invalidRegisterNumber(_instruction: Instruction, _register: int):
        exitError(f'Instruction {_instruction} uses invalid register number {_register}', ExitCode.INVALID_REGISTER_NUMBER)
