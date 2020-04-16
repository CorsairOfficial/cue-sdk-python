from cuesdk import CueSdk
import threading
import queue
import time


def read_keys(inputQueue):
    while (True):
        input_str = input()
        inputQueue.put(input_str)


def get_available_leds():
    leds = list()
    device_count = sdk.get_device_count()
    for device_index in range(device_count):
        led_positions = sdk.get_led_positions_by_device_index(device_index)
        leds.append(led_positions)
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
                device_leds[led] = (0, val, 0)  # green
            sdk.set_led_colors_buffer_by_device_index(di, device_leds)
        sdk.set_led_colors_flush_buffer()
        time.sleep(time_per_frame / 1000)
        x += dx


def main():
    global sdk
    inputQueue = queue.Queue()

    inputThread = threading.Thread(target=read_keys,
                                   args=(inputQueue, ),
                                   daemon=True)
    inputThread.start()
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

    print("Working... Use \"+\" or \"-\" to increase or decrease speed.\n" +
          "Press \"q\" to close program...")
    while (True):
        if (inputQueue.qsize() > 0):
            input_str = inputQueue.get()

            if input_str == "q" or input_str == "Q":
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
