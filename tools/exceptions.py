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
    UNHANDLED_INSTRUCTION = auto()
    INVALID_REGISTER_NUMBER = auto()
    UNHANDLED_CASE = auto()
    CHECKCAST_AGAINST_PRIMITIVE_OR_NONE = auto()
    CAST_ERROR = auto()
    ANALYSE_NOT_IMPLEMENTED = auto()
    BASE_CLASS_CALL = auto()
    INVALID_SUBCLASS = auto()
    ANALYSIS_NOT_FOUND = auto()
    MISCMATCH_PARAMETER_TYPE = auto()
    PARAMETER_COUNT_MISMATCH = auto()
    MISSING_INVOKE_KIND_OR_FILL_NEW_ARRAY = auto()
    MOVE_RESULT_ON_EMPTY_STACK = auto()
    UNREACHABLE = auto()
    RETURN_VOID_INSIDE_NON_VOID_METHOD = auto()
    INVALID_INSTRUCTION = auto()
    INVALID_REGISTER_INDEX = auto()


def exitError(_msg: str, _code: ExitCode):
    print(_msg, file=stderr)
    exit(_code)


def exitException(_ex: Exception, _code: ExitCode):
    print(_ex)
    exit(_code)
