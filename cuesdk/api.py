import ctypes
from .enums import (CorsairAccessMode,
                    CorsairError,
                    CorsairDevicePropertyId,
                    CorsairDevicePropertyType,
                    CorsairLedId,
                    CorsairEventId)
from .structs import (CorsairProtocolDetails,
                      CorsairDeviceInfo,
                      CorsairLedPosition,
                      CorsairLedPositions,
                      CorsairLedColor,
                      CorsairEvent)
from .capi import CorsairNativeApi

__all__ = ['CueSdk']


class Device():
    def __init__(self, id, type, model, caps_mask, led_count, channels):
        self.id = id
        self.type = type
        self.model = model
        self.caps_mask = caps_mask
        self.led_count = led_count
        self.channels = channels

    def __repr__(self):
        return str(self.model)


class Channel():
    def __init__(self, total_led_count, devices):
        self.total_led_count = total_led_count
        self.devices = devices


class ChannelDevice():
    def __init__(self, type, led_count):
        self.type = type
        self.led_count = led_count


class CueSdk():
    def __init__(self, sdk_path=None):
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

    def get_device_count(self):
        """
        Returns number of connected Corsair devices.
        For keyboards, mice, mousemats, headsets and headset stands not more
        than one device of each type is included in return value in case if
        there are multiple devices of same type connected to the system.
        For DIY-devices and coolers actual number of connected devices is
        included in return value. For memory modules actual number of
        connected modules is included in return value, modules are enumerated
        with respect to their logical position (counting from left to right,
        from top to bottom).

        Use get_device_info() to get information about a certain device.
        """
        return native.CorsairGetDeviceCount()

    def get_device_info(self, device_index):
        """
        Returns information about a device based on provided index.

        Parameters
        ----------
        device_index : int
            Zero-based index of device. Should be strictly less than a value
            returned by get_device_count()
        """
        p = native.CorsairGetDeviceInfo(device_index)
        s = p.contents
        channels = []
        for chi in range(s.channels.channelsCount):
            ch = s.channels.channels[chi]
            devices = [
                ChannelDevice(ch.devices[i].type, ch.devices[i].deviceLedCount)
                for i in range(ch.devicesCount)]
            channels.append(Channel(ch.totalLedsCount, devices))
        return Device(s.deviceId.decode(), s.type, s.model.decode(),
                      s.capsMask, s.ledsCount, channels)

    def get_last_error(self):
        """
        Returns last error that occurred in this thread while using
        any of SDK functions.
        """
        return native.CorsairGetLastError()

    def request_control(self):
        """
        Requests exclusive control over lighting.
        By default client has shared control over lighting so there is no need
        to call request_control() unless a client requires exclusive control.
        """
        return native.CorsairRequestControl(
            CorsairAccessMode.ExclusiveLightingControl)

    def release_control(self):
        """
        Releases previously requested exclusive control.
        """
        return native.CorsairReleaseControl(
            CorsairAccessMode.ExclusiveLightingControl)

    def set_layer_priority(self, priority):
        """
        Sets layer priority for this shared client.
        By default CUE has priority of 127 and all shared clients have
        priority of 128 if they don't call this function. Layers with
        higher priority value are shown on top of layers with lower priority.

        Parameters
        ----------
        priority : int
            Priority of a layer [0..255]

        Returns
        -------
        boolean value. True if successful. Use get_last_error() to check the
        reason of failure. If this function is called in exclusive mode
        then it will return True
        """
        return native.CorsairSetLayerPriority(priority)

    def get_led_id_for_key_name(self, key_name):
        """
        Retrieves led id for key name taking logical layout into
        account. So on AZERTY keyboards if user calls
        get_led_id_for_key_name('A') he gets CorsairLedId.K_Q.
        This id can be used in set_led_colors_buffer_by_device_index function

        Parameters
        ----------
        key_name : char
            Key name. ['A'..'Z'] (26 values) are valid values

        Returns
        -------
        Proper CorsairLedId or CorsairLedId.Invalid if error occurred
        """
        return native.CorsairGetLedIdForKeyName(key_name)

    def set_led_colors_buffer_by_device_index(self, device_index, colors):
        """
        Sets specified LEDs to some colors. This function set LEDs colors
        in the buffer which is written to the devices via
        set_led_colors_flush_buffer or set_led_colors_flush_buffer_async.
        Typical usecase is next: set_led_colors_flush_buffer or
        set_led_colors_flush_buffer_async is called to write LEDs colors to
        the device and follows after one or more calls of
        set_led_colors_buffer_by_device_index to set the LEDs buffer.
        This function does not take logical layout into account.

        Parameters
        ----------
        device_index : int
            Zero-based index of device. Should be strictly less than value
            returned by get_device_count()
        colors : list
            The list containing colors for each LED: each item is a list
            with items [ledId, r, g, b]
        """
        sz = len(colors)
        data = (CorsairLedColor * sz)()
        for i, led in enumerate(colors):
            c = CorsairLedColor()
            c.ledId = led[0]
            c.r = led[1]
            c.g = led[2]
            c.b = led[3]
            data[i] = c
        return native.CorsairSetLedsColorsBufferByDeviceIndex(
                        device_index, sz, data)

    def set_led_colors_flush_buffer(self):
        """
        Writes to the devices LEDs colors buffer which is previously filled by
        the set_led_colors_buffer_by_device_index function. This function
        executes synchronously, if you are concerned about delays consider
        using set_led_colors_flush_buffer_async
        """
        return native.CorsairSetLedsColorsFlushBuffer()

    def set_led_colors_flush_buffer_async(self):
        """
        Same as set_led_colors_flush_buffer but returns control to the caller
        immediately
        """
        return native.CorsairSetLedsColorsFlushBufferAsync(None, None)

    def get_led_colors_by_device_index(self, device_index, led_identifiers):
        """
        Gets current color for the list of requested LEDs.
        The color should represent the actual state of the hardware LED, which
        could be a combination of SDK and/or CUE input. This function works
        for keyboard, mouse, mousemat, headset, headset stand, DIY-devices,
        memory module and cooler.

        Parameters
        ----------
        device_index : int
            Zero-based index of device. Should be strictly less than value
            returned by get_device_count()

        led_identifiers : list
            The list of CorsairLedId values

        Returns
        -------
        The list of LED colors: each item is a list with items
        [ledId, r, g, b]
        """
        sz = len(led_identifiers)
        data = (CorsairLedColor * sz)()
        for i in range(sz):
            data[i].ledId = led_identifiers[i]
        ok = native.CorsairGetLedsColorsByDeviceIndex(device_index, sz, data)
        ret = []
        for i in range(sz):
            c = data[i]
            ret.append([c.ledId, c.r, c.g, c.b])
        return ret

    def get_led_positions_by_device_index(self, device_index):
        """
        Provides list of keyboard, mouse, headset, mousemat, headset stand,
        DIY-devices, memory module and cooler LEDs by its index with their
        positions. Position could be either physical (only device-dependent)
        or logical (depend on device as well as CUE settings).

        Parameters
        ----------
        device_index : int
            The index of the device

        Returns
        -------
        The list of positions: each item is a list with items [ledId, x, y]
        """
        leds = native.CorsairGetLedPositionsByDeviceIndex(device_index)
        positions = []
        for i in range(leds.contents.numberOfLed):
            p = leds.contents.pLedPosition[i]
            positions.append([p.ledId, p.left, p.top])
        return positions

    def subscribe_for_events(self, handler):
        """
        Parameters
        ----------
        handler : function
            Callback function with two arguments: event_id and event_data
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
        self.event_handler = None
        return native.CorsairUnsubscribeFromEvents()

    def get_property(self, device_index, property_id):
        if (property_id & CorsairDevicePropertyType.Boolean) != 0:
            prop = ctypes.c_bool()
            success = native.CorsairGetBoolPropertyValue(
                device_index, property_id, ctypes.byref(prop))
            if success:
                return prop.value
        elif (property_id & CorsairDevicePropertyType.Int32) != 0:
            prop = ctypes.c_int32()
            success = native.CorsairGetInt32PropertyValue(
                device_index, property_id, ctypes.byref(prop))
            if success:
                return prop.value
        return None
