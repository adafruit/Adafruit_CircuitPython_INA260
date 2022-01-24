Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-ina260/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/ina260/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_CircuitPython_INA260/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_INA260/actions/
    :alt: Build Status

CircuitPython driver for the TI INA260 current and power sensor


Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Bus Device <https://github.com/adafruit/Adafruit_CircuitPython_BusDevice>`_
* `Register <https://github.com/adafruit/Adafruit_CircuitPython_Register>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

Installing from PyPI
--------------------
.. note:: This library is not available on PyPI yet. Install documentation is included
   as a standard element. Stay tuned for PyPI availability!
   If the library is not planned for PyPI, remove the entire 'Installing from PyPI' section.
   On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
   PyPI <https://pypi.org/project/adafruit-circuitpython-ina260/>`_. To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-ina260

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-ina260

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .env
    source .env/bin/activate
    pip3 install adafruit-circuitpython-ina260

Usage Example
=============
::

    import time
    import board
    import adafruit_ina260

    i2c = board.I2C()
    ina260 = adafruit_ina260.INA260(i2c)
    while True:
        print("Current: %.2f Voltage: %.2f Power:%.2f"
            %(ina260.current, ina260.voltage, ina260.power))
        time.sleep(1)

Documentation
=============

API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/ina260/en/latest/>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_INA260/blob/main/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Documentation
=============

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.
