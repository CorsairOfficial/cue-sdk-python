__all__ = [
    'CorsairError', 'CorsairSessionState', 'CorsairDeviceType',
    'CorsairEventId', 'CorsairDevicePropertyId', 'CorsairDataType',
    'CorsairPropertyFlag', 'CorsairPhysicalLayout', 'CorsairLogicalLayout',
    'CorsairChannelDeviceType', 'CorsairAccessLevel', 'CorsairLedGroup',
    'CorsairLedId_Keyboard', 'CorsairMacroKeyId'
]


class EnumerationType(type):

    def __new__(metacls, name, bases, namespace):
        if "_members_" not in namespace:
            _members_ = {
                k: v
                for k, v in namespace.items() if not k.startswith("_")
            }
            namespace["_members_"] = _members_
        else:
            _members_ = namespace["_members_"]

        namespace["_reverse_map_"] = {v: k for k, v in _members_.items()}
        return super().__new__(metacls, name, bases, namespace)

    def __repr__(self):
        return "<Enumeration %s>" % self.__name__


class Enumeration(metaclass=EnumerationType):

    def __init__(self, value):
        if value not in self._reverse_map_:
            raise ValueError("%d is not a valid value for %s" %
                             (value, type(self).__name__))
        self.value = value

    def __repr__(self):
        return "<%s: %d>" % (self.__str__(), self.value)

    def __str__(self):
        return "%s.%s" % (type(self).__name__,
                          self._reverse_map_.get(self.value, '(unknown)'))

    def __hash__(self):
        return self.value

    def __int__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, int):
            return self.value == other

        return type(self) == type(other) and self.value == other.value

    def __lt__(self, other):
        if isinstance(other, int):
            return self.value < other

        return type(self) == type(other) and self.value < other.value


class CorsairError(Enumeration):
    CE_Success = 0
    CE_NotConnected = 1
    CE_NoControl = 2
    CE_IncompatibleProtocol = 3
    CE_InvalidArguments = 4
    CE_InvalidOperation = 5
    CE_DeviceNotFound = 6
    CE_NotAllowed = 7


class CorsairSessionState(Enumeration):
    CSS_Invalid = 0
    CSS_Closed = 1
    CSS_Connecting = 2
    CSS_Timeout = 3
    CSS_ConnectionRefused = 4
    CSS_ConnectionLost = 5
    CSS_Connected = 6


class CorsairDeviceType(Enumeration):
    CDT_Unknown = 0x0000
    CDT_Keyboard = 0x0001
    CDT_Mouse = 0x0002
    CDT_Mousemat = 0x0004
    CDT_Headset = 0x0008
    CDT_HeadsetStand = 0x0010
    CDT_FanLedController = 0x0020
    CDT_LedController = 0x0040
    CDT_MemoryModule = 0x0080
    CDT_Cooler = 0x0100
    CDT_Motherboard = 0x0200
    CDT_GraphicsCard = 0x0400
    CDT_Touchbar = 0x0800
    CDT_GameController = 0x1000
    CDT_All = 0xFFFFFFFF


class CorsairEventId(Enumeration):
    CEI_Invalid = 0
    CEI_DeviceConnectionStatusChangedEvent = 1
    CEI_KeyEvent = 2


class CorsairDevicePropertyId(Enumeration):
    CDPI_Invalid = 0
    CDPI_PropertyArray = 1
    CDPI_MicEnabled = 2
    CDPI_SurroundSoundEnabled = 3
    CDPI_SidetoneEnabled = 4
    CDPI_EqualizerPreset = 5
    CDPI_PhysicalLayout = 6
    CDPI_LogicalLayout = 7
    CDPI_MacroKeyArray = 8
    CDPI_BatteryLevel = 9
    CDPI_ChannelLedCount = 10
    CDPI_ChannelDeviceCount = 11
    CDPI_ChannelDeviceLedCountArray = 12
    CDPI_ChannelDeviceTypeArray = 13


