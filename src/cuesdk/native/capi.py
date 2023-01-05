import sys
from ctypes import (CDLL, CFUNCTYPE, POINTER, c_bool, c_char, c_int32,
                    c_uint32, c_void_p)

from . import (CORSAIR_STRING_SIZE_M, CorsairDeviceFilter,
               CorsairKeyEventConfiguration, CorsairLedPosition,
               CorsairProperty, CorsairSessionStateChanged,
               CorsairSessionDetails, CorsairDeviceInfo, CorsairLedColor,
               CorsairEvent)

__all__ = [
    'CorsairNativeApi', 'CorsairSessionStateChangedHandler',
    'CorsairEventHandler', 'CorsairAsyncCallback'
]


def load_library(library_path):
    try:
        return CDLL(library_path)
    except OSError:
        print("Unable to load the library %s" % library_path)
        sys.exit()


CorsairDeviceId = c_char * CORSAIR_STRING_SIZE_M
CorsairLedLuid = c_uint32
CorsairError = c_uint32
CorsairLedId = c_uint32
CorsairAccessMode = c_uint32
CorsairDevicePropertyId = c_uint32
CorsairDataType = c_uint32

c_bool_p = POINTER(c_bool)
c_int32_p = POINTER(c_int32)
c_uint32_p = POINTER(c_uint32)

CorsairSessionStateChangedHandler = CFUNCTYPE(
    None, c_void_p, POINTER(CorsairSessionStateChanged))
CorsairAsyncCallback = CFUNCTYPE(None, c_void_p, CorsairError)
CorsairEventHandler = CFUNCTYPE(None, c_void_p, POINTER(CorsairEvent))


class CorsairNativeApi():

    def __init__(self, libpath):
        lib = load_library(libpath)

        def create_func(fn, restype, argtypes):
            f = lib.__getattr__(fn)
            f.restype = restype
            f.argtypes = argtypes
            return f

        self.CorsairConnect = create_func(
            'CorsairConnect', CorsairError,
            [CorsairSessionStateChangedHandler, c_void_p])

        self.CorsairGetSessionDetails = create_func(
            'CorsairGetSessionDetails', CorsairError,
            [POINTER(CorsairSessionDetails)])

        self.CorsairDisconnect = create_func('CorsairDisconnect', CorsairError,
                                             None)

        self.CorsairGetDevices = create_func(
            'CorsairGetDevices', CorsairError, [
                POINTER(CorsairDeviceFilter), c_int32,
                POINTER(CorsairDeviceInfo), c_int32_p
            ])

        self.CorsairGetDeviceInfo = create_func(
            'CorsairGetDeviceInfo', CorsairError,
            [CorsairDeviceId, POINTER(CorsairDeviceInfo)])

        self.CorsairGetLedPositions = create_func(
            'CorsairGetLedPositions', CorsairError,
            [CorsairDeviceId, c_int32,
             POINTER(CorsairLedPosition), c_int32_p])

        self.CorsairSubscribeForEvents = create_func(
            'CorsairSubscribeForEvents', CorsairError,
            [CorsairEventHandler, c_void_p])

        self.CorsairUnsubscribeFromEvents = create_func(
            'CorsairUnsubscribeFromEvents', CorsairError, None)

        self.CorsairConfigureKeyEvent = create_func(
            'CorsairConfigureKeyEvent', CorsairError,
            [CorsairDeviceId,
             POINTER(CorsairKeyEventConfiguration)])

        self.CorsairGetDevicePropertyInfo = create_func(
            'CorsairGetDevicePropertyInfo', CorsairError, [
                CorsairDeviceId, CorsairDevicePropertyId, c_uint32,
                POINTER(CorsairDataType), c_uint32_p
            ])

        self.CorsairReadDeviceProperty = create_func(
            'CorsairReadDeviceProperty', CorsairError, [
                CorsairDeviceId, CorsairDevicePropertyId, c_uint32,
                POINTER(CorsairProperty)
            ])

        self.CorsairWriteDeviceProperty = create_func(
            'CorsairWriteDeviceProperty', CorsairError, [
                CorsairDeviceId, CorsairDevicePropertyId, c_uint32,
                POINTER(CorsairProperty)
            ])

        self.CorsairFreeProperty = create_func('CorsairFreeProperty',
                                               CorsairError,
                                               [POINTER(CorsairProperty)])

        self.CorsairSetLedColors = create_func(
            'CorsairSetLedColors', CorsairError,
            [CorsairDeviceId, c_int32,
             POINTER(CorsairLedColor)])

        self.CorsairSetLedColorsBuffer = create_func(
            'CorsairSetLedColorsBuffer', CorsairError,
            [CorsairDeviceId, c_int32,
             POINTER(CorsairLedColor)])

        self.CorsairSetLedColorsFlushBufferAsync = create_func(
            'CorsairSetLedColorsFlushBufferAsync', CorsairError,
            [CorsairAsyncCallback, c_void_p])

        self.CorsairGetLedColors = create_func(
            'CorsairGetLedColors', c_bool,
            [CorsairDeviceId, c_int32,
             POINTER(CorsairLedColor)])

        self.CorsairSetLayerPriority = create_func('CorsairSetLayerPriority',
                                                   CorsairError, [c_uint32])

        self.CorsairGetLedLuidForKeyName = create_func(
            'CorsairGetLedLuidForKeyName', CorsairError,
            [CorsairDeviceId, c_char,
             POINTER(CorsairLedLuid)])

        self.CorsairRequestControl = create_func(
            'CorsairRequestControl', CorsairError,
            [CorsairDeviceId, CorsairAccessMode])

        self.CorsairReleaseControl = create_func('CorsairReleaseControl',
                                                 CorsairError,
                                                 [CorsairDeviceId])
