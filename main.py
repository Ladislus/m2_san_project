from tools import parse, extract

if __name__ == '__main__':
    APKPath, ClassName, Flag = parse()
    infos: dict = extract(APKPath)

    print(infos)
