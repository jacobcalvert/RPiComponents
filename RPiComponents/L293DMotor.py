"""
    @file L293DMotor
    @module RPiComponents.L293DMotor
    @author Jacob Calvert <jacob+info@jacobncalvert.com>
    @date January, 2015
    @brief Control objects for the L293D motor controller IC

    This module contains two control objects for the L293D motor
    controller chip. A basic on/off/fwd/rev object is first followed
    by a PWM controlled variable speed on/off/fwd/rev control object
"""
import RPi.GPIO as gpio


class BasicL293DMotor(object):

    FWD = 1
    STOPPED = 0
    REV = -1

    def __init__(self, enable_pin, fwd_pin, rev_pin, numbering=gpio.BCM, _gpio=gpio):
        """
        BasicL293DMotor constructor
        @param enable_pin the enable pin used
        @param fwd_pin the forward polarity pin
        @param rev_pin the reverse polarity pin
        @param numbering the pin numbering system (RPi.GPIO.BOARD or RPi.GPIO.BCM)
        @param _gpio the gpio object if using a different than the default
        """
        self._gpio = _gpio
        self._gpio.setmode(numbering)
        self._enable = enable_pin
        self._is_enabled = False
        self._fwd = fwd_pin
        self._rev = rev_pin

        self._direction = self.STOPPED

        self._gpio.setup(self._enable, self._gpio.OUT)
        self._gpio.setup(self._fwd, self._gpio.OUT)
        self._gpio.setup(self._rev, self._gpio.OUT)

    def enable(self):
        """
        enable the motor controller chip
        """
        self._gpio.output(self._enable, self._gpio.HIGH)

    def disable(self):
        """
        disable the motor controller chip
        """
        self._gpio.output(self._enable, self._gpio.LOW)

    def is_enabled(self):
        """
        gets the value of the enable pin T/F or 1/0
        """
        return True if self._gpio.input(self._enable) else False

    def fwd(self):
        """
        start the motor in the fwd direction
        """
        if not self.is_enabled():
            print "Warning: motor is not enabled."
        self._direction = self.FWD
        self._gpio.output(self._rev, self._gpio.LOW)
        self._gpio.output(self._fwd, self._gpio.HIGH)

    def rev(self):
        """
        start the motor in the rev direction
        """
        if not self.is_enabled():
            print "Warning: motor is not enabled."
        self._direction = self.REV
        self._gpio.output(self._fwd, self._gpio.LOW)
        self._gpio.output(self._rev, self._gpio.HIGH)

    def stop(self):
        """
        stop the motor
        """
        if not self.is_enabled():
            print "Warning: motor is not enabled."
        self._direction = self.STOPPED
        self._gpio.output(self._fwd, self._gpio.LOW)
        self._gpio.output(self._rev, self._gpio.LOW)

    def direction(self):
        """
        returns a value indicating the current direction of the motor
        {BasicL293DMotor.FWD, BasicL293DMotor.STOPPED, BasicL293DMotor.REV}
        """
        return self._direction


class VariableSpeedL293DMotor(BasicL293DMotor):
    PWM_FREQ = 100

    def __init__(self, enable_pin, fwd_pin, rev_pin, numbering=gpio.BCM, _gpio=gpio):
        """
        VariableSpeedL293DMotor constructor
        @param enable_pin the enable pin used
        @param fwd_pin the forward polarity pin
        @param rev_pin the reverse polarity pin
        @param numbering the pin numbering system (RPi.GPIO.BOARD or RPi.GPIO.BCM)
        @param _gpio the gpio object if using a different than the default
        """
        BasicL293DMotor.__init__(self, enable_pin, fwd_pin, rev_pin, numbering, _gpio)
        self._pwm_freq = self.PWM_FREQ
        self._pwm_duty_cycle = 0  # stopped
        self._fwd_pwm = self._gpio.PWM(self._fwd, self.PWM_FREQ)
        self._rev_pwm = self._gpio.PWM(self._rev, self.PWM_FREQ)

        self._fwd_pwm.start(self._pwm_duty_cycle)
        self._rev_pwm.start(self._pwm_duty_cycle)

    def stop(self):
        """
        stop the motor
        """
        if not self.is_enabled():
            print "Warning: motor is not enabled."
        self._fwd_pwm.ChangeDutyCycle(0)
        self._rev_pwm.ChangeDutyCycle(0)

    def set_speed(self, speed):
        """
        set the motor speed as a percentage of it's max speed
        """
        if speed < 0 or speed > 100:
            raise ValueError("Speed must be in range [0-100].")

        self._pwm_duty_cycle = speed

        # updating the direction

        if self._direction is self.FWD:
            self.fwd()
        elif self._direction is self.REV:
            self.rev()

    def fwd(self, speed=None):
        """
        start the motor in the fwd direction, set the speed optionally
        @param speed optional speed parameter sets the speed and starts the motor in the indicated direction
        """
        if speed:
            self.set_speed(speed)
        self._direction = self.FWD
        self._fwd_pwm.ChangeDutyCycle(self._pwm_duty_cycle)
        self._rev_pwm.ChangeDutyCycle(0)

    def rev(self, speed=None):
        """
        start the motor in the rev direction, set the speed optionally
        @param speed optional speed parameter sets the speed and starts the motor in the indicated direction
        """
        if speed:
            self.set_speed(speed)
        self._direction = self.REV
        self._rev_pwm.ChangeDutyCycle(self._pwm_duty_cycle)
        self._fwd_pwm.ChangeDutyCycle(0)