class CorsairDataType(Enumeration):
    CT_Boolean = 0
    CT_Int32 = 1
    CT_Float64 = 2
    CT_String = 3
    CT_Boolean_Array = 16
    CT_Int32_Array = 17
    CT_Float64_Array = 18
    CT_String_Array = 19


class CorsairPropertyFlag(Enumeration):
    CPF_None = 0x00
    CPF_CanRead = 0x01
    CPF_CanWrite = 0x02
    CPF_Indexed = 0x04


class CorsairPhysicalLayout(Enumeration):
    CPL_Invalid = 0
    CPL_US = 1
    CPL_UK = 2
    CPL_JP = 3
    CPL_KR = 4
    CPL_BR = 5


class CorsairLogicalLayout(Enumeration):
    CLL_Invalid = 0
    CLL_US_Int = 1
    CLL_NA = 2
    CLL_EU = 3
    CLL_UK = 4
    CLL_BE = 5
    CLL_BR = 6
    CLL_CH = 7
    CLL_CN = 8
    CLL_DE = 9
    CLL_ES = 10
    CLL_FR = 11
    CLL_IT = 12
    CLL_ND = 13
    CLL_RU = 14
    CLL_JP = 15
    CLL_KR = 16
    CLL_TW = 17
    CLL_MEX = 18


class CorsairChannelDeviceType(Enumeration):
    CCDT_Invalid = 0
    CCDT_HD_Fan = 1
    CCDT_SP_Fan = 2
    CCDT_LL_Fan = 3
    CCDT_ML_Fan = 4
    CCDT_QL_Fan = 5
    CCDT_8LedSeriesFan = 6
    CCDT_Strip = 7
    CCDT_DAP = 8
    CCDT_Pump = 9
    CCDT_DRAM = 10
    CCDT_WaterBlock = 11
    CCDT_QX_Fan = 12


class CorsairAccessLevel(Enumeration):
    CAL_Shared = 0
    CAL_ExclusiveLightingControl = 1
    CAL_ExclusiveKeyEventsListening = 2
    CAL_ExclusiveLightingControlAndKeyEventsListening = 3


class CorsairLedGroup(Enumeration):
    CLG_Keyboard = 0
    CLG_KeyboardGKeys = 1
    CLG_KeyboardEdge = 2
    CLG_KeyboardOem = 3
    CLG_Mouse = 4
    CLG_Mousemat = 5
    CLG_Headset = 6
    CLG_HeadsetStand = 7
    CLG_MemoryModule = 8
    CLG_Motherboard = 9
    CLG_GraphicsCard = 10
    CLG_DIY_Channel1 = 11
    CLG_DIY_Channel2 = 12
    CLG_DIY_Channel3 = 13
    CLG_Touchbar = 14
    CLG_GameController = 15


