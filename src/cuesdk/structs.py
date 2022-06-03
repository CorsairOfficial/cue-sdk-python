from dataclasses import dataclass
from collections.abc import Mapping
from typing import Tuple, Union
from .enums import (CorsairEventId, CorsairKeyId, CorsairLedId,
                    CorsairDeviceType, CorsairChannelDeviceType,
                    CorsairPhysicalLayout, CorsairLogicalLayout)

__all__ = [
    'CorsairProtocolDetails', 'CorsairChannelDeviceInfo', 'CorsairChannelInfo',
    'CorsairDeviceInfo', 'CorsairLedPosition', 'CorsairLedPositions',
    'CorsairLedColor', 'CorsairEvent', 'CorsairKeyEvent',
    'CorsairDeviceConnectionStatusChangedEvent'
]


def bytes_to_str_or_default(bytes_arg, default=""):
    return default if not bytes_arg else bytes_arg.decode('utf-8')


@dataclass(frozen=True)
class CorsairProtocolDetails():
    sdk_version: str
    server_version: str
    sdk_protocol_version: int
    server_protocol_version: int
    breaking_changes: bool

    @staticmethod
    def create(nobj):
        return CorsairProtocolDetails(
            bytes_to_str_or_default(nobj.sdkVersion),
            bytes_to_str_or_default(nobj.serverVersion),
            nobj.sdkProtocolVersion, nobj.serverProtocolVersion,
            nobj.breakingChanges)


@dataclass(frozen=True)
class CorsairChannelDeviceInfo():
    type: CorsairChannelDeviceType
    led_count: int

    @staticmethod
    def create(nobj):
        return CorsairChannelDeviceInfo(nobj.type, nobj.deviceLedCount)


@dataclass(frozen=True)
class CorsairChannelInfo():
    total_led_count: int
    devices: list[CorsairChannelDeviceInfo]

    @staticmethod
    def create(nobj):
        devices = [
            CorsairChannelDeviceInfo.create(nobj.devices[i])
            for i in range(nobj.devicesCount)
        ]
        return CorsairChannelInfo(nobj.totalLedsCount, devices)


@dataclass(frozen=True)
class CorsairDeviceInfo():
    id: str
    type: CorsairDeviceType
    model: str
    physical_layout: CorsairPhysicalLayout
    logical_layout: CorsairLogicalLayout
    caps_mask: int
    led_count: int
    channels: list[CorsairChannelInfo]

    @staticmethod
    def create(nobj):
        s = nobj.contents
        channels = [
            CorsairChannelInfo.create(s.channels.channels[chi])
            for chi in range(s.channels.channelsCount)
        ]

        return CorsairDeviceInfo(bytes_to_str_or_default(s.deviceId), s.type,
                                 bytes_to_str_or_default(s.model),
                                 s.physicalLayout, s.logicalLayout, s.capsMask,
                                 s.ledsCount, channels)


@dataclass(frozen=True)
class CorsairLedPosition():
    led_id: CorsairLedId
    top: float
    left: float
    height: float
    width: float

    @staticmethod
    def create(nobj):
        return CorsairLedPosition(nobj.ledId, nobj.top, nobj.left, nobj.height,
                                  nobj.width)


class CorsairLedPositions(Mapping):

    def __init__(self, items=None) -> None:
        self._items = dict(items) if items is not None else dict()

    def __repr__(self) -> str:
        return "{type}({arg})".format(
            type=type(self).__name__,
            arg=repr(self._items) if self._items else "")

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, led_id: CorsairLedId) -> Tuple[float, float]:
        return self._items[led_id]

    def __iter__(self):
        return iter(self._items)

    def create(nobj):
        positions = dict()
        for i in range(nobj.contents.numberOfLed):
            p = CorsairLedPosition.create(nobj.contents.pLedPosition[i])
            positions[p.led_id] = (p.left, p.top)
        return CorsairLedPositions(positions)


@dataclass
class CorsairLedColor():
    led_id: CorsairLedId
    r: int
    g: int
    b: int

    @staticmethod
    def create(nobj):
        return CorsairLedColor(nobj.ledId, nobj.r, nobj.g, nobj.b)


@dataclass(frozen=True)
class CorsairDeviceConnectionStatusChangedEvent():
    device_id: str
    is_connected: bool

    @staticmethod
    def create(nobj):
        return CorsairDeviceConnectionStatusChangedEvent(
            nobj.deviceId.decode(), nobj.isConnected)


@dataclass(frozen=True)
class CorsairKeyEvent():
    device_id: str
    key_id: CorsairKeyId
    is_pressed: bool

    @staticmethod
    def create(nobj):
        return CorsairKeyEvent(nobj.deviceId.decode(), nobj.keyId,
                               nobj.isPressed)


@dataclass(frozen=True)
class CorsairEvent():
    id: str
    data: Union[CorsairKeyEvent, CorsairDeviceConnectionStatusChangedEvent]

    @staticmethod
    def create(nobj):
        e = nobj[0]
        if (e.id == CorsairEventId.DeviceConnectionStatusChangedEvent):
            return CorsairEvent(
                e.id,
                CorsairDeviceConnectionStatusChangedEvent.create(
                    e.deviceConnectionStatusChangedEvent[0]))
        elif (e.id == CorsairEventId.KeyEvent):
            return CorsairEvent(e.id, CorsairKeyEvent.create(e.keyEvent[0]))
        raise ValueError("Unknown event id={id}".format(id=e.id))
