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

    sleep(20 / 1000) # 20 ms delay to prevent overloading Pico
