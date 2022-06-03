import sys
from ctypes import (CDLL, CFUNCTYPE, POINTER, c_bool, c_char, c_int32,
                    c_void_p)
from ..enums import (CorsairAccessMode, CorsairError, CorsairLedId,
                     CorsairDevicePropertyId)
from . import (CorsairProtocolDetails, CorsairDeviceInfo, CorsairLedPositions,
               CorsairLedColor, CorsairEvent)

__all__ = ['CorsairNativeApi']


def load_library(library_path):
    try:
        return CDLL(library_path)
    except OSError:
        print("Unable to load the library %s" % library_path)
        sys.exit()


class CorsairNativeApi():

    def __init__(self, libpath):
        lib = load_library(libpath)

        def create_func(fn, restype, argtypes):
            f = lib.__getattr__(fn)
            f.restype = restype
            f.argtypes = argtypes
            return f

        self.CorsairSetLedsColorsBufferByDeviceIndex = create_func(
            'CorsairSetLedsColorsBufferByDeviceIndex', c_bool,
            [c_int32, c_int32, POINTER(CorsairLedColor)])
        self.CorsairSetLedsColorsFlushBuffer = create_func(
            'CorsairSetLedsColorsFlushBuffer', c_bool, None)
        self.CallbackFunc = CFUNCTYPE(c_void_p, c_bool, CorsairError)
        self.CorsairSetLedsColorsFlushBufferAsync = create_func(
            'CorsairSetLedsColorsFlushBufferAsync', c_bool,
            [self.CallbackFunc, c_void_p])
        self.CorsairGetLedsColors = create_func(
            'CorsairGetLedsColors', c_bool,
            [c_int32, POINTER(CorsairLedColor)])
        self.CorsairGetLedsColorsByDeviceIndex = create_func(
            'CorsairGetLedsColorsByDeviceIndex', c_bool,
            [c_int32, c_int32, POINTER(CorsairLedColor)])
        self.CorsairGetDeviceCount = create_func('CorsairGetDeviceCount',
                                                 c_int32, None)
        self.CorsairGetDeviceInfo = create_func('CorsairGetDeviceInfo',
                                                POINTER(CorsairDeviceInfo),
                                                [c_int32])
        self.CorsairGetLedPositions = create_func('CorsairGetLedPositions',
                                                  POINTER(CorsairLedPositions),
                                                  None)
        self.CorsairGetLedPositionsByDeviceIndex = create_func(
            'CorsairGetLedPositionsByDeviceIndex',
            POINTER(CorsairLedPositions), [c_int32])
        self.CorsairGetLedIdForKeyName = create_func(
            'CorsairGetLedIdForKeyName', CorsairLedId, [c_char])
        self.CorsairRequestControl = create_func('CorsairRequestControl',
                                                 c_bool, [CorsairAccessMode])
        self.CorsairPerformProtocolHandshake = create_func(
            'CorsairPerformProtocolHandshake', CorsairProtocolDetails, None)
        self.CorsairGetLastError = create_func('CorsairGetLastError',
                                               CorsairError, None)
        self.CorsairReleaseControl = create_func('CorsairReleaseControl',
                                                 c_bool, [CorsairAccessMode])
        self.CorsairSetLayerPriority = create_func('CorsairSetLayerPriority',
                                                   c_bool, [c_int32])
        c_bool_p = POINTER(c_bool)
        self.CorsairGetBoolPropertyValue = create_func(
            'CorsairGetBoolPropertyValue', c_bool,
            [c_int32, CorsairDevicePropertyId, c_bool_p])
        c_int32_p = POINTER(c_int32)
        self.CorsairGetInt32PropertyValue = create_func(
            'CorsairGetInt32PropertyValue', c_bool,
            [c_int32, CorsairDevicePropertyId, c_int32_p])
        self.EventHandler = CFUNCTYPE(None, c_void_p, POINTER(CorsairEvent))
        self.CorsairSubscribeForEvents = create_func(
            'CorsairSubscribeForEvents', c_bool, [self.EventHandler, c_void_p])
        self.CorsairUnsubscribeFromEvents = create_func(
            'CorsairUnsubscribeFromEvents', c_bool, None)
