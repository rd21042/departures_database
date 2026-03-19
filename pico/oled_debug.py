from machine import Pin, I2C
import ssd1306

i2c = I2C(0, scl=Pin(1), sda=Pin(0))
print(i2c.scan())
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
oled.fill(0)
oled.text("Debug", 0, 0)
oled.show()
