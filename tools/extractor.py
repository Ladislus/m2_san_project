from __future__ import annotations

from androguard.core.bytecodes.apk import APK
from androguard.core.bytecodes.dvm import DalvikVMFormat


def extract(APKPath: str) -> dict[str, APK | list[DalvikVMFormat] | dict]:
    _apk = APK(APKPath)

    return {
        'APK': _apk,
        'Application Name': _apk.get_app_name(),
        'Permissions': _apk.get_permissions(),
        'Requested Permissions': _apk.get_requested_permissions(),
        'Declared Permissions': _apk.get_declared_permissions(),
        'Declared Permissions details': _apk.get_declared_permissions_details(),
        'Activities': _apk.get_activities(),
        'Dalviks': [ DalvikVMFormat(dex, using_api=_apk.get_target_sdk_version()) for dex in _apk.get_all_dex() ]
    }