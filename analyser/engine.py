from androguard.core.bytecodes.dvm import ClassDefItem, EncodedMethod

from tools import InfoDict, ExitCode


def analyse(
        _classDefItem: ClassDefItem,
        _flag: int,
        _infos: InfoDict,
        _inputFile: str | None):
    match _flag:
        case 1:
            analyze1(_classDefItem, verbose=True)
        case 2:
            pass
        case 3:
            if _inputFile is None:
                print(f'No input file provided for analysis 3')
                exit(ExitCode.NO_INPUT_FILE_GIVEN)
            analyse3(_infos, _inputFile)
        case _:
            raise ValueError('Invalid flag')


def analyze1(classDefItem: ClassDefItem, flag: bool = False, verbose: bool = False):
    methods: list[EncodedMethod] = classDefItem.get_methods()

    for currentMethod in methods:
        # Load the method infos if not already loaded
        currentMethod.load()

        localRegisterCount: int = currentMethod.get_locals()
        registerInformations = currentMethod.get_information()
        parameterCount: int = len(registerInformations['params']) if 'params' in registerInformations.keys() else 0
        returnType: str = registerInformations['return']

        if verbose:
            print(
                f'Method: {currentMethod.get_name()}\n'
                f'\tLocal register count: {localRegisterCount}\n'
                f'\tParameter count: {parameterCount}\n'
                f'\tReturn type: {returnType}\n'
            )

            for instructions in currentMethod.get_instructions():
                print(f'\tInstruction : {instructions}')
                print(f'\t\tName of instruction : {instructions.get_name()}')
                print(f'\t\tInt op value : {hex(instructions.get_op_value())}')
                print(f'\t\tHex : {instructions.get_hex()}')
            currentMethod.show()


def analyse2(classDefItem: ClassDefItem, flag: bool = False, verbose: bool = False):
    pass


def analyse3(infos: InfoDict, inputFile: str):
    pass