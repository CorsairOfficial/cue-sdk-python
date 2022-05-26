import ctypes
from .enums import (CorsairEventId, CorsairKeyId, CorsairLedId,
                    CorsairDeviceType, CorsairChannelDeviceType,
                    CorsairPhysicalLayout, CorsairLogicalLayout)
from .utils import bytes_to_str_or_default

__all__ = [
    'CorsairProtocolDetails', 'CorsairChannelDeviceInfo', 'CorsairChannelInfo',
    'CorsairChannelsInfo', 'CorsairDeviceInfo', 'CorsairLedPosition',
    'CorsairLedPositions', 'CorsairLedColor', 'CorsairEvent',
    'CorsairKeyEvent', 'CorsairDeviceConnectionStatusChangedEvent'
]

CORSAIR_DEVICE_ID_MAX = 128


class CorsairProtocolDetails(ctypes.Structure):
    _fields_ = [('sdkVersion', ctypes.c_char_p),
                ('serverVersion', ctypes.c_char_p),
                ('sdkProtocolVersion', ctypes.c_int32),
                ('serverProtocolVersion', ctypes.c_int32),
                ('breakingChanges', ctypes.c_bool)]

    def __str__(self):
        return ("\n".join([
            "SDK version: " + bytes_to_str_or_default(self.sdkVersion),
            "SDK protocol version: " + str(self.sdkProtocolVersion),
            "Server version: " + bytes_to_str_or_default(self.serverVersion),
            "Server protocol version: " + str(self.serverProtocolVersion),
            "Breaking changes: " + str(self.breakingChanges)
        ]))


class CorsairChannelDeviceInfo(ctypes.Structure):
    _fields_ = [('type', CorsairChannelDeviceType),
                ('deviceLedCount', ctypes.c_int32)]


class CorsairChannelInfo(ctypes.Structure):
    _fields_ = [('totalLedsCount', ctypes.c_int32),
                ('devicesCount', ctypes.c_int32),
                ('devices', ctypes.POINTER(CorsairChannelDeviceInfo))]


class CorsairChannelsInfo(ctypes.Structure):
    _fields_ = [('channelsCount', ctypes.c_int32),
                ('channels', ctypes.POINTER(CorsairChannelInfo))]


class CorsairDeviceInfo(ctypes.Structure):
    _fields_ = [('type', CorsairDeviceType), ('model', ctypes.c_char_p),
                ('physicalLayout', CorsairPhysicalLayout),
                ('logicalLayout', CorsairLogicalLayout),
                ('capsMask', ctypes.c_int32), ('ledsCount', ctypes.c_int32),
                ('channels', CorsairChannelsInfo),
                ('deviceId', ctypes.c_char * CORSAIR_DEVICE_ID_MAX)]


class CorsairLedPosition(ctypes.Structure):
    _fields_ = [('ledId', CorsairLedId), ('top', ctypes.c_double),
                ('left', ctypes.c_double), ('height', ctypes.c_double),
                ('width', ctypes.c_double)]


class CorsairLedPositions(ctypes.Structure):
    _fields_ = [('numberOfLed', ctypes.c_int32),
                ('pLedPosition', ctypes.POINTER(CorsairLedPosition))]


class CorsairLedColor(ctypes.Structure):
    _fields_ = [('ledId', CorsairLedId), ('r', ctypes.c_int32),
                ('g', ctypes.c_int32), ('b', ctypes.c_int32)]


class CorsairDeviceConnectionStatusChangedEvent(ctypes.Structure):
    _fields_ = [('deviceId', ctypes.c_char * CORSAIR_DEVICE_ID_MAX),
                ('isConnected', ctypes.c_bool)]


class CorsairKeyEvent(ctypes.Structure):
    _fields_ = [('deviceId', ctypes.c_char * CORSAIR_DEVICE_ID_MAX),
                ('keyId', CorsairKeyId), ('isPressed', ctypes.c_bool)]


class CorsairEventPayload(ctypes.Union):
    _fields_ = [('deviceConnectionStatusChangedEvent',
                 ctypes.POINTER(CorsairDeviceConnectionStatusChangedEvent)),
                ('keyEvent', ctypes.POINTER(CorsairKeyEvent))]


class CorsairEvent(ctypes.Structure):
    _anonymous_ = ("payload", )
    _fields_ = [('id', CorsairEventId), ('payload', CorsairEventPayload)]
