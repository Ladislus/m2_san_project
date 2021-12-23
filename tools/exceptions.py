from enum import Enum, auto


class ClassDefItemNotFoundException(Exception):
    pass


class ExitCode(Enum):
    EXIT_SUCCESS = 0
    FILE_NOT_FOUND = auto()
    CLASS_NOT_FOUND = auto()
    MULTIPLE_CLASSES_FOUND = auto()
    NO_INPUT_FILE_GIVEN = auto()
