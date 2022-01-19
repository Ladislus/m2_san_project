from androguard.core.analysis.analysis import Analysis
from androguard.core.bytecodes.dvm import Instruction, Instruction21c, Instruction35c
from tools import APKInfos, MethodInfos, SMALI_TARGETED_INTENT_CONSTRUCTOR, APKKeys, MethodKeys
from .analyser import Analyser


class Analyse3(Analyser):
    def __init__(self, apkInfos: APKInfos, methodInfos: MethodInfos, analysis: Analysis, verbose: bool):
        self._data: dict[int, str] = {}
        self._actions: list[str] = []
        super().__init__({}, {}, apkInfos, methodInfos, analysis, verbose)

    def _analyseConstString(self, _instruction: Instruction21c) -> None:
        self._data[_instruction.AA] = _instruction.cm.get_string(_instruction.BBBB)

    def _analyseInvokeDirect(self, _instruction: Instruction35c) -> None:
        _className, _methodName, _parametersTypesAndReturnType = _instruction.cm.get_method(_instruction.BBBB)
        _parametersTypes = _parametersTypesAndReturnType[0]
        _returnType = _parametersTypesAndReturnType[1]
        if f'{_className}->{_methodName}{_parametersTypes}{_returnType}' == SMALI_TARGETED_INTENT_CONSTRUCTOR:
            params = self._getVariadicProvidedParameters(_instruction)
            if len(params) != 2:
                return
            paramIndex: int = params[1]
            assert paramIndex in self._data.keys(), f'{paramIndex} not in {self._data.keys()}'
            self._actions.append(f'Method \'{self._methodInfos[MethodKeys.NAME]}\' uses Intent with action: \'{self._data[paramIndex]}\' (inside \'{self._methodInfos[MethodKeys.CLASSNAME]}\')')
        else:
            self._useless(_instruction)

    def collect(self):
        return self._actions

    def analyse(self, _instruction: Instruction, **kwargs) -> None:

        self._current = _instruction

        if self._verbose:
            self._printInstruction(_instruction)

        match _instruction:

            case Instruction21c() as _inst21c if _inst21c.get_name() == 'const-string':
                self._analyseConstString(_inst21c)

            case Instruction35c() as _inst35c if _inst35c.get_name() == 'invoke-direct':
                self._analyseInvokeDirect(_inst35c)

            case _other:
                self._useless(_other)