from enum import Enum, auto

class ClassDefItemNotFoundException(Exception):
    pass

class ExitCode(Enum):
    EXIT_SUCCESS = 0
    CLASS_NOT_FOUND = auto()
    MULTIPLE_CLASSES_FOUND = auto()