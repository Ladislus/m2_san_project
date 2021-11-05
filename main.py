#!/usr/bin/env python3.9

from tools import parse

from androguard.core.bytecodes.apk import APK
from androguard.core.bytecodes.dvm import DalvikVMFormat

from androguard.misc import AnalyzeAPK

if __name__ == '__main__':
    APKPath, ClassName, Flag = parse()

    _apk = APK(APKPath)
    print(f'APK : {_apk}')
    print(f'Application Name: {_apk.get_app_name()}')
    print(f'Permissions: {_apk.get_permissions()}')
    print(f'Requested Permissions: {_apk.get_requested_permissions()}')
    print(f'Declared Permissions: {_apk.get_declared_permissions()}')

    print('Activities')
    for idx, act in enumerate(_apk.get_activities()):
        print(f'\tActivity {idx}: {act}')
