from androguard.core.analysis.analysis import Analysis
from androguard.core.bytecodes.dvm import ClassDefItem, EncodedMethod

from .analyser import Analyser
from .analyse1 import Analyse1

from tools import APKInfos, extractInfosFromMethod, MethodInfos, exitError, ExitCode


def analyse(_classDefItem: ClassDefItem, _flag: int, _apkInfos: APKInfos, _analysis: Analysis, _inputFile: str | None, _verbose: bool):

    # Extract all the methods from the class
    methods: list[EncodedMethod] = _classDefItem.get_methods()

    for currentMethod in methods:
        # Load the method infos if not already loaded
        currentMethod.load()

        # Extract the method infos for the instruction analysis
        methodInfos: MethodInfos = extractInfosFromMethod(currentMethod)

        analyser: Analyser
        match _flag:
            case 1:
                analyser = Analyse1(_apkInfos, methodInfos, _analysis, _verbose)
            case 2:
                exitError(f'Analyse {_flag} not implemented in engine.analyse()', ExitCode.ANALYSE_NOT_IMPLEMENTED)
            case 3:
                exitError(f'Analyse {_flag} not implemented in engine.analyse()', ExitCode.ANALYSE_NOT_IMPLEMENTED)
            case _:
                exitError(f'Unknown flag {_flag} in engine.analyse()', ExitCode.UNHANDLED_CASE)

        if _verbose:
            currentMethod.show()

        for instruction in currentMethod.get_instructions():

            # Apply the analysis function for the current instruction
            analyser.analyse(instruction)

        analyser.reportMethod()
