from enum import Enum, auto
from sys import stderr


class ClassDefItemNotFoundException(Exception):
    pass


class ExitCode(Enum):
    EXIT_SUCCESS = 0
    FILE_NOT_FOUND = auto()
    CLASS_NOT_FOUND = auto()
    MULTIPLE_CLASSES_FOUND = auto()
    NO_INPUT_FILE_GIVEN = auto()
    UNKNOWN_INSTRUCTION_TYPE = auto()


def exitError(_msg: str, _code: ExitCode):
    print(_msg, file=stderr)
    exit(_code)


def exitException(_ex: Exception, _code: ExitCode):
    print(_ex)
    exit(_code)
