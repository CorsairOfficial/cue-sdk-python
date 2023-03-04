from cuesdk import (CueSdk, CorsairDeviceFilter, CorsairDeviceType,
                    CorsairError, CorsairSessionState, CorsairDeviceInfo)
import sys

COLS = ["Device type", "Model name", "LED count", "Channel count"]
COL_WIDTH = 28


def hr():
    print("—" * COL_WIDTH * len(COLS))


def print_device(device: CorsairDeviceInfo):
    print(f"{str(device.type)[18:]:{COL_WIDTH-2}} |"
          f" {device.model:{COL_WIDTH-3}} |"
          f" {device.led_count:{COL_WIDTH-3}} |"
          f" {device.channel_count:{COL_WIDTH-2}}")


def main():
    sdk = CueSdk()

    def on_state_changed(evt):
        print(evt.state)
        # the app must wait for CSS_Connected event before proceeding
        if evt.state == CorsairSessionState.CSS_Connected:
            details, err = sdk.get_session_details()
            print(details)

            devices, err = sdk.get_devices(
                CorsairDeviceFilter(
                    device_type_mask=CorsairDeviceType.CDT_All))
            if err == CorsairError.CE_Success and devices:
                hr()
                print("|".join([f"{col:^{COL_WIDTH-1}}" for col in COLS]))
                hr()
                for d in devices:
                    device, err = sdk.get_device_info(d.device_id)
                    if device:
                        print_device(device)
                hr()
            else:
                print(err)

    err = sdk.connect(on_state_changed)
    if err != CorsairError.CE_Success:
        print("\nERROR: Unable to connect to iCUE")
        print(err)
        sys.exit()


if __name__ == "__main__":
    main()
    input()  # wait for <Enter>
