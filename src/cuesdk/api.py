import os
import platform
from ctypes import c_bool, c_int32, c_void_p, byref, sizeof
from typing import (Any, List, Collection, Mapping, Optional, Union, Callable,
                    Tuple)

from .enums import (CorsairAccessMode, CorsairError, CorsairDevicePropertyId,
                    CorsairDevicePropertyType, CorsairLedId, CorsairEventId)
from .structs import (CorsairEvent, CorsairLedPositions, CorsairLedPosition,
                      CorsairLedColor, CorsairProtocolDetails,
                      CorsairDeviceInfo)
from .native import CorsairNativeApi, CorsairLedColor as CorsairLedColorStruct

__all__ = ['CueSdk']

napi: CorsairNativeApi = None


def get_library_path(lib_name):
    return os.path.join(os.path.dirname(__file__), 'bin', lib_name)


def get_library_path_windows():
    suffix = '.x64' if sizeof(c_void_p) == 8 else ''
    lib_name = 'CUESDK' + suffix + '_2017.dll'
    return get_library_path(lib_name)


def get_library_path_mac():
    lib_name = 'libCUESDK.dylib'
    return get_library_path(lib_name)


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

    def connect(self) -> bool:
        details = napi.CorsairPerformProtocolHandshake()
        self._protocol_details = CorsairProtocolDetails.create(details)
        err = self.get_last_error()
        return err == CorsairError.Success

    @property
    def protocol_details(self) -> CorsairProtocolDetails:
        return self._protocol_details

    def get_devices(self):
        cnt = napi.CorsairGetDeviceCount()
        if cnt > 0:
            return [self.get_device_info(i) for i in range(cnt)]
        return []

    def get_device_count(self) -> int:
        """Returns number of connected Corsair devices.

        For keyboards, mice, mousemats, headsets and headset stands not more
        than one device of each type is included in return value in case if
        there are multiple devices of same type connected to the system.
        For DIY-devices and coolers actual number of connected devices is
        included in return value. For memory modules actual number of
        connected modules is included in return value, modules are enumerated
        with respect to their logical position (counting from left to right,
        from top to bottom).

        Use `CueSdk.get_device_info` to get information about a certain device.
        """
        return napi.CorsairGetDeviceCount()

    def get_device_info(self, device_index: int):
        """Returns information about a device based on provided index.

        Args:
            device_index: zero-based index of device. Should be strictly
                less than a value returned by `CueSdk.get_device_count`
        """
        p = napi.CorsairGetDeviceInfo(device_index)
        return CorsairDeviceInfo.create(p)

    def get_last_error(self) -> CorsairError:
        """Returns last error that occurred in this thread while using
        any of SDK functions.
        """
        return CorsairError(napi.CorsairGetLastError())

    def request_control(self) -> bool:
        """Requests exclusive control over lighting.

        By default client has shared control over lighting so there is
        no need to call `CueSdk.request_control` unless a client
        requires exclusive control.
        """
        return napi.CorsairRequestControl(
            CorsairAccessMode.ExclusiveLightingControl)

    def release_control(self) -> bool:
        """Releases previously requested exclusive control."""
        return napi.CorsairReleaseControl(
            CorsairAccessMode.ExclusiveLightingControl)

    def set_layer_priority(self, priority: int) -> bool:
        """Sets layer priority for this shared client.

        By default CUE has priority of 127 and all shared clients have
        priority of 128 if they don't call this function. Layers with
        higher priority value are shown on top of layers with lower priority.

        Args:
            priority: priority of a layer [0..255]

        Returns:
            boolean value. True if successful. Use `CueSdk.get_last_error`
            to check the reason of failure. If this function is called in
            exclusive mode then it will return True
        """
        return napi.CorsairSetLayerPriority(priority)

    def get_led_id_for_key_name(self, key_name: str) -> CorsairLedId:
        """Retrieves led id for key name taking logical layout into account.

        So on AZERTY keyboards if user calls `get_led_id_for_key_name('A')` he
        gets `CorsairLedId.K_Q`. This id can be used in
        `CueSdk.set_led_colors_buffer_by_device_index` function

        Args:
            key_name: key name. ['A'..'Z'] (26 values) are valid values

        Returns:
            Proper `CorsairLedId` or `CorsairLedId.Invalid` if error
            occurred
        """
        if not isinstance(key_name, str):
            raise TypeError("'key_name' argument must be a string")
        encoded = key_name.encode()
        if len(encoded) != 1 or not ord('A') <= encoded[0] <= ord('Z'):
            return CorsairLedId(CorsairLedId.Invalid)

        return CorsairLedId(napi.CorsairGetLedIdForKeyName(encoded))

    def _set_led_colors_buffer_by_device_index(
            self, device_index: int,
            led_colors: Mapping[CorsairLedId, Tuple[int, int, int]]) -> bool:
        """DEPRECATED. Sets specified LEDs to some colors.

        This function set LEDs colors in the buffer which is written to the
        devices via `CueSdk.set_led_colors_flush_buffer` or
        `CueSdk.set_led_colors_flush_buffer_async`.
        Typical usecase is next: `CueSdk.set_led_colors_flush_buffer` or
        `CueSdk.set_led_colors_flush_buffer_async` is called to write LEDs
        colors to the device and follows after one or more calls of
        `CueSdk.set_led_colors_buffer_by_device_index` to set the LEDs buffer.
        This function does not take logical layout into account.

        Args:
            device_index: zero-based index of device. Should be strictly less
                than value returned by `CueSdk.get_device_count`
            led_colors: a dict mapping `CorsairLedId` keys to the corresponding
                color values. Each color is represented as a tuple of ints
                (r, g, b). For example:

            ```python
            { CorsairLedId.K_F1: (255, 0, 0) }
            ```
        """
        sz = len(led_colors)
        data = (CorsairLedColorStruct * sz)()
        rgb_keys = ['r', 'g', 'b']
        for i, led in enumerate(led_colors):
            rgb = dict(zip(rgb_keys, led_colors[led]))
            data[i] = CorsairLedColorStruct(ledId=led, **rgb)
        return napi.CorsairSetLedsColorsBufferByDeviceIndex(
            device_index, sz, data)

    def set_led_colors_buffer_by_device_index(
            self, device_index: int,
            led_colors: Collection[CorsairLedColor]) -> bool:
        """Sets specified LEDs to some colors.

        This function set LEDs colors in the buffer which is written to the
        devices via `CueSdk.set_led_colors_flush_buffer` or
        `CueSdk.set_led_colors_flush_buffer_async`.
        Typical usecase is next: `CueSdk.set_led_colors_flush_buffer` or
        `CueSdk.set_led_colors_flush_buffer_async` is called to write LEDs
        colors to the device and follows after one or more calls of
        `CueSdk.set_led_colors_buffer_by_device_index` to set the LEDs buffer.
        This function does not take logical layout into account.

        Args:
            device_index: zero-based index of device. Should be strictly less
                than value returned by `CueSdk.get_device_count`
            led_colors: a list of `CorsairLedColor` elements.
        """
        sz = len(led_colors)
        data = (CorsairLedColorStruct * sz)()
        for i, led in enumerate(led_colors):
            data[i] = CorsairLedColorStruct(ledId=int(led.led_id),
                                            r=led.r,
                                            g=led.g,
                                            b=led.b)
        return napi.CorsairSetLedsColorsBufferByDeviceIndex(
            device_index, sz, data)

    def set_led_colors_flush_buffer(self) -> bool:
        """Writes to the devices LEDs colors buffer which is previously filled
        by the `CueSdk.set_led_colors_buffer_by_device_index` function.

        This function executes synchronously, if you are concerned about
        delays consider using `CueSdk.set_led_colors_flush_buffer_async`
        """
        return napi.CorsairSetLedsColorsFlushBuffer()

    def set_led_colors_flush_buffer_async(self) -> bool:
        """Same as `CueSdk.set_led_colors_flush_buffer` but returns control to
        the caller immediately
        """
        return napi.CorsairSetLedsColorsFlushBufferAsync(None, None)

    def _get_led_colors_by_device_index(
        self, device_index: int, led_identifiers: Collection[CorsairLedId]
    ) -> Union[None, Mapping[CorsairLedId, Tuple[int, int, int]]]:
        """DEPRECATED. Gets current color for the requested LEDs.

        The color should represent the actual state of the hardware LED, which
        could be a combination of SDK and/or CUE input. This function works
        for keyboard, mouse, mousemat, headset, headset stand, DIY-devices,
        memory module and cooler.

        Args:
            device_index: zero-based index of device. Should be strictly less
                than value returned by `CueSdk.get_device_count`
            led_identifiers: the list of `CorsairLedId` values

        Returns:
            A dict mapping `CorsairLedId` keys to the corresponding color
            values. Each color is represented as a tuple of ints. For
            example:

            ```python
            {
                CorsairLedId.K_Escape: (255, 0, 0),
                CorsairLedId.K_F1: (128, 0, 128)
            }
            ```

            If error occurred, the function returns None
        """
        sz = len(led_identifiers)
        data = (CorsairLedColorStruct * sz)()
        for i in range(sz):
            data[i].ledId = led_identifiers[i]
        ok = napi.CorsairGetLedsColorsByDeviceIndex(device_index, sz, data)
        if not ok:
            return None
        ret = {}
        for i in range(sz):
            c = data[i]
            ret[c.ledId] = (c.r, c.g, c.b)
        return ret

    def get_led_colors_by_device_index(
        self, device_index: int, led_identifiers: Collection[CorsairLedId]
    ) -> Union[None, List[CorsairLedColor]]:
        """Gets current color for the requested LEDs.

        The color should represent the actual state of the hardware LED, which
        could be a combination of SDK and/or CUE input. This function works
        for keyboard, mouse, mousemat, headset, headset stand, DIY-devices,
        memory module and cooler.

        Args:
            device_index: zero-based index of device. Should be strictly less
                than value returned by `CueSdk.get_device_count`
            led_identifiers: the list of `CorsairLedId` values

        Returns:
            A list if `CorsairLedColor` elements.
            If error occurred, the function returns None
        """
        sz = len(led_identifiers)
        data = (CorsairLedColorStruct * sz)()
        for i in range(sz):
            data[i].ledId = int(led_identifiers[i])
        ok = napi.CorsairGetLedsColorsByDeviceIndex(device_index, sz, data)
        if not ok:
            return None
        return list([CorsairLedColor.create(data[i]) for i in range(sz)])

    def get_led_positions_by_device_index(
        self, device_index: int
    ) -> Union[None, Mapping[CorsairLedPosition, Tuple[float, float]]]:
        """Provides dictionary of keyboard, mouse, headset, mousemat,
        headset stand, DIY-devices, memory module and cooler LEDs by its index
        with their positions.

        Position could be either physical (only device-dependent)
        or logical (depend on device as well as CUE settings).

        Args:
            device_index: zero-based index of device. Should be strictly less
                than value returned by `CueSdk.get_device_count`

        Returns:
            A dict mapping `CorsairLedId` keys to the corresponding LED
            positions. Each position is represented as a tuple of floats.
            For example:

            ```python
            { CorsairLedId.K_Escape: (77.0, 36.0) }
            ```

            If error occurred, the function returns None
        """
        leds = napi.CorsairGetLedPositionsByDeviceIndex(device_index)
        if not leds:
            return None
        return CorsairLedPositions.create(leds)

    def subscribe_for_events(
            self, handler: Callable[[CorsairEventId, Any], None]) -> bool:
        """Registers a callback that will be called by SDK when some event
        happened.

        If client is already subscribed but calls this function again SDK
        should use only last callback registered for sending notifications.

        Args:
            handler:
                Callback function with two arguments: event_id and event_data

        Returns:
            boolean value. True if successful. Use `CueSdk.get_last_error`
            to check the reason of failure.
        """
        if handler is None:
            return False

        def raw_handler(ctx, e):
            evt = CorsairEvent.create(e)
            handler(evt.id, evt.data)

        self.event_handler = napi.EventHandler(raw_handler)
        return napi.CorsairSubscribeForEvents(self.event_handler, None)

    def unsubscribe_from_events(self):
        """Unregisters callback previously registered by
        `CueSdk.subscribe_for_events` call

        Returns:
            boolean value. True if successful. Use `CueSdk.get_last_error`
            to check the reason of failure.
        """
        self.event_handler = None
        return napi.CorsairUnsubscribeFromEvents()

    def get_property(self, device_index: int,
                     property_id: CorsairDevicePropertyId):
        pid = int(property_id)
        if (pid & CorsairDevicePropertyType.Boolean) != 0:
            prop = c_bool()
            success = napi.CorsairGetBoolPropertyValue(device_index, pid,
                                                       byref(prop))
            if success:
                return prop.value
        elif (pid & CorsairDevicePropertyType.Int32) != 0:
            prop = c_int32()
            success = napi.CorsairGetInt32PropertyValue(
                device_index, pid, byref(prop))
            if success:
                return prop.value
        return None
