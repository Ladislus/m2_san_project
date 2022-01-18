from androguard.core.analysis.analysis import Analysis, ClassAnalysis
from androguard.core.bytecodes.dvm import Instruction, Instruction3rc, Instruction35c
from tools import APKInfos, MethodInfos, exitError, ExitCode, MethodKeys, SMALI_OBJECT_TYPE, SMALI_BOOLEAN_TYPE, \
    SMALI_INT_TYPE, SMALI_ARRAY_MARKER, Colors, SMALI_OBJECT_MARKER

# Type aliases for analysis
Analyse1MemoryContentType: type = str or None
Analyse1SubmemoryType: type = list[Analyse1MemoryContentType]
Analyse1MemoryType: type = dict[Instruction, Analyse1SubmemoryType]
Analyse1StackContentType: type = str
Analyse1SubstackType: type = list[Analyse1StackContentType]
Analyse1StackType: type = dict[Instruction, Analyse1SubstackType]


Analyse2MemoryContentType: type = tuple[str or None, bool]
Analyse2SubmemoryType: type = list[Analyse2MemoryContentType]
Analyse2MemoryType: type = dict[Instruction, Analyse2SubmemoryType]
Analyse2StackContentType: type = str
Analyse2SubstackType: type = list[Analyse2StackContentType]
Analyse2StackType: type = dict[Instruction, Analyse2SubstackType]

