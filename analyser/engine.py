from androguard.core.bytecodes.dvm import ClassDefItem, EncodedMethod

from analyser.analyse1 import analyse1
from analyser.analyse2 import analyse2
from analyser.analyse3 import analyse3
from tools import APKInfos, extractInfosFromMethod, MethodInfos, MethodKeys


def analyse(_classDefItem: ClassDefItem, _flag: int, _apkInfos: APKInfos, _inputFile: str | None, _verbose: bool):
    # Select the function corresponding to the desired analysis
    func = analyse1 if _flag == 1 else analyse2 if _flag == 2 else analyse3

    # Extract all the methods from the class
    methods: list[EncodedMethod] = _classDefItem.get_methods()

    for currentMethod in methods:
        # TODO Initialise the memory of the current method's analysis (depends on the type of analysis)
        # mem = () if _flag == 1 else ...

        # Load the method infos if not already loaded
        currentMethod.load()

        # Extract the method infos for the instruction analysis
        methodInfos: MethodInfos = extractInfosFromMethod(currentMethod)

        if _verbose:
            print(
                f'Method: { methodInfos[MethodKeys.NAME] }\n'
                f'\tLocal register count: { methodInfos[MethodKeys.LOCALREGISTERCOUNT] }\n'
                f'\tLocal register infos: { methodInfos[MethodKeys.REGISTERINFORMATIONS] }\n'
                f'\tParameter count: { methodInfos[MethodKeys.PARAMETERCOUNT] }\n'
                f'\tReturn type: { methodInfos[MethodKeys.RETURNTYPE] }\n'
            )

        for instruction in currentMethod.get_instructions():
            if _verbose:
                print(
                    f'\tInstruction : {instruction}\n'
                    f'\t\tName of instruction : {instruction.get_name()}\n'
                    f'\t\tInt op value : {hex(instruction.get_op_value())}\n'
                    f'\t\tHex : {instruction.get_hex()}\n'
                )
                currentMethod.show()
            func(instruction, _apkInfos, methodInfos, _verbose)