class CorsairLedId_Keyboard(Enumeration):
    CLK_Invalid = 0
    CLK_Escape = 1
    CLK_F1 = 2
    CLK_F2 = 3
    CLK_F3 = 4
    CLK_F4 = 5
    CLK_F5 = 6
    CLK_F6 = 7
    CLK_F7 = 8
    CLK_F8 = 9
    CLK_F9 = 10
    CLK_F10 = 11
    CLK_F11 = 12
    CLK_F12 = 13
    CLK_GraveAccentAndTilde = 14
    CLK_1 = 15
    CLK_2 = 16
    CLK_3 = 17
    CLK_4 = 18
    CLK_5 = 19
    CLK_6 = 20
    CLK_7 = 21
    CLK_8 = 22
    CLK_9 = 23
    CLK_0 = 24
    CLK_MinusAndUnderscore = 25
    CLK_EqualsAndPlus = 26
    CLK_Backspace = 27
    CLK_Tab = 28
    CLK_Q = 29
    CLK_W = 30
    CLK_E = 31
    CLK_R = 32
    CLK_T = 33
    CLK_Y = 34
    CLK_U = 35
    CLK_I = 36
    CLK_O = 37
    CLK_P = 38
    CLK_BracketLeft = 39
    CLK_BracketRight = 40
    CLK_CapsLock = 41
    CLK_A = 42
    CLK_S = 43
    CLK_D = 44
    CLK_F = 45
    CLK_G = 46
    CLK_H = 47
    CLK_J = 48
    CLK_K = 49
    CLK_L = 50
    CLK_SemicolonAndColon = 51
    CLK_ApostropheAndDoubleQuote = 52
    CLK_Backslash = 53
    CLK_Enter = 54
    CLK_LeftShift = 55
    CLK_NonUsBackslash = 56
    CLK_Z = 57
    CLK_X = 58
    CLK_C = 59
    CLK_V = 60
    CLK_B = 61
    CLK_N = 62
    CLK_M = 63
    CLK_CommaAndLessThan = 64
    CLK_PeriodAndBiggerThan = 65
    CLK_SlashAndQuestionMark = 66
    CLK_RightShift = 67
    CLK_LeftCtrl = 68
    CLK_LeftGui = 69
    CLK_LeftAlt = 70
    CLK_Space = 71
    CLK_RightAlt = 72
    CLK_RightGui = 73
    CLK_Application = 74
    CLK_RightCtrl = 75
    CLK_LedProgramming = 76
    CLK_Lang1 = 77
    CLK_Lang2 = 78
    CLK_International1 = 79
    CLK_International2 = 80
    CLK_International3 = 81
    CLK_International4 = 82
    CLK_International5 = 83
    CLK_PrintScreen = 84
    CLK_ScrollLock = 85
    CLK_PauseBreak = 86
    CLK_Insert = 87
    CLK_Home = 88
    CLK_PageUp = 89
    CLK_Delete = 90
    CLK_End = 91
    CLK_PageDown = 92
    CLK_UpArrow = 93
    CLK_LeftArrow = 94
    CLK_DownArrow = 95
    CLK_RightArrow = 96
    CLK_NonUsTilde = 97
    CLK_Brightness = 98
    CLK_WinLock = 99
    CLK_Mute = 100
    CLK_Stop = 101
    CLK_ScanPreviousTrack = 102
    CLK_PlayPause = 103
    CLK_ScanNextTrack = 104
    CLK_NumLock = 105
    CLK_KeypadSlash = 106
    CLK_KeypadAsterisk = 107
    CLK_KeypadMinus = 108
    CLK_Keypad7 = 109
    CLK_Keypad8 = 110
    CLK_Keypad9 = 111
    CLK_KeypadPlus = 112
    CLK_Keypad4 = 113
    CLK_Keypad5 = 114
    CLK_Keypad6 = 115
    CLK_Keypad1 = 116
    CLK_Keypad2 = 117
    CLK_Keypad3 = 118
    CLK_KeypadComma = 119
    CLK_KeypadEnter = 120
    CLK_Keypad0 = 121
    CLK_KeypadPeriodAndDelete = 122
    CLK_VolumeUp = 123
    CLK_VolumeDown = 124
    CLK_MR = 125
    CLK_M1 = 126
    CLK_M2 = 127
    CLK_M3 = 128
    CLK_Fn = 129


class CorsairMacroKeyId(Enumeration):
    CMKI_Invalid = 0
    CMKI_1 = 1
    CMKI_2 = 2
    CMKI_3 = 3
    CMKI_4 = 4
    CMKI_5 = 5
    CMKI_6 = 6
    CMKI_7 = 7
    CMKI_8 = 8
    CMKI_9 = 9
    CMKI_10 = 10
    CMKI_11 = 11
    CMKI_12 = 12
    CMKI_13 = 13
    CMKI_14 = 14
    CMKI_15 = 15
    CMKI_16 = 16
    CMKI_17 = 17
    CMKI_18 = 18
    CMKI_19 = 19
    CMKI_20 = 20
