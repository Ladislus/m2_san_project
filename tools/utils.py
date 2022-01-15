from androguard.core.bytecodes.dvm import Instruction30t, Instruction20t, Instruction10t, Instruction22t, Instruction21t
from .exceptions import ExitCode, exitError

# Type aliases
GotoType: type = Instruction10t or Instruction20t or Instruction30t
IfType: type = Instruction21t or Instruction22t


def getOffsetFromGoto(_instruction: GotoType) -> int:
    match _instruction:
        case Instruction10t() as _currentInstruction:
            return _currentInstruction.AA
        case Instruction20t() as _currentInstruction:
            return _currentInstruction.AAAA
        case Instruction30t() as _currentInstruction:
            return _currentInstruction.AAAAAAAA
        case err:
            exitError(f'Unknown instruction type: {err}', ExitCode.UNKNOWN_INSTRUCTION_TYPE)


def getOffsetFromIf(_instruction: IfType) -> int:
    match _instruction:
        case Instruction21t() as _currentInstruction:
            return _currentInstruction.BBBB
        case Instruction22t() as _currentInstruction:
            return _currentInstruction.CCCC
        case err:
            exitError(f'Unknown instruction type: {err}', ExitCode.UNKNOWN_INSTRUCTION_TYPE)



