#!/usr/bin/env python3
import time
import serial

INTERVAL = .25  # Seconds
MONITORED_DISKS = ["sda", "nvme0n1"]
port: str = "/dev/ttyACM1"
baud_rate: int = 115200


def parse_diskstats():
    diskstats = {}
    fields = [
        "major", "minor", "device",
        "reads_completed", "reads_merged", "sectors_read", "time_reading_ms",
        "writes_completed", "writes_merged", "sectors_written", "time_writing_ms",
        "ios_in_progress", "time_doing_ios_ms", "weighted_time_ios_ms"
    ]

    with open("/proc/diskstats", "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 14:
                continue  # Not enough data

            device = parts[2]
            metrics = {field: int(value) if field != "device" else value
                       for field, value in zip(fields, parts[:14])}
            diskstats[device] = metrics

    return diskstats


def get_total_activity(prev, curr):
    reads = 0
    writes = 0
    for dev in curr:
        if dev not in prev or dev not in MONITORED_DISKS:
            continue
        delta_read = curr[dev]['sectors_read'] - prev[dev]['sectors_read']
        delta_write = curr[dev]['sectors_written'] - prev[dev]['sectors_written']
        reads = reads + delta_read
        writes = writes + delta_write

    return reads, writes


if __name__ == "__main__":
    print("Monitoring disk I/O every 1 second...\n")
    prev_stats = parse_diskstats()

    try:
        with serial.Serial(port, baud_rate, timeout=1) as ser:
            print(f"Successfully opened serial port {port}.")
            while True:
                curr_stats = parse_diskstats()
                reads, writes = get_total_activity(prev_stats, curr_stats)

                total_sectors = reads + writes/10
                num_chars = int((total_sectors / 50000) * 20)
                num_chars = min(num_chars, 20)

                print(f"Sectors Read: {reads}, Sectors Written: {writes}, Chars sent: {num_chars}")
                prev_stats = curr_stats

                if num_chars > 0:
                    delay = INTERVAL / num_chars
                    for _ in range(num_chars):
                        ser.write(f"c\n".encode('utf-8'))
                        time.sleep(delay)
                else:
                    time.sleep(INTERVAL)

            # Check for incoming data
                # if ser.in_waiting > 0:
                #     line = ser.readline().decode('utf-8').rstrip()

    except serial.SerialException as e:
        print(e)
        print(f"Error: Could not access serial port '{port}'.")
        exit(1)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")