from sys import stdout
from typing import Any
from androguard.core.bytecodes.apk import APK
from androguard.core.bytecodes.dvm import DalvikVMFormat, EncodedMethod
from enum import Enum, auto
from .exceptions import ExitCode, exitException
from .constants import *


class APKKeys(Enum):
    APK = auto()
    PATH = auto()
    NAME = auto()
    VERSION = auto()
    PERMISSIONS = auto()
    PERMISSIONSDETAILS = auto()
    DECLAREDPERMISSIONS = auto()
    DETAILEDDECLAREDPERMISSIONS = auto()
    ACTIVITIES = auto()
    DALVIKVMFORMAT = auto()


APKInfos: type = dict[APKKeys, Any]


def printAPKInfos(_infos: APKInfos):
    print(
        f'APK Infos:',
        f'\n\tName: {_infos[APKKeys.NAME]}',
        f'\n\tPath: {_infos[APKKeys.PATH]}',
        f'\n\tVersion: {_infos[APKKeys.VERSION]}',
        f'\n\tPermissions: {_infos[APKKeys.PERMISSIONS]}',
        f'\n\tDetailed Permissions: {_infos[APKKeys.PERMISSIONSDETAILS]}',
        f'\n\tDeclared Permissions: {_infos[APKKeys.DECLAREDPERMISSIONS]}',
        f'\n\tDetailed Declared Permissions: {_infos[APKKeys.DETAILEDDECLAREDPERMISSIONS]}',
        f'\n\tActivities: {_infos[APKKeys.ACTIVITIES]}',
        f'\n\tDalvikVMFormat: {_infos[APKKeys.DALVIKVMFORMAT]}'
    )


def extractInfosFromAPK(_APKPath: str) -> APKInfos:
    try:
        apk = APK(_APKPath)
        return {
            APKKeys.APK: apk,
            APKKeys.PATH: _APKPath,
            APKKeys.NAME: apk.get_app_name(),
            APKKeys.VERSION: apk.get_target_sdk_version(),
            APKKeys.PERMISSIONS: apk.get_permissions(),
            APKKeys.PERMISSIONSDETAILS: apk.get_details_permissions(),
            APKKeys.DECLAREDPERMISSIONS: apk.get_declared_permissions(),
            APKKeys.DETAILEDDECLAREDPERMISSIONS: apk.get_declared_permissions_details(),
            APKKeys.ACTIVITIES: apk.get_activities(),
            APKKeys.DALVIKVMFORMAT: [
                DalvikVMFormat(dex, using_api=apk.get_target_sdk_version()) for dex in apk.get_all_dex()
            ]
        }

    except FileNotFoundError as e:
        exitException(e, ExitCode.FILE_NOT_FOUND)


class MethodKeys(Enum):
    CLASSNAME = auto()
    NAME = auto()
    CONSTRUCTOR = auto()
    STATIC = auto()
    FINAL = auto()
    SYNCHRONIZED = auto()
    ACCESS = auto()
    LOCALREGISTERCOUNT = auto()
    LOCALREGISTER = auto()
    PARAMETERCOUNT = auto()
    PARAMS = auto()
    RETURNTYPE = auto()


MethodInfos: type = dict[MethodKeys, Any]


def printMethodInfos(_infos: MethodInfos):
    print(
        f'Method Infos:',
        f'\n\tClass: {_infos[MethodKeys.CLASSNAME]}',
        f'\n\tName: {_infos[MethodKeys.NAME]}',
        f'\n\tConstructor: {_infos[MethodKeys.CONSTRUCTOR]}',
        f'\n\tStatic: {_infos[MethodKeys.STATIC]}',
        f'\n\tFinal: {_infos[MethodKeys.FINAL]}',
        f'\n\tSynchronized: {_infos[MethodKeys.SYNCHRONIZED]}',
        f'\n\tAccess: {_infos[MethodKeys.ACCESS]}',
        f'\n\tLocal Register Count: {_infos[MethodKeys.LOCALREGISTERCOUNT]}',
        f'\n\tLocal Register: {_infos[MethodKeys.LOCALREGISTER]}',
        f'\n\tParameter Count: {_infos[MethodKeys.PARAMETERCOUNT]}',
        f'\n\tParameters: {_infos[MethodKeys.PARAMS]}',
        f'\n\tReturn Type: {_infos[MethodKeys.RETURNTYPE]}\n'
    )


