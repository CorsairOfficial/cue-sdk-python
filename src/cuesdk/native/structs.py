import ctypes

__all__ = [
    'CorsairVersion', 'CorsairSessionDetails', 'CorsairSessionStateChanged',
    'CorsairDeviceInfo', 'CorsairLedPosition', 'CorsairDeviceFilter',
    'CorsairDeviceConnectionStatusChangedEvent', 'CorsairKeyEvent',
    'CorsairEvent', 'CorsairDataType_BooleanArray',
    'CorsairDataType_Int32Array', 'CorsairDataType_Float64Array',
    'CorsairDataType_StringArray', 'CorsairDataValue', 'CorsairProperty',
    'CorsairLedColor', 'CorsairKeyEventConfiguration', 'CORSAIR_STRING_SIZE_S',
    'CORSAIR_STRING_SIZE_M', 'CORSAIR_LAYER_PRIORITY_MAX',
    'CORSAIR_DEVICE_COUNT_MAX', 'CORSAIR_DEVICE_LEDCOUNT_MAX'
]

CORSAIR_STRING_SIZE_S = 64
CORSAIR_STRING_SIZE_M = 128
CORSAIR_LAYER_PRIORITY_MAX = 255
CORSAIR_DEVICE_COUNT_MAX = 64
CORSAIR_DEVICE_LEDCOUNT_MAX = 512


class CorsairVersion(ctypes.Structure):
    _fields_ = [('major', ctypes.c_int32), ('minor', ctypes.c_int32),
                ('patch', ctypes.c_int32)]


class CorsairSessionDetails(ctypes.Structure):
    _fields_ = [('clientVersion', CorsairVersion),
                ('serverVersion', CorsairVersion),
                ('serverHostVersion', CorsairVersion)]


class CorsairSessionStateChanged(ctypes.Structure):
    _fields_ = [('state', ctypes.c_uint), ('details', CorsairSessionDetails)]


class CorsairDeviceInfo(ctypes.Structure):
    _fields_ = [('type', ctypes.c_uint),
                ('deviceId', ctypes.c_char * CORSAIR_STRING_SIZE_M),
                ('serial', ctypes.c_char * CORSAIR_STRING_SIZE_M),
                ('model', ctypes.c_char * CORSAIR_STRING_SIZE_M),
                ('ledCount', ctypes.c_int32), ('channelCount', ctypes.c_int32)]


class CorsairLedPosition(ctypes.Structure):
    _fields_ = [('id', ctypes.c_uint), ('cx', ctypes.c_double),
                ('cy', ctypes.c_double)]


class CorsairDeviceFilter(ctypes.Structure):
    _fields_ = [('deviceTypeMask', ctypes.c_int32)]


class CorsairDeviceConnectionStatusChangedEvent(ctypes.Structure):
    _fields_ = [('deviceId', ctypes.c_char * CORSAIR_STRING_SIZE_M),
                ('isConnected', ctypes.c_bool)]


class CorsairKeyEvent(ctypes.Structure):
    _fields_ = [('deviceId', ctypes.c_char * CORSAIR_STRING_SIZE_M),
                ('keyId', ctypes.c_uint), ('isPressed', ctypes.c_bool)]


class CorsairEventPayload(ctypes.Union):
    _fields_ = [('deviceConnectionStatusChangedEvent',
                 ctypes.POINTER(CorsairDeviceConnectionStatusChangedEvent)),
                ('keyEvent', ctypes.POINTER(CorsairKeyEvent))]


class CorsairEvent(ctypes.Structure):
    _anonymous_ = ("payload", )
    _fields_ = [('id', ctypes.c_uint), ('payload', CorsairEventPayload)]


class CorsairDataType_BooleanArray(ctypes.Structure):
    _fields_ = [('items', ctypes.POINTER(ctypes.c_bool)),
                ('count', ctypes.c_uint)]


class CorsairDataType_Int32Array(ctypes.Structure):
    _fields_ = [('items', ctypes.POINTER(ctypes.c_int32)),
                ('count', ctypes.c_uint)]


class CorsairDataType_Float64Array(ctypes.Structure):
    _fields_ = [('items', ctypes.POINTER(ctypes.c_double)),
                ('count', ctypes.c_uint)]


class CorsairDataType_StringArray(ctypes.Structure):
    _fields_ = [('items', ctypes.POINTER(ctypes.c_char_p)),
                ('count', ctypes.c_uint)]


class CorsairDataValue(ctypes.Union):
    _fields_ = [('boolean', ctypes.c_bool), ('int32', ctypes.c_int32),
                ('float64', ctypes.c_double), ('string', ctypes.c_char_p),
                ('boolean_array', CorsairDataType_BooleanArray),
                ('int32_array', CorsairDataType_Int32Array),
                ('float64_array', CorsairDataType_Float64Array),
                ('string_array', CorsairDataType_StringArray)]


class CorsairProperty(ctypes.Structure):
    _fields_ = [('type', ctypes.c_uint), ('value', CorsairDataValue)]


class CorsairLedColor(ctypes.Structure):
    _fields_ = [('id', ctypes.c_uint), ('r', ctypes.c_ubyte),
                ('g', ctypes.c_ubyte), ('b', ctypes.c_ubyte),
                ('a', ctypes.c_ubyte)]


class CorsairKeyEventConfiguration(ctypes.Structure):
    _fields_ = [('keyId', ctypes.c_uint), ('isIntercepted', ctypes.c_bool)]
