import math

class Color():
    def __init__(self, color, fmt='rgb'):
        self.__initialize__(color, fmt)

    def __initialize__(self, color, fmt='rgb'):
        if fmt == 'rgb':
            self.rgb = (int(color[0]), int(color[1]), int(color[2]))
            self.hex = self._rgb2hex(self.rgb)
            self.hsv = self._rgb2hsv(self.rgb)
            self.rgb0 = self.rgb[0] / 255, self.rgb[1] / 255, self.rgb[2] / 255
        elif fmt == 'rgb0':
            self.rgb = (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255))
            self.hex = self._rgb2hex(self.rgb)
            self.hsv = self._rgb2hsv(self.rgb)
            self.rgb0 = (color[0], color[1], color[2])
        elif fmt == 'hex':
            self.hex = color
            self.rgb = self._hex2rgb(self.hex)
            self.hsv = self._rgb2hsv(self.rgb)
            self.rgb0 = self.rgb[0] / 255, self.rgb[1] / 255, self.rgb[2] / 255
        elif fmt == 'hsv':
            self.hsv = color
            self.rgb = self._hsv2rgb(self.hsv)
            self.hex = self._rgb2hex(self.rgb)
            self.rgb0 = self.rgb[0] / 255, self.rgb[1] / 255, self.rgb[2] / 255
        self.__automaticPalette__()

    def __automaticPalette__(self):
        self.rgbColors = []
        self.hexColors = []
        self.hsvColors = []
        self.rgb0Colors = []
        hsv = self.hsv
        for i in range(255):
            new_hsv = hsv[0], hsv[1], (1 / 255) * i
            self.rgbColors.append(self._hsv2rgb(new_hsv))
            self.hexColors.append(self._rgb2hex(self.rgbColors[-1]))
            self.hsvColors.append(new_hsv)
            r, g, b = self.rgbColors[-1]
            self.rgb0Colors.append((r / 255, g / 255, b / 255))

    def _testPalette(self, o=1):
        from matplotlib import pyplot as plt
        from matplotlib.patches import Rectangle
        if o == 1:
            someX, someY = 0.5, 0.1
            plt.figure()
            s = 1
            currentAxis = plt.gca()
            for x in range(254):
                currentAxis.add_patch(Rectangle((x * s, someY), s, 0.1, alpha=1, color=self.rgb0Colors[x]))
            currentAxis.add_patch(Rectangle((5 * s, someY + 0.07), 30, 0.02, alpha=1, color=self.rgb0))

            plt.ylim(0.1, 0.2)
            plt.xlim(0, (x + 1) * s)
            plt.show()
        elif o == 2:
            local = self.rgb0Colors[90:190][0:-1:10]
            someX, someY = 0.5, 0.1
            plt.figure()
            s = 1
            currentAxis = plt.gca()
            for x in range(len(local)):
                currentAxis.add_patch(Rectangle((x * s, someY), s, 0.1, alpha=1, color=local[x]))
            currentAxis.add_patch(Rectangle((5 * s, someY + 0.07), 30, 0.02, alpha=1, color=self.rgb0))

            plt.ylim(0.1, 0.2)
            plt.xlim(0, (x + 1) * s)
            plt.show()

    def _hex2rgb(self, value):
        # http://stackoverflow.com/questions/214359/converting-hex-color-to-rgb-and-vice-versa
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + int(lv / 3)], 16) for i in range(0, lv, int(lv / 3)))

    def _rgb2hex(self, rgb):
        # http://stackoverflow.com/questions/214359/converting-hex-color-to-rgb-and-vice-versa
        r = rgb[0]
        g = rgb[1]
        b = rgb[2]
        return '#%02X%02X%02X' % (r, g, b)

    def _hsv2rgb(self, hsv):
        # http://code.activestate.com/recipes/576919-python-rgb-and-hsv-conversion/
        h, s, v = hsv
        h = float(h)
        s = float(s)
        v = float(v)
        h60 = h / 60.0
        h60f = math.floor(h60)
        hi = int(h60f) % 6
        f = h60 - h60f
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        r, g, b = 0, 0, 0
        if hi == 0:
            r, g, b = v, t, p
        elif hi == 1:
            r, g, b = q, v, p
        elif hi == 2:
            r, g, b = p, v, t
        elif hi == 3:
            r, g, b = p, q, v
        elif hi == 4:
            r, g, b = t, p, v
        elif hi == 5:
            r, g, b = v, p, q
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        return r, g, b

    def _rgb2hsv(self, rgb):
        # http://code.activestate.com/recipes/576919-python-rgb-and-hsv-conversion/
        r, g, b = rgb
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx - mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g - b) / df) + 360) % 360
        elif mx == g:
            h = (60 * ((b - r) / df) + 120) % 360
        elif mx == b:
            h = (60 * ((r - g) / df) + 240) % 360
        if mx == 0:
            s = 0
        else:
            s = df / mx
        v = mx
        return h, s, v

    def getColor(self, fmt='rgb'):
        if fmt == 'rgb':
            return self.rgb
        elif fmt == 'hex':
            return self.hex
        elif fmt == 'rgb0':
            return self.rgb0
        elif fmt == 'hsv':
            return self.hsv