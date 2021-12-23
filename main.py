from androguard.core.bytecodes.dvm import ClassDefItem, DalvikVMFormat
from analyser.engine import analyse
from tools import parse, extract, APKKeys, ClassDefItemNotFoundException, ExitCode, InfoDict
from tools.exceptions import exitError, exitException


def findCorrespondingClass(_ClassName: str, _dalvikFormats: list[DalvikVMFormat]) -> list[ClassDefItem]:
    foundItems: list[ClassDefItem] = []
    for dalvikFormat in _dalvikFormats:
        for currentClass in dalvikFormat.get_classes():
            cleanedName: str = currentClass.get_name().split('/')[-1][:-1]
            if cleanedName == _ClassName:
                foundItems.append(currentClass)
    if len(foundItems) == 0:
        raise ClassDefItemNotFoundException(f'Class "{_ClassName}" not found')
    return foundItems


if __name__ == '__main__':
    pathToTheAPK, ClassNameToAnalyse, analyseTypeFlag, inputFile, verbose = parse()
    infosOfTheAPK: InfoDict = extract(pathToTheAPK)

    try:
        classDefItems: list[ClassDefItem] = findCorrespondingClass(ClassNameToAnalyse, infosOfTheAPK[APKKeys.DALVIKVMFORMAT])

        if len(classDefItems) > 1:
            print('Multiple classes found')
            for x in classDefItems:
                print(f'\t{x}')
            exit(ExitCode.MULTIPLE_CLASSES_FOUND)

        analyse(classDefItems[0], analyseTypeFlag, infosOfTheAPK, inputFile, _verbose=verbose)
    except ClassDefItemNotFoundException as e:
        exitException(e, ExitCode.CLASS_NOT_FOUND)
