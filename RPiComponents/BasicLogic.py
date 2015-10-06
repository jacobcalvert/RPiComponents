"""
    @file BasicLogic
    @module RPiComponents.BasicLogic
    @author Jacob Calvert <jacob+info@jacobncalvert.com>
    @date January, 2015
    @brief Basic logic control objects

    This module contains several basic logic control objects
    for reading or writing to a pin in a object-oriented style.
"""
import RPi.GPIO as gpio


class BasicToggleOutput(object):

    def __init__(self, pin, numbering=gpio.BCM, _gpio=gpio):
        """
        BasicToggleOutput constructor
        @param pin the GPIO pin number to be used
        @param numbering the pin numbering system (RPi.GPIO.BOARD or RPi.GPIO.BCM)
        @param _gpio the gpio object if using a different than the default
        """
        self._pin = pin
        self._gpio = _gpio
        self._gpio.setmode(numbering)
        self._gpio.setup(self._pin, self._gpio.OUT)

    def high(self):
        """
        sets the pin to the logic HIGH state
        """
        self._gpio.output(self._pin, self._gpio.HIGH)

    def low(self):
        """
        sets the pin to the logic LOW state
        """
        self._gpio.output(self._pin, self._gpio.LOW)

    def hi(self):
        """
        alias of high()
        """
        self.high()

    def lo(self):
        """
        alias of low()
        """
        self.low()

    def value(self):
        """
        gets the current value (hi/lo) of the pin
        @return a value T/F or 1/0 indicating the state of the pin
        """
        return self._gpio.input(self._pin)


class BasicSoftPWM(object):

    PWM_FREQ = 100  # Hz

    def __init__(self, pin, duty_cycle, numbering=gpio.BCM, _gpio=gpio):

        """
        BasicSoftPWM constructor
        @param pin the pin to set up PWM on
        @param duty_cycle the initial duty cycle for the PWM
        @param numbering the pin numbering system (RPi.GPIO.BOARD or RPi.GPIO.BCM)
        @param _gpio the gpio object if using a different than the default
        """
        if duty_cycle < 0 or duty_cycle > 100:
            self._pwm_duty_cycle = 0
            raise ValueError("Duty Cycle must be in range [0-100].")
        self._pin = pin
        self._gpio = _gpio
        self._gpio.setmode(numbering)
        self._gpio.setup(self._pin, self._gpio.OUT)
        self._pwm_duty_cycle = duty_cycle
        self._pwm_freq = self.PWM_FREQ
        self._pwm_handle = self._gpio.PWM(self._pin, self._pwm_freq)

    def start(self):
        """
        starts the PWM cycle
        """
        self._pwm_handle.start(self._pwm_duty_cycle)

    def stop(self):
        """
        stops the PWM cycle
        """
        self._pwm_handle.stop()

    def set_duty_cycle(self, dc):
        """
        sets the duty_cycle of the PWM
        @param dc the duty cycle [0,100]
        """
        if dc < 0 or dc > 100:
            raise ValueError("Duty Cycle must be in range [0-100].")
        else:
            self._pwm_duty_cycle = dc
            self._pwm_handle.ChangeDutyCycle(self._pwm_duty_cycle)

    def set_pwm_freq(self, freq):
        """
        sets the PWM frequency
        @param freq the frequency
        """
        self._pwm_freq = freq
        self._pwm_handle.ChangeFrequency(self._pwm_freq)

    def frequency(self):
        """
        gets the PWM frequency
        """
        return self._pwm_freq

    def duty_cycle(self):
        """
        gets the PWM duty cycle
        """
        return self._pwm_duty_cycle


class BasicToggleInput(object):
    def __init__(self, pin, pud=None, numbering=gpio.BCM, _gpio=gpio):
        """
        BasicToggleInput constructor
        @param pin the input pin to be used
        @param pud a RPi.GPIO macro defining whether to use pull-up, pull-down or no software PUD
        @param numbering the pin numbering system (RPi.GPIO.BOARD or RPi.GPIO.BCM)
        @param _gpio the gpio object if using a different than the default
        """
        self._pin = pin
        self._gpio = _gpio
        self._gpio.setmode(numbering)
        if pud:
            self._gpio.setup(self._pin, self._gpio.IN, pull_up_down=pud)  # using internal pud resistor
        else:
            self._gpio.setup(self._pin, self._gpio.IN)  # external pud

    def sample(self):
        """
        gets the current value (hi/lo) of the pin
        @return a value T/F or 1/0 indicating the state of the pin
        """
        return self._gpio.input(self._pin)


class BasicToggleInputOutput(object):
    MODE_IN = 0
    MODE_OUT= 1

    def __init__(self, pin, mode=MODE_IN, pud=None, numbering=gpio.BCM, _gpio=gpio):
        self._pin = pin
        self._gpio = _gpio
        self._gpio.setmode(numbering)
        self._pud = pud
        if mode == BasicToggleInputOutput.MODE_IN:
            self.set_input()
        else:
            self.set_output()

    def sample(self):
        return self._gpio.input(self._pin)

    def set_output(self):
        self._gpio.setup(self._pin, self._gpio.OUT)

    def set_input(self):
        if self._pud:
                self._gpio.setup(self._pin, self._gpio.IN, pull_up_down=self._pud)  # using internal pud resistor
        else:
                self._gpio.setup(self._pin, self._gpio.IN)  # external pud

    def high(self):
        """
        sets the pin to the logic HIGH state
        """
        self._gpio.output(self._pin, self._gpio.HIGH)

    def low(self):
        """
        sets the pin to the logic LOW state
        """
        self._gpio.output(self._pin, self._gpio.LOW)

    def hi(self):
        """
        alias of high()
        """
        self.high()

    def lo(self):
        """
        alias of low()
        """
        self.low()

    def value(self):
        """
        gets the current value (hi/lo) of the pin
        @return a value T/F or 1/0 indicating the state of the pin
        """
        return self._gpio.input(self._pin)


class ToggleInputCallback(BasicToggleInput):

    DEBOUNCE_DELAY_MS = 2
    INST_COUNT = 0

    def __init__(self, pin, callback=None, debounce_delay=DEBOUNCE_DELAY_MS, edge=gpio.RISING, pud=None, numbering=gpio.BCM, _gpio=gpio):
        """
        ThreadedCallbackSwitch constructor
        @param pin the GPIO pin number to be used
        @param callback the callback to be fired when the switch is activated
        @param callback_args the arguments to be passed to the callback
        @param edge RISING, FALLING, or BOTH
        @param numbering the pin numbering system (RPi.GPIO.BOARD or RPi.GPIO.BCM)
        @param _gpio the gpio object if using a different than the default
        """
        BasicToggleInput.__init__(self, pin, pud=pud, numbering=numbering, _gpio=gpio)
        self._callback = callback
        if callback is None:
            self._callback = self.default_callback
        self._inst_id = ToggleInputCallback.INST_COUNT+1
        ToggleInputCallback.INST_COUNT += 1
        self._gpio.add_event_detect(self._pin, edge, self._callback, debounce_delay)

    def default_callback(self, pin):
        print "Callback happened on ToggleInputCallback instance # %d @ pin %d" % (self._inst_id, pin)