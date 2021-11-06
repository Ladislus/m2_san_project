from typing import Any

from tools import parse, extract, APKKeys

if __name__ == '__main__':
    APKPath, ClassName, Flag = parse()
    infos: dict[APKKeys, Any] = extract(APKPath)

#    print(infos)
