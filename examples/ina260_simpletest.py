# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

import time

import board

import adafruit_ina260

i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
ina260 = adafruit_ina260.INA260(i2c)
while True:
    print(
        f"Current: {ina260.current:.2f} mA Voltage: {ina260.voltage:.2f} V Power:{ina260.power:.2f} mW"  # noqa: E501
    )
    time.sleep(1)
