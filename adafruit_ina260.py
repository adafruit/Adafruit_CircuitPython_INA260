# SPDX-FileCopyrightText: Bryan Siepert 2019 for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`adafruit_ina260`
================================================================================
CircuitPython driver for the TI INA260 current and power sensor
* Author(s): Bryan Siepert
Implementation Notes
--------------------
**Hardware:**
* `INA260 Breakout <https://www.adafruit.com/products/4226>`_
**Software and Dependencies:**
* Adafruit CircuitPython firmware for the supported boards:
* https://github.com/adafruit/circuitpython/releases
* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
* Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

# imports

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_INA260.git"

from micropython import const
import adafruit_bus_device.i2c_device as i2cdevice

from adafruit_register.i2c_struct import ROUnaryStruct
from adafruit_register.i2c_bits import ROBits, RWBits
from adafruit_register.i2c_bit import ROBit, RWBit

_REG_CONFIG = const(0x00)  # CONFIGURATION REGISTER (R/W)
_REG_CURRENT = const(0x01)  # SHUNT VOLTAGE REGISTER (R)
_REG_BUSVOLTAGE = const(0x02)  # BUS VOLTAGE REGISTER (R)
_REG_POWER = const(0x03)  # POWER REGISTER (R)
_REG_MASK_ENABLE = const(0x06)  # MASK ENABLE REGISTER (R/W)
_REG_ALERT_LIMIT = const(0x07)  # ALERT LIMIT REGISTER (R/W)
_REG_MFG_UID = const(0xFE)  # MANUFACTURER UNIQUE ID REGISTER (R)
_REG_DIE_UID = const(0xFF)  # DIE UNIQUE ID REGISTER (R)


# pylint: disable=too-few-public-methods
class Mode:
    """Modes avaible to be set

    +--------------------+---------------------------------------------------------------------+
    | Mode               | Description                                                         |
    +====================+=====================================================================+
    | ``Mode.CONTINUOUS``| Default: The sensor will continuously measure the bus voltage and   |
    |                    | shunt voltage across the shunt resistor to calculate ``power`` and  |
    |                    | ``current``                                                         |
    +--------------------+---------------------------------------------------------------------+
    | ``Mode.TRIGGERED`` | The sensor will immediately begin measuring and calculating current,|
    |                    | bus voltage, and power. Re-set this mode to initiate another        |
    |                    | measurement                                                         |
    +--------------------+---------------------------------------------------------------------+
    | ``Mode.SHUTDOWN``  |  Shutdown the sensor, reducing the quiescent current and turning off|
    |                    |  current into the device inputs. Set another mode to re-enable      |
    +--------------------+---------------------------------------------------------------------+

    """

    SHUTDOWN = const(0x0)
    TRIGGERED = const(0x3)
    CONTINUOUS = const(0x7)


class ConversionTime:
    """Options for ``current_conversion_time`` or ``voltage_conversion_time``

    +----------------------------------+------------------+
    | ``ConversionTime``               | Time             |
    +==================================+==================+
    | ``ConversionTime.TIME_140_us``   | 140 us           |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_204_us``   | 204 us           |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_332_us``   | 332 us           |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_558_us``   | 588 us           |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_1_1_ms``   | 1.1 ms (Default) |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_2_116_ms`` | 2.116 ms         |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_4_156_ms`` | 4.156 ms         |
    +----------------------------------+------------------+
    | ``ConversionTime.TIME_8_244_ms`` | 8.244 ms         |
    +----------------------------------+------------------+

    """

    TIME_140_us = const(0x0)
    TIME_204_us = const(0x1)
    TIME_332_us = const(0x2)
    TIME_558_us = const(0x3)
    TIME_1_1_ms = const(0x4)
    TIME_2_116_ms = const(0x5)
    TIME_4_156_ms = const(0x6)
    TIME_8_244_ms = const(0x7)

    @staticmethod
    def get_seconds(time_enum):
        """Retrieve the time in seconds giving value read from register"""
        conv_dict = {
            0: 140e-6,
            1: 204e-6,
            2: 332e-6,
            3: 558e-6,
            4: 1.1e-3,
            5: 2.116e-3,
            6: 4.156e-3,
            7: 8.244e-3,
        }
        return conv_dict[time_enum]


