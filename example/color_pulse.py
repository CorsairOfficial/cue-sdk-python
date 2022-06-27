import queue
import time
import threading

from cuesdk import CueSdk
from cuesdk.structs import CorsairLedColor


def read_keys(input_queue):
    while True:
        input_str = input()
        input_queue.put(input_str)


def get_available_leds():
    leds = list()
    device_count = sdk.get_device_count()

    for device_index in range(device_count):
        led_positions = sdk.get_led_positions_by_device_index(device_index)
        led_colors = list(
            [CorsairLedColor(led, 0, 0, 0) for led in led_positions.keys()])
        leds.append(led_colors)

    return leds


def perform_pulse_effect(wave_duration, all_leds):
    time_per_frame = 25
    x = 0
    cnt = len(all_leds)
    dx = time_per_frame / wave_duration

    while x < 2:
        val = int((1 - (x - 1)**2) * 255)
        for di in range(cnt):
            device_leds = all_leds[di]
            for led in device_leds:
                led.g = val

            sdk.set_led_colors_buffer_by_device_index(di, device_leds)

        sdk.set_led_colors_flush_buffer()
        time.sleep(time_per_frame / 1000)
        x += dx


def main():
    global sdk

    input_queue = queue.Queue()
    input_thread = threading.Thread(target=read_keys,
                                    args=(input_queue, ),
                                    daemon=True)
    input_thread.start()
    sdk = CueSdk()

    connected = sdk.connect()
    if not connected:
        err = sdk.get_last_error()
        print("Handshake failed: %s" % err)
        return

    wave_duration = 500
    colors = get_available_leds()
    if not colors:
        return

    print('Working... Use "+" or "-" to increase or decrease speed.\n'
          'Press "q" to close program...')

    while True:
        if input_queue.qsize() > 0:
            input_str = input_queue.get()

            if input_str.lower() == "q":
                print("Exiting.")
                break
            elif input_str == "+":
                if wave_duration > 100:
                    wave_duration -= 100
            elif input_str == "-":
                if wave_duration < 2000:
                    wave_duration += 100

        perform_pulse_effect(wave_duration, colors)

        time.sleep(0.01)


if __name__ == "__main__":
    main()