# Type union
AnalyseMemoryContentType: type = Analyse1MemoryContentType or Analyse2MemoryContentType
AnalyseStackContentType: type = Analyse1StackContentType or Analyse2StackContentType
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
        self._current: Instruction or None = None

    def analyse(self, instruction: Instruction, **kwargs) -> bool:
        exitError('Method `analyse()` from base class Analyser shoudn\'t be called', ExitCode.BASE_CLASS_CALL)
        # Placeholder return to please the linter
        return True

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

    @staticmethod
    def _isArray(_type: str) -> bool:
        return _type.startswith(SMALI_ARRAY_MARKER)

    @staticmethod
    def _isValidPrimitiveType(_first: str, _second: str) -> bool:
        # Special case for boolean, because int can be interpreted as booleans
        if _first == SMALI_BOOLEAN_TYPE:
            return _second in (SMALI_BOOLEAN_TYPE, SMALI_INT_TYPE)
        elif _second == SMALI_BOOLEAN_TYPE:
            return _first in (SMALI_BOOLEAN_TYPE, SMALI_INT_TYPE)
        else:
            return _first == _second

    def _isSubclass(self, _className: str, _superclassName: str) -> bool:
        """
        Method to find if a class is a subclass of another one
        :param _className: The subclass name
        :param _superclassName: The superclass name
        :return: boolean
        """

        # If the superclass is Object, return True (all classes implement Object)
        if _superclassName == SMALI_OBJECT_TYPE:
            return True
        elif _className == SMALI_OBJECT_TYPE:
            return False

        # If the _className is the same as the _superclassName, return true
        if _className == _superclassName:
            return True

        # TODO Comment
        todo: set[str] = set()
        todo.add(_className)
        done: set[str] = set()
        while len(todo) > 0:
            curr = todo.pop()
            if curr not in done and curr != SMALI_OBJECT_TYPE:
                _a: ClassAnalysis = self._analysis.get_class_analysis(curr)
                done.add(curr)
                if _a is not None:
                    todo.add(_a.extends)
                    [todo.add(x) for x in _a.implements]
                else:
                    # TODO Better analysis
                    print(f'{Colors.WARNING}Couldn\'t find analysis for \'{curr}\', defaulting return to True{Colors.ENDC}')
                    return True
        return _superclassName in done

    # GETTERS

    def _putRegisterContent(self, _registerIndex: int, _value: AnalyseMemoryContentType) -> None:
        exitError('Method `_putRegisterContent()` from base class Analyser shoudn\'t be called', ExitCode.BASE_CLASS_CALL)

    def _getRegisterContent(self, _registerIndex: int) -> Analyse1MemoryContentType:
        exitError('Method `_getRegisterContent()` from base class Analyser shoudn\'t be called', ExitCode.BASE_CLASS_CALL)
        # Placeholder return to please linter
        return ''

    def _putStack(self, _value: AnalyseStackContentType) -> None:
        exitError('Method `_putStack()` from base class Analyser shoudn\'t be called', ExitCode.BASE_CLASS_CALL)

    def _popStack(self) -> AnalyseStackContentType:
        exitError('Method `_popStack()` from base class Analyser shoudn\'t be called', ExitCode.BASE_CLASS_CALL)
        # Placeholder return to please linter
        return ''

    # ANALYSIS

    @staticmethod
    def _unhandled(_instruction: Instruction) -> None:
        """
        Method called when an instruction is not handled
        :param _instruction: The instruction that isn't handled
        """
        exitError(f'Unhandled instruction type \'{type(_instruction).__name__}\'', ExitCode.UNHANDLED_INSTRUCTION)

    def _useless(self, _instruction: Instruction) -> None:
        """
        Method called when an instruction shouldn't be analysed
        :param _instruction: The instruction
        """
        if self._verbose:
            print(f'Instruction \'{_instruction.get_name()}\' (OP: {hex(_instruction.get_op_value())}) shouldn\'t be analysed')

    # DEBUG

    @staticmethod
    def _printInstruction(_instruction: Instruction) -> None:
        """
        Method to print an instruction.
        :param _instruction: The instruction to print
        """
        print(
            'Instruction: \n'
            f'\tName: \'{_instruction.get_name()}\'\n'
            f'\tOP: \'{hex(_instruction.get_op_value())}\'\n'
            f'\tOutput: \'{_instruction.get_output()}\'\n'
            f'\tSize: \'{_instruction.get_length()}\''
        )

    def _printMemory(self):
        exitError('Method `_printMemory()` from base class Analyser shoudn\'t be called', ExitCode.BASE_CLASS_CALL)

    # UTILS

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
        return [parameter.strip() for parameter in parametersString.split(' ') if parameter]

    def _decomposeInvokedMethod(self, _instruction: InvokeType) -> MethodCallInfosType:
        """
        Method that decompose a call methode (ex: Lcom/example/ex2test/MainActivity;->findViewById(I)Landroid/view/View;)
        into 4 separated components: (Class, Method name, list of parameters type, return type)
        :param _instruction: The instruction to decompose
        :return: A tuple containing the 4 components (Class: str, Method name: str, parameters type: list[str], return type: str)
        """
        calledMethodInformations = _instruction.cm.get_method(_instruction.BBBB)
        return calledMethodInformations[0], calledMethodInformations[1], self._getParametersTypeFromString(calledMethodInformations[2][0]), calledMethodInformations[2][1]

    @staticmethod
    def _getVariadicProvidedParameters(_instruction: InvokeType) -> list[int]:
        candidate: list[int] = []
        # _instruction.A contains the parameter count
        argumentsLength: int = _instruction.A

        # If the count allow it, add the given parameter
        if argumentsLength >= 1:
            candidate.append(_instruction.C)
        if argumentsLength >= 2:
            candidate.append(_instruction.D)
        if argumentsLength >= 3:
            candidate.append(_instruction.E)
        if argumentsLength >= 4:
            candidate.append(_instruction.F)
        if argumentsLength >= 5:
            candidate.append(_instruction.G)

        return candidate

    # TODO Comment
    @staticmethod
    def _decomposeArrays(_first: str, _second: str) -> ((int, str), (int, str)):
        _firstCounter = 0
        while _first.startswith(SMALI_ARRAY_MARKER):
            _first = _first[1:]
            _firstCounter += 1
        _secondCounter = 0
        while _second.startswith(SMALI_ARRAY_MARKER):
            _second = _second[1:]
            _secondCounter += 1
        return (_firstCounter, _first), (_secondCounter, _second)

    def _findClosestParent(self, _first: str, _seccond: str) -> str:
        if _first is SMALI_OBJECT_TYPE or _seccond is SMALI_OBJECT_TYPE:
            return SMALI_OBJECT_TYPE

        if _first == _seccond:
            return _first

        todoFirst: set[str] = set()
        todoFirst.add(_first)
        todoSecond: list[str] = [_seccond]
        doneFirst: set[str] = set()
        while len(todoFirst) > 0:
            curr = todoFirst.pop()
            if curr not in doneFirst and curr != SMALI_OBJECT_TYPE:
                _a: ClassAnalysis = self._analysis.get_class_analysis(curr)
                doneFirst.add(curr)
                if _a is not None:
                    todoFirst.add(_a.extends)
                    [todoFirst.add(x) for x in _a.implements]
        while len(todoSecond) > 0:
            curr = todoSecond.pop(0)
            if curr in doneFirst:
                return curr
            _a: ClassAnalysis = self._analysis.get_class_analysis(curr)
            if _a is not None:
                todoSecond.append(_a.extends)
                todoSecond.extend(_a.implements)

        return SMALI_OBJECT_TYPE

    def _compatibleType(self, _first: str, _second: str) -> str:
        if _first.startswith(SMALI_ARRAY_MARKER) or _second.startswith(SMALI_ARRAY_MARKER):
            (_firstCount, _firstValue), (_secondCounter, _secondValue) = self._decomposeArrays(_first, _second)
            if _firstCount != _secondCounter:
                exitError(f'Array dimensions differs ({_firstCount} != {_secondCounter})', ExitCode.MEMORY_ERROR)

        if _second.startswith(SMALI_OBJECT_MARKER):
            if not _first.startswith(SMALI_OBJECT_MARKER):
                exitError(f'Memory type mismatch between \'{_second}\' and \'{_first}\'', ExitCode.MEMORY_ERROR)
            # Check if the provided object is a subtype of the parameter
            return self._findClosestParent(_first, _second)
        # Else check if the primitive types match
        if not self._isValidPrimitiveType(_first, _second):
            exitError(f'Memory type mismatch between \'{_second}\' and \'{_first}\'', ExitCode.MEMORY_ERROR)
        return _first

    def _validateParameterType(self, _firstIndex: int, _firstValue: str, _secondValue: str) -> None:
        if _firstValue.startswith(SMALI_ARRAY_MARKER) or _secondValue.startswith(SMALI_ARRAY_MARKER):
            (_firstCount, _firstValue), (_secondCounter, _secondValue) = self._decomposeArrays(_firstValue, _secondValue)
            if _firstCount != _secondCounter:
                exitError(f'Array dimensions differs ({_firstCount} != {_secondCounter})', ExitCode.MISCMATCH_PARAMETER_TYPE)

        if _secondValue.startswith(SMALI_OBJECT_MARKER):
            if not _firstValue.startswith(SMALI_OBJECT_MARKER):
                exitError(f'Parameter expect type \'{_secondValue}\', but primitive type \'{_firstValue}\' given', ExitCode.MISCMATCH_PARAMETER_TYPE)
            # Check if the provided object is a subtype of the parameter
            if not self._isSubclass(_firstValue, _secondValue):
                exitError(f'Parameter \'v{_firstIndex}\' has type \'{_firstValue}\' which is not a subtype of \'{_secondValue}\'', ExitCode.MISCMATCH_PARAMETER_TYPE)
        # Else check if the primitive types match
        elif not self._isValidPrimitiveType(_firstValue, _secondValue):
            exitError(f'Parameter \'v{_firstIndex}\' has type \'{_firstValue}\'instead of \'{_secondValue}\'', ExitCode.MISCMATCH_PARAMETER_TYPE)

    # ERRORS

    @staticmethod
    def _Error_invalidRegisterNumber(_instruction: Instruction, _register: int):
        exitError(f'Instruction \'{_instruction.get_name()}\' uses invalid register number \'{_register}\'', ExitCode.INVALID_REGISTER_INDEX)
