from dataclasses import dataclass
from typing import Union
from .enums import (CorsairDataType, CorsairEventId, CorsairDeviceType,
                    CorsairMacroKeyId, CorsairSessionState)

__all__ = [
    'CorsairVersion', 'CorsairSessionDetails', 'CorsairSessionStateChanged',
    'CorsairDeviceInfo', 'CorsairLedPosition', 'CorsairDeviceFilter',
    'CorsairDeviceConnectionStatusChangedEvent', 'CorsairKeyEvent',
    'CorsairEvent', 'CorsairLedColor', 'CorsairKeyEventConfiguration',
    'CorsairProperty'
]


def bytes_to_str_or_default(bytes_arg, default=""):
    return default if not bytes_arg else bytes_arg.decode('utf-8')


@dataclass(frozen=True)
class CorsairVersion():
    major: int
    minor: int
    patch: int

    @staticmethod
    def create(nobj):
        return CorsairVersion(nobj.major, nobj.minor, nobj.patch)


@dataclass(frozen=True)
class CorsairSessionDetails():
    client_version: CorsairVersion
    server_version: CorsairVersion
    server_host_version: CorsairVersion

    @staticmethod
    def create(nobj):
        return CorsairSessionDetails(
            CorsairVersion.create(nobj.clientVersion),
            CorsairVersion.create(nobj.serverVersion),
            CorsairVersion.create(nobj.serverHostVersion))


@dataclass(frozen=True)
class CorsairSessionStateChanged():
    state: CorsairSessionState
    details: CorsairSessionDetails

    @staticmethod
    def create(nobj):
        return CorsairSessionStateChanged(
            CorsairSessionState(nobj.state),
            CorsairSessionDetails.create(nobj.details))


@dataclass(frozen=True)
class CorsairDeviceInfo():
    type: CorsairDeviceType
    device_id: str
    serial: str
    model: str
    led_count: int
    channel_count: int

    @staticmethod
    def create(nobj):
        return CorsairDeviceInfo(CorsairDeviceType(nobj.type),
                                 bytes_to_str_or_default(nobj.deviceId),
                                 bytes_to_str_or_default(nobj.serial),
                                 bytes_to_str_or_default(nobj.model),
                                 nobj.ledCount, nobj.channelCount)


@dataclass(frozen=True)
class CorsairLedPosition():
    id: int
    cx: float
    cy: float

    @staticmethod
    def create(nobj):
        return CorsairLedPosition(nobj.id, nobj.cx, nobj.cy)


@dataclass(frozen=True)
class CorsairDeviceFilter():
    device_type_mask: int

    @staticmethod
    def create(nobj):
        return CorsairDeviceFilter(nobj.deviceTypeMask)


@dataclass(frozen=True)
class CorsairDeviceConnectionStatusChangedEvent():
    device_id: str
    is_connected: bool

    @staticmethod
    def create(nobj):
        return CorsairDeviceConnectionStatusChangedEvent(
            bytes_to_str_or_default(nobj.deviceId), nobj.isConnected)


@dataclass(frozen=True)
class CorsairKeyEvent():
    device_id: str
    key_id: CorsairMacroKeyId
    is_pressed: bool

    @staticmethod
    def create(nobj):
        return CorsairKeyEvent(bytes_to_str_or_default(nobj.deviceId),
                               CorsairMacroKeyId(nobj.keyId), nobj.isPressed)


@dataclass(frozen=True)
class CorsairEvent():
    id: CorsairEventId
    data: Union[CorsairKeyEvent, CorsairDeviceConnectionStatusChangedEvent]

    @staticmethod
    def create(nobj):
        e = nobj
        id = CorsairEventId(e.id)
        if (id == CorsairEventId.CEI_DeviceConnectionStatusChangedEvent):
            return CorsairEvent(
                id,
                CorsairDeviceConnectionStatusChangedEvent.create(
                    e.deviceConnectionStatusChangedEvent[0]))
        elif (id == CorsairEventId.CEI_KeyEvent):
            return CorsairEvent(id, CorsairKeyEvent.create(e.keyEvent[0]))
        raise ValueError(f"Unknown event id={id}")


@dataclass
class CorsairLedColor():
    id: int
    r: int
    g: int
    b: int
    a: int

    @staticmethod
    def create(nobj):
        return CorsairLedColor(nobj.id, nobj.r, nobj.g, nobj.b, nobj.a)


@dataclass(frozen=True)
class CorsairKeyEventConfiguration():
    key_id: CorsairMacroKeyId
    is_intercepted: bool

    @staticmethod
    def create(nobj):
        return CorsairKeyEventConfiguration(CorsairMacroKeyId(nobj.keyId),
                                            nobj.isIntercepted)


@dataclass(frozen=True)
class CorsairProperty():
    type: CorsairDataType
    value: Union[bool, int, float, str, tuple]

    @staticmethod
    def create(nobj):
        t = CorsairDataType(nobj.type)
        if t == CorsairDataType.CT_Boolean:
            return CorsairProperty(t, nobj.value.boolean)
        if t == CorsairDataType.CT_Int32:
            return CorsairProperty(t, nobj.value.int32)
        if t == CorsairDataType.CT_Float64:
            return CorsairProperty(t, nobj.value.float64)
        if t == CorsairDataType.CT_String:
            return CorsairProperty(t, nobj.value.string)
        if t == CorsairDataType.CT_Boolean_Array:
            items = tuple(nobj.value.boolean_array.items[i]
                          for i in range(nobj.value.boolean_array.count))
            return CorsairProperty(t, items)
        if t == CorsairDataType.CT_Int32_Array:
            items = tuple(nobj.value.int32_array.items[i]
                          for i in range(nobj.value.int32_array.count))
            return CorsairProperty(t, items)
        if t == CorsairDataType.CT_Float64_Array:
            items = tuple(nobj.value.float64_array.items[i]
                          for i in range(nobj.value.float64_array.count))
            return CorsairProperty(t, items)
        if t == CorsairDataType.CT_String_Array:
            items = tuple(nobj.value.string_array.items[i]
                          for i in range(nobj.value.string_array.count))
            return CorsairProperty(t, items)
        raise ValueError(f"Unknown data type={t}")