class AveragingCount:
    """Options for ``averaging_count``

    +-------------------------------+------------------------------------+
    | ``AveragingCount``            | Number of measurements to average  |
    +===============================+====================================+
    | ``AveragingCount.COUNT_1``    | 1 (Default)                        |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_4``    | 4                                  |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_16``   | 16                                 |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_64``   | 64                                 |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_128``  | 128                                |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_256``  | 256                                |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_512``  | 512                                |
    +-------------------------------+------------------------------------+
    | ``AveragingCount.COUNT_1024`` | 1024                               |
    +-------------------------------+------------------------------------+

    """

    COUNT_1 = const(0x0)
    COUNT_4 = const(0x1)
    COUNT_16 = const(0x2)
    COUNT_64 = const(0x3)
    COUNT_128 = const(0x4)
    COUNT_256 = const(0x5)
    COUNT_512 = const(0x6)
    COUNT_1024 = const(0x7)

    @staticmethod
    def get_averaging_count(avg_count):
        """Retrieve the number of measurements giving value read from register"""
        conv_dict = {0: 1, 1: 4, 2: 16, 3: 64, 4: 128, 5: 256, 6: 512, 7: 1024}
        return conv_dict[avg_count]


# pylint: enable=too-few-public-methods


class INA260:
    """Driver for the INA260 power and current sensor.

    :param ~busio.I2C i2c_bus: The I2C bus the INA260 is connected to.
    :param address: The I2C device address for the sensor. Default is ``0x40``.

    """

    def __init__(self, i2c_bus, address=0x40):
        self.i2c_device = i2cdevice.I2CDevice(i2c_bus, address)

        if self._manufacturer_id != self.TEXAS_INSTRUMENT_ID:
            raise RuntimeError(
                "Failed to find Texas Instrument ID, read {} while expected {}"
                " - check your wiring!".format(
                    self._manufacturer_id, self.TEXAS_INSTRUMENT_ID
                )
            )

        if self._device_id != self.INA260_ID:
            raise RuntimeError(
                "Failed to find INA260 ID, read {} while expected {}"
                " - check your wiring!".format(self._device_id, self.INA260_ID)
            )

    _raw_current = ROUnaryStruct(_REG_CURRENT, ">h")
    _raw_voltage = ROUnaryStruct(_REG_BUSVOLTAGE, ">H")
    _raw_power = ROUnaryStruct(_REG_POWER, ">H")

    # MASK_ENABLE fields
    overcurrent_limit = RWBit(_REG_MASK_ENABLE, 15, 2, False)
    """Setting this bit high configures the ALERT pin to be asserted if the current measurement
       following a conversion exceeds the value programmed in the Alert Limit Register.
    """
    under_current_limit = RWBit(_REG_MASK_ENABLE, 14, 2, False)
    """Setting this bit high configures the ALERT pin to be asserted if the current measurement
       following a conversion drops below the value programmed in the Alert Limit Register.
    """
    bus_voltage_over_voltage = RWBit(_REG_MASK_ENABLE, 13, 2, False)
    """Setting this bit high configures the ALERT pin to be asserted if the bus voltage measurement
       following a conversion exceeds the value programmed in the Alert Limit Register.
    """
    bus_voltage_under_voltage = RWBit(_REG_MASK_ENABLE, 12, 2, False)
    """Setting this bit high configures the ALERT pin to be asserted if the bus voltage measurement
       following a conversion drops below the value programmed in the Alert Limit Register.
    """
    power_over_limit = RWBit(_REG_MASK_ENABLE, 11, 2, False)
    """Setting this bit high configures the ALERT pin to be asserted if the Power calculation
       made following a bus voltage measurement exceeds the value programmed in the
       Alert Limit Register.
    """
    conversion_ready = RWBit(_REG_MASK_ENABLE, 10, 2, False)
    """Setting this bit high configures the ALERT pin to be asserted when the Conversion Ready Flag,
        Bit 3, is asserted indicating that the device is ready for the next conversion.
    """
    # from 5 to 9 are not used
    alert_function_flag = ROBit(_REG_MASK_ENABLE, 4, 2, False)
    """While only one Alert Function can be monitored at the ALERT pin at time, the
       Conversion Ready can also be enabled to assert the ALERT pin.
       Reading the Alert Function Flag following an alert allows the user to determine if the Alert
       Function was the source of the Alert.

       When the Alert Latch Enable bit is set to Latch mode, the Alert Function Flag bit
       clears only when the Mask/Enable Register is read.
       When the Alert Latch Enable bit is set to Transparent mode, the Alert Function Flag bit
       is cleared following the next conversion that does not result in an Alert condition.
    """
    _conversion_ready_flag = ROBit(_REG_MASK_ENABLE, 3, 2, False)
    """Bit to help coordinate one-shot or triggered conversion. This bit is set after all
        conversion, averaging, and multiplication are complete.
        Conversion Ready flag bit clears when writing the configuration register or
        reading the Mask/Enable register.
    """
    math_overflow_flag = ROBit(_REG_MASK_ENABLE, 2, 2, False)
    """This bit is set to 1 if an arithmetic operation resulted in an overflow error.
    """
    alert_polarity_bit = RWBit(_REG_MASK_ENABLE, 1, 2, False)
    """Active-high open collector when True, Active-low open collector when false (default).
    """
    alert_latch_enable = RWBit(_REG_MASK_ENABLE, 0, 2, False)
    """Configures the latching feature of the ALERT pin and Alert Flag Bits.
    """

    reset_bit = RWBit(_REG_CONFIG, 15, 2, False)
    """Setting this bit t 1 generates a system reset. Reset all registers to default values."""
    averaging_count = RWBits(3, _REG_CONFIG, 9, 2, False)
    """The window size of the rolling average used in continuous mode"""
    voltage_conversion_time = RWBits(3, _REG_CONFIG, 6, 2, False)
    """The conversion time taken for the bus voltage measurement"""
    current_conversion_time = RWBits(3, _REG_CONFIG, 3, 2, False)
    """The conversion time taken for the current measurement"""

    mode = RWBits(3, _REG_CONFIG, 0, 2, False)
    """The mode that the INA260 is operating in. Must be one of
    ``Mode.CONTINUOUS``, ``Mode.TRIGGERED``, or ``Mode.SHUTDOWN``
    """

    mask_enable = RWBits(16, _REG_MASK_ENABLE, 0, 2, False)
    """The Mask/Enable Register selects the function that is enabled to control the ALERT pin as
        well as how that pin functions.
        If multiple functions are enabled, the highest significant bit
        position Alert Function (D15-D11) takes priority and responds to the Alert Limit Register.
    """
    alert_limit = RWBits(16, _REG_ALERT_LIMIT, 0, 2, False)
    """The Alert Limit Register contains the value used to compare to the register selected in the
        Mask/Enable Register to determine if a limit has been exceeded.
        The format for this register will match the format of the register that is selected for
        comparison.
    """

    TEXAS_INSTRUMENT_ID = const(0x5449)
    INA260_ID = const(0x227)
    _manufacturer_id = ROUnaryStruct(_REG_MFG_UID, ">H")
    """Manufacturer identification bits"""
    _device_id = ROBits(12, _REG_DIE_UID, 4, 2, False)
    """Device identification bits"""
    revision_id = ROBits(4, _REG_DIE_UID, 0, 2, False)
    """Device revision identification bits"""

    @property
    def current(self):
        """The current (between V+ and V-) in mA"""
        if self.mode == Mode.TRIGGERED:
            while self._conversion_ready_flag == 0:
                pass
        return self._raw_current * 1.25

    @property
    def voltage(self):
        """The bus voltage in V"""
        if self.mode == Mode.TRIGGERED:
            while self._conversion_ready_flag == 0:
                pass
        return self._raw_voltage * 0.00125

    @property
    def power(self):
        """The power being delivered to the load in mW"""
        if self.mode == Mode.TRIGGERED:
            while self._conversion_ready_flag == 0:
                pass
        return self._raw_power * 10
