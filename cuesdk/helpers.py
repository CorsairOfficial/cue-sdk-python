__all__ = ['ColorRgb']


class ColorRgb(object):
    def __init__(self, r: int = 0, g: int = 0, b: int = 0):
        def validate(c):
            if not 0 <= c <= 255:
                raise ValueError("The argument must be between 0 and 255.")
            return int(c)

        self.r = validate(r)
        self.g = validate(g)
        self.b = validate(b)

    @property
    def rgb(self):
        return (self.r, self.g, self.b)

    @property
    def hex(self):
        return "0x%06x" % (((self.r & 0xff) << 16) | ((self.g & 0xff) << 8) |
                           (self.b & 0xff))

    @staticmethod
    def _denorm_(fnum):
        return 255 * max(min(fnum, 1), 0)

    @classmethod
    def from_vec3(cls, *v3):
        dn = cls._denorm_
        col = (dn(c) for c in v3)
        return cls(*col)

    @classmethod
    def from_hexstr(cls, hexstr: str):
        val = hexstr.lstrip('#').lower().replace('0x', '').rjust(6, '0')
        return cls(*(int(val[i:i + 2], 16) for i in (0, 2, 4)))

    def __str__(self):
        return self.hex

    def __repr__(self):
        return "ColorRgb(%d, %d, %d)" % self.rgb

    def __iter__(self):
        return iter(self.rgb)
