from cuesdk import CueSdk, CorsairEventId


def sdk_event_handler(event_id, data):
    print("Event: %s" % event_id)
    if (event_id == CorsairEventId.KeyEvent):
        print(" Device id: %s\n    Key id: %s\n Key state: %s" %
              (data.deviceId.decode(), data.keyId,
               "pressed" if data.isPressed else "released"))
    elif (event_id == CorsairEventId.DeviceConnectionStatusChangedEvent):
        print(" Device id: %s\n    Status: %s" %
              (data.deviceId.decode(),
               "connected" if data.isConnected else "disconnected"))
    else:
        print("Invalid event!")


def main():
    sdk = CueSdk()
    connected = sdk.connect()
    if not connected:
        err = sdk.get_last_error()
        print("Handshake failed: %s" % err)
        return

    subscribed = sdk.subscribe_for_events(sdk_event_handler)
    if not subscribed:
        err = sdk.get_last_error()
        print("Subscribe for events error: %s" % err)
        return

    print("Working... Press any G/M key or connect/disconnect Corsair device"
          " to see events in action\n")
    print("Press 'q' to close program...")

    while True:
        input_str = input()
        if input_str.lower() == "q":
            print("Exiting.")
            break

    sdk.unsubscribe_from_events()


if __name__ == "__main__":
    main()
