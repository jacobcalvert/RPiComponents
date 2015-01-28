"""
    @file LED
    @module RPiComponents.LED
    @author Jacob Calvert <jacob+info@jacobncalvert.com>
    @date January, 2015
    @brief Basic LED control objects

    This module contains two basic control objects
    for controlling LEDs using the GPIOs
"""
import RPi.GPIO as gpio
import BasicLogic


class BasicLED(BasicLogic.BasicToggleOutput):
    def __init__(self, pin, numbering=gpio.BCM, _gpio=gpio):
        """
        BasicLED constructor
        @param pin the GPIO pin number to be used
        @param numbering the pin numbering system (RPi.GPIO.BOARD or RPi.GPIO.BCM)
        @param _gpio the gpio object if using a different than the default
        """
        BasicLogic.BasicToggleOutput.__init__(self, pin, numbering, _gpio)

    def on(self):
        self.high()

    def off(self):
        self.low()


class FadableLED(BasicLogic.BasicSoftPWM):
    def __init__(self, pin, initial_brightness, numbering=gpio.BCM, _gpio=gpio):

        """
        FadableLED constructor, creates a control that can be used to fade an LED via PWM
        @param pin the GPIO pin number to be used
        @param initial_brightness the initial brightness to set the LED to [0,100]
        @param numbering the pin numbering system (RPi.GPIO.BOARD or RPi.GPIO.BCM)
        @param _gpio the gpio object if using a different than the default
        """
        self._brightness = initial_brightness
        BasicLogic.BasicSoftPWM.__init__(self, pin, self._brightness, numbering, _gpio)
        self.start()

    def set_brightness(self, brightness):
        """
        sets the brightness of the LED
        @param brightness the brightness [0,100]
        """
        if brightness < 0 or brightness > 100:
            raise ValueError("Brightness must be in range [0-100]")
        else:
            self._brightness = brightness
            self.set_duty_cycle(self._brightness)

    def on(self):
        """
        turns the LED on to 100%
        """
        self.set_brightness(100)

    def off(self):
        """
        turns the LED off to 0%
        """
        self.set_brightness(0)