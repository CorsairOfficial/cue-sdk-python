import os
import platform
from ctypes import (c_int32, c_uint32, c_void_p, byref, sizeof,
                    create_string_buffer)
from typing import (Any, Collection, Sequence, Optional, Callable)

from .enums import (CorsairAccessLevel, CorsairDataType, CorsairError,
                    CorsairDevicePropertyId)
from .structs import (CorsairDeviceFilter, CorsairEvent, CorsairProperty,
                      CorsairKeyEventConfiguration, CorsairLedPosition,
                      CorsairLedColor, CorsairDeviceInfo,
                      CorsairSessionDetails, CorsairSessionStateChanged)
from .native import (
    CorsairNativeApi, CorsairSessionStateChangedHandler, CorsairEventHandler,
    CorsairAsyncCallback, CORSAIR_STRING_SIZE_M, CORSAIR_DEVICE_COUNT_MAX,
    CORSAIR_DEVICE_LEDCOUNT_MAX, CORSAIR_LAYER_PRIORITY_MAX,
    CorsairSessionDetails as CorsairSessionDetailsNative, CorsairDeviceInfo as
    CorsairDeviceInfoNative, CorsairDeviceFilter as CorsairDeviceFilterNative,
    CorsairLedPosition as CorsairLedPositionNative,
    CorsairKeyEventConfiguration as CorsairKeyEventConfigurationNative,
    CorsairProperty as CorsairPropertyNative, CorsairLedColor as
    CorsairLedColorNative)

__all__ = ['CueSdk']

napi: CorsairNativeApi


def get_library_path(lib_name):
    return os.path.join(os.path.dirname(__file__), 'bin', lib_name)


def get_library_path_windows():
    lib_name = 'iCUESDK.x64_2019.dll'
    return get_library_path(lib_name)


def get_library_path_mac():
    lib_name = 'libiCUESDK.dylib'
    return get_library_path(lib_name)


def str_to_char_array(s: str, sz: int):
    return create_string_buffer(s.encode('utf-8'), sz)


def to_native_id(device_id):
    if not device_id:
        return None
    return str_to_char_array(device_id, CORSAIR_STRING_SIZE_M)


