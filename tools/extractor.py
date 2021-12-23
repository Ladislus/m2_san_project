from typing import Any
from androguard.core.bytecodes.apk import APK
from androguard.core.bytecodes.dvm import DalvikVMFormat
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


InfoDict = dict[APKKeys, Any]


def extract(_APKPath: str) -> InfoDict:
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
