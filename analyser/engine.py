from androguard.core.bytecodes.dvm import ClassDefItem, EncodedMethod

from analyser.analyse1 import analyse1
from analyser.analyse2 import analyse2
from analyser.analyse3 import analyse3
from tools import APKInfos


def analyse(_classDefItem: ClassDefItem, _flag: int, _infos: APKInfos, _inputFile: str | None, _verbose: bool):
    func = analyse1 if _flag == 1 else analyse2 if _flag == 2 else analyse3

    methods: list[EncodedMethod] = _classDefItem.get_methods()

    for currentMethod in methods:
        # Initialise the memory of the current method's analysis (depends on the type of analysis)
        # mem = () if _flag == 1 else ...

        # Load the method infos if not already loaded
        currentMethod.load()

        localRegisterCount: int = currentMethod.get_locals()
        registerInformations = currentMethod.get_information()
        parameterCount: int = len(registerInformations['params']) if 'params' in registerInformations.keys() else 0
        returnType: str = registerInformations['return']

        if _verbose:
            print(
                f'Method: {currentMethod.get_name()}\n'
                f'\tLocal register count: {localRegisterCount}\n'
                f'\tParameter count: {parameterCount}\n'
                f'\tReturn type: {returnType}\n'
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
            func(instruction, _infos, _verbose)
