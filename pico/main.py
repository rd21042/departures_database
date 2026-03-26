import sys
import uselect
from machine import Pin, I2C
from time import sleep
import ssd1306

# OLED setup
i2c = I2C(0, scl=Pin(1), sda=Pin(0))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)

buffer = []

oled.fill(0)
oled.text("Ready", 0, 0)
oled.show()

while True:
    if poll.poll(10):
        line = sys.stdin.readline().strip()

        if line:
            buffer.append(line)
            buffer = buffer[-4:] # Keep last 4 lines (OLED height limit)

            oled.fill(0)

            for i, row in enumerate(buffer):
                oled.text(row[:16], 0, i * 10)  # limit width to 16 chars

            oled.show()

    sleep(50 / 1000) # 50 ms delay to prevent overloading Pico
