import time
import board
import pwmio
import usb_cdc
import digitalio

MAX_BRIGHTNESS_VALUE = 20

BUZZER_PIN = board.GP18
BUZZER_2_PIN = board.GP9
POWER_PIN = board.GP28
VOLUME_PWM_PIN = board.GP25
LED_PIN = board.GP12

power = digitalio.DigitalInOut(POWER_PIN)
power.direction = digitalio.Direction.OUTPUT
power.value = False

buzzer = digitalio.DigitalInOut(BUZZER_PIN)
buzzer.direction = digitalio.Direction.OUTPUT
buzzer.value = False

buzzer2 = digitalio.DigitalInOut(BUZZER_2_PIN)
buzzer2.direction = digitalio.Direction.OUTPUT
buzzer2.value = False

vol = pwmio.PWMOut(VOLUME_PWM_PIN, frequency=10000, duty_cycle=18000)
led = pwmio.PWMOut(LED_PIN, frequency=5000, duty_cycle=0)

def blink_led(led, times=100, duration_seconds=10):
    on_off_cycles = times * 2
    sleep_interval = duration_seconds / on_off_cycles

    for _ in range(times):
        # Turn LED on (nearly full brightness)
        led.duty_cycle = 30000
        time.sleep(sleep_interval)

        # Turn LED off
        led.duty_cycle = 0
        time.sleep(sleep_interval)

print("Booting...")
blink_led(led, 100, 1)
led.duty_cycle = 0
time.sleep(1)
led.duty_cycle = 65535
print("Booting... done")


def set_rate(rate):
    for _ in range(int(1 / (0.011 + 1 / rate))):
        led.duty_cycle = 65535
        buzzer.value = True
        time.sleep(0.00001)
        buzzer2.value = True
        time.sleep(0.01)
        buzzer.value = False
        buzzer2.value = False
        led.duty_cycle = 0
        time.sleep(float(1 / rate))

def test():
    power.value = True

    for i in range(1, 10):
        set_rate(i)

    set_rate(20)

    power.value = False

# test()


def click():
    led.duty_cycle = 65535
    buzzer.value = True
    time.sleep(0.00001)
    buzzer2.value = True
    time.sleep(0.01)
    buzzer.value = False
    buzzer2.value = False
    led.duty_cycle = 0

console = usb_cdc.data
console.write(b"sec_unit_boot_ok\n")

while True:
    if console.in_waiting > 0:
        data = console.readline()
        print(data)
        if data:
            try:
                power.value = True
                time.sleep(0.01)
                click()
                power.value = False

            except (ValueError, UnicodeDecodeError):
                # Handle cases where the input is not a valid number
                console.write(b"Invalid input. Please enter a number between 0 and 100.\n")

    # A small delay to prevent the loop from running too fast
    time.sleep(0.01)
