import sys
import uselect
from machine import Pin, I2C, ADC
from time import sleep
import ssd1306

# OLED setup
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# Joystick setup
joystick_x_value = ADC(27)
joystick_y_value = ADC(26)

# Serial setup
poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)

# OLED Screen Setup
oled.fill(0)
oled.text("Ready", 0, 0)
oled.show()

buffer = []

while True:
    if poll.poll(10):
        line = sys.stdin.readline().strip()
        buffer.append(line)

        if len(buffer) == 8:
            oled.fill(0)
            for i, line in enumerate(buffer):
                oled.text(line, 0, i * 8)
            oled.show()
            buffer = []

        print(joystick_x_value.read_u16())

    sleep(0.02) # 20 ms delay to prevent overloading Pico
