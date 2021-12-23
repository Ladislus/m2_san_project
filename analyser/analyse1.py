from androguard.core.bytecodes.dvm import Instruction, Instruction12x, Instruction10x, Instruction35c, Instruction31i, \
    Instruction11x, Instruction22x, Instruction32x, Instruction10t, Instruction11n, Instruction20bc, Instruction20t, \
    Instruction21c, Instruction21h, Instruction21s, Instruction21t, Instruction22b, Instruction22c, Instruction22cs, \
    Instruction22s, Instruction22t, Instruction23x, Instruction30t, Instruction31c, Instruction31t, Instruction35mi, \
    Instruction35ms, Instruction3rc, Instruction3rmi, Instruction3rms, Instruction40sc, Instruction41c, Instruction51l, \
    Instruction52c, Instruction5rc
from tools import InfoDict, ExitCode
from tools.exceptions import exitError


def inst12x(_instruction: Instruction12x, _infos: InfoDict):
    print(f'Instruction 12x {_instruction.get_name()} (OP: {hex(_instruction.get_op_value())})')


def inst11x(_instruction: Instruction11x, _infos: InfoDict):
    print(f'Instruction 11x {_instruction.get_name()} (OP: {hex(_instruction.get_op_value())})')


def analyse1(_currentInstruction: Instruction, _infos: InfoDict, _verbose: bool, **kwargs):

    match _currentInstruction:
        case Instruction10t() as _inst10t:
            pass
        case Instruction10x() as _inst10x:
            pass
        case Instruction11n() as _inst11n:
            pass
        case Instruction11x() as _inst11x:
            inst11x(_inst11x, _infos)
        case Instruction12x() as _inst12x:
            inst12x(_inst12x, _infos)
        case Instruction20bc() as _inst20bc:
            pass
        case Instruction20t() as _inst20t:
            pass
        case Instruction21c() as _inst21c:
            pass
        case Instruction21h() as _inst21h:
            pass
        case Instruction21s() as _inst21s:
            pass
        case Instruction21t() as _inst21t:
            pass
        case Instruction22b() as _inst22b:
            pass
        case Instruction22c() as _inst22c:
            pass
        case Instruction22cs() as _inst22cs:
            pass
        case Instruction22s() as _inst22s:
            pass
        case Instruction22t() as _inst22t:
            pass
        case Instruction22x() as _inst22x:
            pass
        case Instruction23x() as _inst23x:
            pass
        case Instruction30t() as _inst30t:
            pass
        case Instruction31c() as _inst31c:
            pass
        case Instruction31i() as _inst31i:
            pass
        case Instruction31t() as _inst31t:
            pass
        case Instruction32x() as _inst32x:
            pass
        case Instruction35c() as _inst35c:
            pass
        case Instruction35mi() as _inst35mi:
            pass
        case Instruction35ms() as _inst35ms:
            pass
        case Instruction3rc() as _inst3rc:
            pass
        case Instruction3rmi() as _inst3rmi:
            pass
        case Instruction3rms() as _inst3rms:
            pass
        case Instruction40sc() as _inst40sc:
            pass
        case Instruction41c() as _inst41c:
            pass
        # FIXME Can't find import
        # case Instruction45cc() as _inst45cc:
        #     pass
        # case Instruction4rcc() as _inst4rcc:
        #     pass
        case Instruction51l() as _inst51l:
            pass
        case Instruction52c() as _inst52c:
            pass
        case Instruction5rc() as _inst5rc:
            pass
        case _:
            exitError(f'Unhandled instruction type {type(_currentInstruction)}', ExitCode.UNKNOWN_INSTRUCTION_TYPE)
