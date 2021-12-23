from typing import Any
from androguard.core.bytecodes.apk import APK
from androguard.core.bytecodes.dvm import DalvikVMFormat, EncodedMethod
from .exceptions import ExitCode, exitException
from enum import Enum


class APKKeys(Enum):
    APK = 'APK'
    PATH = 'APKPath'
    NAME = 'APKName'
    VERSION = 'APKVersion'
    PERMISSIONS = 'APKPermissions'
    REQUESTEDPERMISSIONS = 'APKRequestedPersmissions'
    DECLAREDPERMISSIONS = 'APKDeclaredPermissions'
    DETAILEDDECLAREDPERMISSIONS = 'APKDetailedDeclaredPermissions'
    ACTIVITIES = 'APKActivities'
    DALVIKVMFORMAT = 'APKDalvikVMFormat'


APKInfos = dict[APKKeys, Any]


def extractInfosFromAPK(_APKPath: str) -> APKInfos:
    try:
        apk = APK(_APKPath)

        return {
            APKKeys.APK: apk,
            APKKeys.PATH: _APKPath,
            APKKeys.NAME: apk.get_app_name(),
            APKKeys.VERSION: apk.get_target_sdk_version(),
            APKKeys.PERMISSIONS: apk.get_permissions(),
            APKKeys.REQUESTEDPERMISSIONS: apk.get_requested_permissions(),
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
    NAME = 'MethodName'
    LOCALREGISTERCOUNT = 'MethodLocalRegisterCount'
    REGISTERINFORMATIONS = 'MethodRegisterInformations'
    PARAMETERCOUNT = 'MethodParameterCount'
    RETURNTYPE = 'MethodReturnType'


MethodInfos = dict[MethodKeys, Any]


def extractInfosFromMethod(_method: EncodedMethod) -> MethodInfos:
    registerInformations = _method.get_information()

    return {
        MethodKeys.NAME: _method.get_name(),
        MethodKeys.LOCALREGISTERCOUNT: _method.get_locals(),
        MethodKeys.REGISTERINFORMATIONS: registerInformations,
        MethodKeys.PARAMETERCOUNT: len(registerInformations['params']) if 'params' in registerInformations.keys() else 0,
        MethodKeys.RETURNTYPE: registerInformations['return']
    }
