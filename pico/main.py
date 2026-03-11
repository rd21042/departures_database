from machine import Pin, I2C
from time import sleep
from DIYables_MicroPython_OLED import OLED_SSD1306_I2C

i2c = I2C(0, scl=Pin(21), sda=Pin(20), freq=400000)
oled = OLED_SSD1306_I2C(128, 64, i2c)

oled.clear_display()
oled.display()
oled.set_text_size(2)

pin = Pin("LED", Pin.OUT)

while True:
    pin.toggle()
    sleep(1)