class CueSdk(object):

    def __init__(self, sdk_path: Optional[str] = None) -> None:
        global napi
        if sdk_path is None:
            system = platform.system()
            if system == "Windows":
                sdk_path = get_library_path_windows()
            elif system == "Darwin":
                sdk_path = get_library_path_mac()
        napi = CorsairNativeApi(sdk_path)
        self._protocol_details = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def connect(
        self, on_state_changed: Callable[[CorsairSessionStateChanged], None]
    ) -> CorsairError:
        if sizeof(c_void_p) < 8:
            return CorsairError(CorsairError.CE_NotAllowed)
        if on_state_changed is None:
            return CorsairError(CorsairError.CE_InvalidArguments)

        def raw_handler(ctx, e):
            evt = CorsairSessionStateChanged.create(e.contents)
            on_state_changed(evt)

        self.session_state_changed_event_handler = CorsairSessionStateChangedHandler(
            raw_handler)

        return CorsairError(
            napi.CorsairConnect(self.session_state_changed_event_handler,
                                None))

    def disconnect(self) -> CorsairError:
        self.session_state_changed_event_handler = None
        return CorsairError(napi.CorsairDisconnect())

    def get_session_details(self):
        res = None
        nobj = CorsairSessionDetailsNative()
        err = CorsairError(napi.CorsairGetSessionDetails(nobj))
        if err == CorsairError.CE_Success:
            res = CorsairSessionDetails.create(nobj)
        return (res, err)

    def get_devices(self, device_filter: CorsairDeviceFilter):
        if not device_filter:
            return (None, CorsairError(CorsairError.CE_InvalidArguments))

        df = CorsairDeviceFilterNative(
            deviceTypeMask=device_filter.device_type_mask)

        infos = (CorsairDeviceInfoNative * CORSAIR_DEVICE_COUNT_MAX)()
        cnt = c_int32()
        err = CorsairError(
            napi.CorsairGetDevices(df, CORSAIR_DEVICE_COUNT_MAX, infos,
                                   byref(cnt)))

        if err == CorsairError.CE_Success:
            return ([
                CorsairDeviceInfo.create(infos[i]) for i in range(cnt.value)
            ], err)

        return (None, err)

    def get_device_info(self, device_id: str):
        if not device_id:
            return (None, CorsairError(CorsairError.CE_InvalidArguments))

        nobj = CorsairDeviceInfoNative()
        err = CorsairError(
            napi.CorsairGetDeviceInfo(to_native_id(device_id), nobj))
        if err == CorsairError.CE_Success:
            return (CorsairDeviceInfo.create(nobj), err)
        return (None, err)

    def get_led_positions(self, device_id: str):
        if not device_id:
            return (None, CorsairError(CorsairError.CE_InvalidArguments))

        leds = (CorsairLedPositionNative * CORSAIR_DEVICE_LEDCOUNT_MAX)()
        cnt = c_int32()
        err = CorsairError(
            napi.CorsairGetLedPositions(to_native_id(device_id),
                                        CORSAIR_DEVICE_LEDCOUNT_MAX, leds,
                                        byref(cnt)))

        if err == CorsairError.CE_Success:
            return ([
                CorsairLedPosition.create(leds[i]) for i in range(cnt.value)
            ], err)

        return (None, err)

    def subscribe_for_events(
            self, on_event: Callable[[CorsairEvent], None]) -> CorsairError:
        if on_event is None:
            return CorsairError(CorsairError.CE_InvalidArguments)

        def raw_handler(ctx, e):
            evt = CorsairEvent.create(e.contents)
            on_event(evt)

        self.event_handler = CorsairEventHandler(raw_handler)
        return CorsairError(
            napi.CorsairSubscribeForEvents(self.event_handler, None))

    def unsubscribe_from_events(self) -> CorsairError:
        self.event_handler = None
        return CorsairError(napi.CorsairUnsubscribeFromEvents())

    def configure_key_event(
            self, device_id: str,
            configuration: CorsairKeyEventConfiguration) -> CorsairError:
        if not device_id or not configuration:
            return CorsairError(CorsairError.CE_InvalidArguments)

        cfg = CorsairKeyEventConfigurationNative()
        cfg.keyId = configuration.key_id
        cfg.isIntercepted = configuration.is_intercepted
        return CorsairError(
            napi.CorsairConfigureKeyEvent(to_native_id(device_id), cfg))

    def get_device_property_info(self,
                                 device_id: str,
                                 property_id: CorsairDevicePropertyId,
                                 index: int = 0):
        if not device_id or not property_id or index < 0:
            return (None, CorsairError(CorsairError.CE_InvalidArguments))

        dt = c_uint32()
        flags = c_uint32()
        err = CorsairError(
            napi.CorsairGetDevicePropertyInfo(to_native_id(device_id),
                                              property_id, index, byref(dt),
                                              byref(flags)))

        res = None
        if err == CorsairError.CE_Success:
            res = {'data_type': CorsairDataType(dt.value), 'flags': flags.value}

        return (res, err)

    def read_device_property(self,
                             device_id: str,
                             property_id: CorsairDevicePropertyId,
                             index: int = 0):
        if not device_id or not property_id or index < 0:
            return (None, CorsairError(CorsairError.CE_InvalidArguments))

        nobj = CorsairPropertyNative()
        err = CorsairError(
            napi.CorsairReadDeviceProperty(to_native_id(device_id),
                                           property_id, index, nobj))

        if err == CorsairError.CE_Success:
            return (CorsairProperty.create(nobj), err)

        return (None, err)

    def write_device_property(self, device_id: str,
                              property_id: CorsairDevicePropertyId, index: int,
                              prop: Any) -> CorsairError:
        if not device_id or not property_id or index < 0 or not prop:
            return CorsairError(CorsairError.CE_InvalidArguments)

        nobj = CorsairPropertyNative()
        nobj.type = prop.type
        nobj.value = prop.value  # TODO: convert value to native object

        return CorsairError(
            napi.CorsairWriteDeviceProperty(to_native_id(device_id),
                                            property_id, index, nobj))

    def request_control(self, device_id: str,
                        access_level: CorsairAccessLevel) -> CorsairError:
        return CorsairError(
            napi.CorsairRequestControl(to_native_id(device_id), access_level))

    def release_control(self, device_id: Optional[str]) -> CorsairError:
        return CorsairError(napi.CorsairReleaseControl(
            to_native_id(device_id)))

    def set_layer_priority(self, priority: int) -> CorsairError:
        if not 0 <= priority <= CORSAIR_LAYER_PRIORITY_MAX:
            return CorsairError(CorsairError.CE_InvalidArguments)

        return CorsairError(napi.CorsairSetLayerPriority(priority))

    def get_led_luid_for_key_name(self, device_id: str, key_name: str):
        if not device_id or not isinstance(key_name, str):
            return (None, CorsairError(CorsairError.CE_InvalidArguments))

        encoded = key_name.encode()
        if len(encoded) != 1 or not ord('A') <= encoded[0] <= ord('Z'):
            return (None, CorsairError(CorsairError.CE_InvalidArguments))
        luid = c_uint32()
        err = CorsairError(
            napi.CorsairGetLedLuidForKeyName(to_native_id(device_id), encoded,
                                             byref(luid)))
        if (err == CorsairError.CE_Success):
            return (int(luid.value), err)
        return (None, err)

    def set_led_colors(
            self, device_id: str,
            led_colors: Collection[CorsairLedColor]) -> CorsairError:
        if not device_id:
            return CorsairError(CorsairError.CE_InvalidArguments)

        sz = len(led_colors)
        data = (CorsairLedColorNative * sz)()
        for i, led in enumerate(led_colors):
            data[i] = CorsairLedColorNative(id=int(led.id),
                                            r=led.r,
                                            g=led.g,
                                            b=led.b,
                                            a=led.a)
        return CorsairError(
            napi.CorsairSetLedColors(to_native_id(device_id), sz, data))

    def set_led_colors_buffer(
            self, device_id: str,
            led_colors: Collection[CorsairLedColor]) -> CorsairError:
        if not device_id:
            return CorsairError(CorsairError.CE_InvalidArguments)

        sz = len(led_colors)
        data = (CorsairLedColorNative * sz)()
        for i, led in enumerate(led_colors):
            data[i] = CorsairLedColorNative(id=int(led.id),
                                            r=led.r,
                                            g=led.g,
                                            b=led.b,
                                            a=led.a)
        return CorsairError(napi.CorsairSetLedColorsBuffer(
            to_native_id(device_id), sz, data))

    def set_led_colors_flush_buffer_async(
            self,
            callback: Optional[Callable[[CorsairError], None]]) -> CorsairError:
        if not callback:
            return CorsairError(
                napi.CorsairSetLedColorsFlushBufferAsync(None, None))

        def raw_handler(ctx, e):
            err = CorsairError(e)
            callback(err)

        async_callback = CorsairAsyncCallback(raw_handler)

        return CorsairError(
            napi.CorsairSetLedColorsFlushBufferAsync(async_callback, None))

    def get_led_colors(self, device_id: str,
                       led_colors: Sequence[CorsairLedColor]):
        if not device_id:
            return (None, CorsairError(CorsairError.CE_InvalidArguments))

        sz = len(led_colors)
        data = (CorsairLedColorNative * sz)()
        for i in range(sz):
            data[i].id = int(led_colors[i].id)
        err = CorsairError(
            napi.CorsairGetLedColors(to_native_id(device_id), sz, data))
        if err == CorsairError.CE_Success:
            return (list([CorsairLedColor.create(data[i])
                          for i in range(sz)]), err)

        return (None, err)
