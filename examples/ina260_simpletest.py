import time
import board
import adafruit_ina260

i2c = board.I2C()
ina260 = adafruit_ina260.INA260(i2c)
while True:
    print("Current: %.2f Voltage: %.2f Power:%.2f"
          %(ina260.current, ina260.voltage, ina260.power))
    time.sleep(1)
