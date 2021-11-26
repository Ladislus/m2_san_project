from typing import Any
from androguard.core.bytecodes.apk import APK
from androguard.core.bytecodes.dvm import DalvikVMFormat
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


def extract(APKPath: str) -> InfoDict:
    _apk = APK(APKPath)

    return {
        APKKeys.APK: _apk,
        APKKeys.PATH: APKPath,
        APKKeys.NAME: _apk.get_app_name(),
        APKKeys.VERSION: _apk.get_target_sdk_version(),
        APKKeys.PERMISSIONS: _apk.get_permissions(),
        APKKeys.REQUESTEDPERMISSIONS: _apk.get_requested_permissions(),
        APKKeys.DECLAREDPERMISSIONS: _apk.get_declared_permissions(),
        APKKeys.DETAILEDDECLAREDPERMISSIONS: _apk.get_declared_permissions_details(),
        APKKeys.ACTIVITIES: _apk.get_activities(),
        APKKeys.DALVIKVMFORMAT: [
            DalvikVMFormat(dex, using_api=_apk.get_target_sdk_version()) for dex in _apk.get_all_dex()
        ]
    }
