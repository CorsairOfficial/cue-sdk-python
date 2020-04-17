from ctypes import c_bool, c_int32, byref
from typing import Any, Optional, Union, Callable, Dict, Sequence, Tuple

from .capi import CorsairNativeApi
from .enums import (CorsairAccessMode, CorsairError, CorsairDevicePropertyId,
                    CorsairDevicePropertyType, CorsairLedId, CorsairEventId)
from .helpers import ColorRgb
from .structs import (CorsairProtocolDetails, CorsairDeviceInfo,
                      CorsairLedPosition, CorsairLedPositions, CorsairLedColor,
                      CorsairEvent)
from .utils import bytes_to_str_or_default

__all__ = ['CueSdk']


class Device(object):
    def __init__(self, id, type, model, caps_mask, led_count, channels):
        self.id = id
        self.type = type
        self.model = model
        self.caps_mask = caps_mask
        self.led_count = led_count
        self.channels = channels

    def __repr__(self):
        return self.model


class Channel(object):
    def __init__(self, total_led_count, devices):
        self.total_led_count = total_led_count
        self.devices = devices


class ChannelDevice(object):
    def __init__(self, type, led_count):
        self.type = type
        self.led_count = led_count


class CueSdk(object):
    def __init__(self, sdk_path: Optional[str] = None) -> None:
        global native
        native = CorsairNativeApi(sdk_path)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def connect(self):
        self.protocol_details = native.CorsairPerformProtocolHandshake()
        err = native.CorsairGetLastError()
        return err == CorsairError.Success

    def get_devices(self):
        cnt = native.CorsairGetDeviceCount()
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
        return native.CorsairGetDeviceCount()

    def get_device_info(self, device_index: int):
        """Returns information about a device based on provided index.

        Args:
            device_index: zero-based index of device. Should be strictly
                less than a value returned by `CueSdk.get_device_count`
        """
        p = native.CorsairGetDeviceInfo(device_index)
        s = p.contents
        channels = []
        for chi in range(s.channels.channelsCount):
            ch = s.channels.channels[chi]
            devices = [
                ChannelDevice(ch.devices[i].type, ch.devices[i].deviceLedCount)
                for i in range(ch.devicesCount)
            ]
            channels.append(Channel(ch.totalLedsCount, devices))
        return Device(bytes_to_str_or_default(s.deviceId), s.type,
                      bytes_to_str_or_default(s.model), s.capsMask,
                      s.ledsCount, channels)

    def get_last_error(self) -> CorsairError:
        """Returns last error that occurred in this thread while using
        any of SDK functions.
        """
        return native.CorsairGetLastError()

    def request_control(self) -> bool:
        """Requests exclusive control over lighting.

        By default client has shared control over lighting so there is
        no need to call `CueSdk.request_control` unless a client
        requires exclusive control.
        """
        return native.CorsairRequestControl(
            CorsairAccessMode.ExclusiveLightingControl)

    def release_control(self) -> bool:
        """Releases previously requested exclusive control."""
        return native.CorsairReleaseControl(
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
        return native.CorsairSetLayerPriority(priority)

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
        if not isinstance(key_name,
                          str) or len(key_name) != 1 or not key_name.isalpha():
            return CorsairLedId(CorsairLedId.Invalid)

        return native.CorsairGetLedIdForKeyName(key_name.encode())

    def set_led_colors_buffer_by_device_index(
            self, device_index: int,
            led_colors: Dict[CorsairLedId, Tuple[int, int, int]]) -> bool:
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
            led_colors: a dict mapping `CorsairLedId` keys to the corresponding
                color values. Each color is represented as a tuple of ints
                (r, g, b). For example:

            ```python
            { CorsairLedId.K_F1: (255, 0, 0) }
            ```
        """
        sz = len(led_colors)
        data = (CorsairLedColor * sz)()
        rgb_keys = ['r', 'g', 'b']
        for i, led in enumerate(led_colors):
            rgb = dict(zip(rgb_keys, led_colors[led]))
            data[i] = CorsairLedColor(ledId=led, **rgb)
        return native.CorsairSetLedsColorsBufferByDeviceIndex(
            device_index, sz, data)

    def set_led_colors_flush_buffer(self) -> bool:
        """Writes to the devices LEDs colors buffer which is previously filled
        by the `CueSdk.set_led_colors_buffer_by_device_index` function.

        This function executes synchronously, if you are concerned about
        delays consider using `CueSdk.set_led_colors_flush_buffer_async`
        """
        return native.CorsairSetLedsColorsFlushBuffer()

    def set_led_colors_flush_buffer_async(self) -> bool:
        """Same as `CueSdk.set_led_colors_flush_buffer` but returns control to
        the caller immediately
        """
        return native.CorsairSetLedsColorsFlushBufferAsync(None, None)

    def get_led_colors_by_device_index(
        self, device_index: int, led_identifiers: Sequence[CorsairLedId]
    ) -> Union[None, Dict[CorsairLedId, Tuple[int, int, int]]]:
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
        data = (CorsairLedColor * sz)()
        for i in range(sz):
            data[i].ledId = led_identifiers[i]
        ok = native.CorsairGetLedsColorsByDeviceIndex(device_index, sz, data)
        if not ok:
            return None
        ret = {}
        for i in range(sz):
            c = data[i]
            ret[c.ledId] = (c.r, c.g, c.b)
        return ret

    def get_led_positions_by_device_index(
        self, device_index: int
    ) -> Union[None, Dict[CorsairLedId, Tuple[float, float]]]:
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
        leds = native.CorsairGetLedPositionsByDeviceIndex(device_index)
        if not leds:
            return None
        positions = {}
        for i in range(leds.contents.numberOfLed):
            p = leds.contents.pLedPosition[i]
            positions[p.ledId] = (p.left, p.top)
        return positions

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
            id = e[0].id
            if (id == CorsairEventId.DeviceConnectionStatusChangedEvent):
                handler(id, e[0].deviceConnectionStatusChangedEvent[0])
            elif (id == CorsairEventId.KeyEvent):
                handler(id, e[0].keyEvent[0])

        self.event_handler = native.EventHandler(raw_handler)
        return native.CorsairSubscribeForEvents(self.event_handler, None)

    def unsubscribe_from_events(self):
        """Unregisters callback previously registered by
        `CueSdk.subscribe_for_events` call

        Returns:
            boolean value. True if successful. Use `CueSdk.get_last_error`
            to check the reason of failure.
        """
        self.event_handler = None
        return native.CorsairUnsubscribeFromEvents()

    def get_property(self, device_index, property_id):
        if (property_id & CorsairDevicePropertyType.Boolean) != 0:
            prop = c_bool()
            success = native.CorsairGetBoolPropertyValue(
                device_index, property_id, byref(prop))
            if success:
                return prop.value
        elif (property_id & CorsairDevicePropertyType.Int32) != 0:
            prop = c_int32()
            success = native.CorsairGetInt32PropertyValue(
                device_index, property_id, byref(prop))
            if success:
                return prop.value
        return None
