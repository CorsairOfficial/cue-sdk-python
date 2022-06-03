from cuesdk import CueSdk
import sys


def br():
    print("—" * 80)


sdk = CueSdk()
if not sdk.connect():
    print(sdk.protocol_details)
    print("\nERROR: Unable to connect to iCUE")
    sys.exit()

print(sdk.protocol_details)
devices = sdk.get_devices()
COLS = ["Device type", "Model name", "LED count"]
COL_WIDTH = 26
br()
print("| ".join([f"{col:^{COL_WIDTH}}" for col in COLS]))
br()
print("\n".join([
    f"{str(d.type)[18:]:{COL_WIDTH}}|"
    f" {d.model:{COL_WIDTH}}|"
    f" {d.led_count}" for d in devices
]))
br()

for i, v in enumerate(devices):
    print(f"{str(v.type)[18:]}: {v.model} (leds: {v.led_count})")
    positions = sdk.get_led_positions_by_device_index(i)
    print("LEDS: [" + ", ".join([f"{str(p)[13:]}"
                                 for p in positions.keys()]) + "]")
    for chi, ch in enumerate(v.channels):
        print(f"CHANNEL {chi + 1} (total leds: {ch.total_led_count}): [" +
              ", ".join(
                  [f"{str(d.type)[25:]} * {d.led_count}"
                   for d in ch.devices]) + "]")
    br()
