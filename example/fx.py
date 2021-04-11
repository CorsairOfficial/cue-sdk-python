
from colorsys import hsv_to_rgb
from functools import reduce
import math
import operator
import queue
import time
import threading

from cuesdk import CueSdk
from cuesdk.helpers import ColorRgb


def swirls2(env, px, py):
    """
    Source https://www.shadertoy.com/view/4dX3Rf
    """
    t = env.time
    x = px - (env.resolution.x / 2)
    y = py - (env.resolution.y / 2)
    r = math.sqrt(x**2 + y**2)
    angle = math.atan2(x, y) - math.sin(t) * r / 200 + t
    intensity = 0.5 + 0.25 * math.sin(15 * angle)

    return hsv_to_rgb(angle / math.pi, intensity, 1)


def gradient(env, px, py):
    x = px / env.resolution.x
    y = py / env.resolution.y
    return (x, y, 0)


def rainbow45(env, px, py):
    uvx = px / env.resolution.x
    uvy = py / env.resolution.y
    direction = math.radians(45)
    xr = uvx * math.cos(direction) - uvy * math.sin(direction)
    vec = [0.0, 0.66, 0.33]
    rgb = [(math.sin(-8 * env.time + (xr + v) * math.pi * 2) * 0.5 + 0.5)
           for v in vec]
    return rgb


class Resolution:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class FxEnv:
    def __init__(self, resolution, time=0):
        self.resolution = resolution
        self.time = time


class DeviceFrame:
    def __init__(self, leds):
        self.leds = leds.copy()
        if leds:
            max_by_x, max_by_y = reduce(
                lambda acc, pt: (max(acc[0], pt[0]), max(acc[1], pt[1])),
                leds.values(), (float('-inf'), float('-inf')))
            self.env = FxEnv(Resolution(max_by_x, max_by_y))
            self.colors = dict.fromkeys(leds, (0, 0, 0))
            self.empty = False
        else:
            self.empty = True

    def update(self, frame_time, fx):
        if self.empty:
            return

        self.env.time = frame_time
        for key in self.colors:
            self.colors[key] = ColorRgb.from_vec3(
                *fx(self.env,
                    self.leds[key][0],
                    self.leds[key][1])).rgb


def read_keys(input_queue):
    while True:
        input_str = input()
        input_queue.put(input_str)


def main():
    sdk = CueSdk()
    connected = sdk.connect()
    if not connected:
        err = sdk.get_last_error()
        print("Handshake failed: %s" % err)
        return

    frames = list()
    device_count = sdk.get_device_count()
    for device_index in range(device_count):
        led_positions = sdk.get_led_positions_by_device_index(device_index)
        frames.append(DeviceFrame(led_positions))

    if not frames:
        return

    # List of effects.
    fxs = [gradient, rainbow45, swirls2]
    fxi = 0

    input_queue = queue.Queue()
    input_thread = threading.Thread(target=read_keys,
                                    args=(input_queue, ),
                                    daemon=True)
    input_thread.start()

    print('Working...\nPress "q" to close program\n'
          "Press any other key to switch between effects")

    while True:
        if input_queue.qsize() > 0:
            input_str = input_queue.get()

            if input_str.lower() == "q":
                print("Exiting.")
                break
            else:
                fxi = (fxi + 1) % len(fxs)
                print("Switching to %s" % fxs[fxi].__name__)

        frame_time = time.time()
        for di in range(device_count):
            frame = frames[di]

            if not frame.empty:
                frame.update(frame_time, fxs[fxi])
                sdk.set_led_colors_buffer_by_device_index(di, frame.colors)

        sdk.set_led_colors_flush_buffer()


if __name__ == "__main__":
    main()
