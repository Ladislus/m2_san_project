from androguard.core.bytecodes.dvm import ClassDefItem, DalvikVMFormat

from analyser.engine import analyse
from tools import parse, extract, APKKeys, ClassDefItemNotFoundException, ExitCode, InfoDict


def findCorrespondingClass(ClassName: str, dalvikFormats: list[DalvikVMFormat]) -> list[ClassDefItem]:
    foundItems: list[ClassDefItem] = []
    for dalvikFormat in dalvikFormats:
        for currentClass in dalvikFormat.get_classes():
            cleanedName: str = currentClass.get_name().split('/')[-1][:-1]
            if cleanedName == ClassName:
                foundItems.append(currentClass)
    if len(foundItems) == 0:
        raise ClassDefItemNotFoundException(f'Class "{ClassName}" not found')
    return foundItems


if __name__ == '__main__':
    pathToTheAPK, ClassNameToAnalyse, analyseTypeFlag, inputFile = parse()
    infosOfTheAPK: InfoDict = extract(pathToTheAPK)

    try:
        classDefItems: list[ClassDefItem] = findCorrespondingClass(ClassNameToAnalyse, infosOfTheAPK[APKKeys.DALVIKVMFORMAT])

        if len(classDefItems) > 1:
            print('Multiple classes found')
            for x in classDefItems:
                print(f'\t{x}')
            exit(ExitCode.MULTIPLE_CLASSES_FOUND)

        analyse(classDefItems[0], analyseTypeFlag, infosOfTheAPK, inputFile)
    except ClassDefItemNotFoundException as e:
        print(e)
        exit(ExitCode.CLASS_NOT_FOUND)
