import sys
import uselect
from machine import Pin, I2C
from time import sleep
import ssd1306

i2c = I2C(0, scl=Pin(1), sda=Pin(0))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
poll = uselect.poll()
poll.register(sys.stdin, uselect.POLLIN)

oled.fill(0)
oled.text("Ready", 0, 0)
oled.show()

while True:
    if poll.poll(0):
        line = sys.stdin.readline().strip()
        oled.fill(0)
        lines = line.split("\n")
        
        for i, row in enumerate(lines):
            oled.text(row, 0, i * 10)
            oled.show()
    
    sleep(0.1)
