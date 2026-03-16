#!/usr/bin/env python3
import time
import serial
import random

INTERVAL = 1  # Seconds
port: str = "/dev/ttyACM1"
baud_rate: int = 115200

if __name__ == "__main__":
    try:
        with serial.Serial(port, baud_rate, timeout=1) as ser:
            print(f"Successfully opened serial port {port}.")
            while True:
                time.sleep(INTERVAL)

                total = random.randint(0, 100)
                ser.write(f"{total}\n".encode('utf-8'))
                print(f"Sent {total} to serial")

                # Check for incoming data
                # if ser.in_waiting > 0:
                #     line = ser.readline().decode('utf-8').rstrip()
                #     if line:
                #         print(f"Received from serial: {line}")

    except serial.SerialException as e:
        print(e)
        print(f"Error: Could not access serial port '{port}'.")
        exit(1)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