def _humanParameterTypeToSmaliType(_type: (int, str)) -> (int, str):
    if _type[1] == HUMAN_VOID_TYPE:
        return _type[0], SMALI_VOID_TYPE
    elif _type[1] == HUMAN_BOOLEAN_TYPE:
        return _type[0], SMALI_BOOLEAN_TYPE
    elif _type[1] == HUMAN_BYTE_TYPE:
        return _type[0], SMALI_BYTE_TYPE
    elif _type[1] == HUMAN_CHAR_TYPE:
        return _type[0], SMALI_CHAR_TYPE
    elif _type[1] == HUMAN_SHORT_TYPE:
        return _type[0], SMALI_SHORT_TYPE
    elif _type[1] == HUMAN_INT_TYPE:
        return _type[0], SMALI_INT_TYPE
    elif _type[1] == HUMAN_LONG_TYPE:
        return _type[0], SMALI_LONG_TYPE
    elif _type[1] == HUMAN_FLOAT_TYPE:
        return _type[0], SMALI_FLOAT_TYPE
    elif _type[1] == HUMAN_DOUBLE_TYPE:
        return _type[0], SMALI_DOUBLE_TYPE
    else:
        return _type[0], 'L' + _type[1].replace('.', '/') + ';'


def humanTypeToSmaliType(_type: str) -> str:
    if _type == HUMAN_VOID_TYPE:
        return SMALI_VOID_TYPE
    elif _type == HUMAN_BOOLEAN_TYPE:
        return SMALI_BOOLEAN_TYPE
    elif _type == HUMAN_BYTE_TYPE:
        return SMALI_BYTE_TYPE
    elif _type == HUMAN_CHAR_TYPE:
        return SMALI_CHAR_TYPE
    elif _type == HUMAN_SHORT_TYPE:
        return SMALI_SHORT_TYPE
    elif _type == HUMAN_INT_TYPE:
        return SMALI_INT_TYPE
    elif _type == HUMAN_LONG_TYPE:
        return SMALI_LONG_TYPE
    elif _type == HUMAN_FLOAT_TYPE:
        return SMALI_FLOAT_TYPE
    elif _type == HUMAN_DOUBLE_TYPE:
        return SMALI_DOUBLE_TYPE
    else:
        return 'L' + _type.replace('.', '/') + ';'


def _humanParametersTypesToSmaliTypes(_types: list[(int, str)]) -> list[(int, str)]:
    return [_humanParameterTypeToSmaliType(currentType) for currentType in _types]


def extractInfosFromMethod(_method: EncodedMethod) -> MethodInfos:
    registerInformations = _method.get_information()

    accessFlags = _method.get_access_flags_string()
    acces = 'Private' if ACCESS_PRIVATE in accessFlags else 'Public' if ACCESS_PUBLIC in accessFlags else 'Protected' if ACCESS_PROTECTED in accessFlags else 'Package'

    return {
        MethodKeys.CLASSNAME: _method.get_class_name().removesuffix(';'),
        MethodKeys.NAME: _method.get_name(),
        MethodKeys.STATIC: ACCESS_STATIC in accessFlags,
        MethodKeys.CONSTRUCTOR: ACCESS_CONSTRUCTOR in accessFlags,
        MethodKeys.FINAL: ACCESS_FINAL in accessFlags,
        MethodKeys.SYNCHRONIZED: ACCESS_SYNCHRONIZED in accessFlags,
        MethodKeys.ACCESS: acces,
        MethodKeys.LOCALREGISTERCOUNT: _method.get_locals() + 1,
        MethodKeys.LOCALREGISTER: registerInformations['registers'],
        MethodKeys.PARAMETERCOUNT: len(registerInformations['params']) if 'params' in registerInformations.keys() else 0,
        MethodKeys.PARAMS: _humanParametersTypesToSmaliTypes(registerInformations['params']) if 'params' in registerInformations.keys() else [],
        MethodKeys.RETURNTYPE: humanTypeToSmaliType(registerInformations['return'])
    }
