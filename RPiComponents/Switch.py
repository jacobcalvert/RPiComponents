"""
    @file Switch
    @module RPiComponents.Switch
    @author Jacob Calvert <jacob+info@jacobncalvert.com>
    @date January, 2015
    @brief Switch control objects

    This module contains a class to start a sampling thread on a
    input switch from the GPIO pins and fire a callback in a new thread
    when the switch is activated
"""
import RPi.GPIO as gpio
import threading
import time
import BasicLogic


class ThreadedCallbackSwitch(BasicLogic.BasicToggleInput, threading.Thread):

    SLEEP_DELAY_S = 0.02
    INST_COUNT = 0

    def __init__(self, pin, callback=None, callback_args=None, positive_trig=True, pud=None, numbering=gpio.BCM, _gpio=gpio):
        """
        ThreadedCallbackSwitch constructor
        @param pin the GPIO pin number to be used
        @param callback the callback to be fired when the switch is activated
        @param callback_args the arguments to be passed to the callback
        @param positive_trig if set to True, the callback will fire on 'switch down', if set to False it will fire on 'switch up'
        @param pud the pull up or pull down resistor value from RPi.GPIO if None then no PUD will be set in software
        @param numbering the pin numbering system (RPi.GPIO.BOARD or RPi.GPIO.BCM)
        @param _gpio the gpio object if using a different than the default
        """
        BasicLogic.BasicToggleInput.__init__(self, pin, pud, numbering, _gpio)
        threading.Thread.__init__(self)
        self._callback = callback
        self._callback_args = callback_args
        self._run_flag = threading.Event()
        self._trigger = positive_trig
        self._inst_id = ThreadedCallbackSwitch.INST_COUNT+1
        ThreadedCallbackSwitch.INST_COUNT += 1

    def run(self):
        """
        DON'T CALL THIS DIRECTLY
        start the thread by calling the start() method on this object.
        kthx
        """
        self._run_flag.set()
        last_val = self.sample()
        while self._run_flag.isSet():
            sample = self.sample()
            if sample == last_val:
                time.sleep(self.SLEEP_DELAY_S)
            else:
                send_event = False
                if sample == self._trigger:
                    send_event = True

                if send_event:
                    if self._callback and self._callback_args:
                        self._callback(self._callback_args)

                    elif self._callback and not self._callback_args:
                        self._callback()

                    elif not self._callback:
                        print "Callback happened on ThreadedCallbackSwitch instance # %d" % (self._inst_id)
                last_val = sample
        del self

    def stop(self):
        """
        sets the run/stop flag event to false so the monitoring thread will exit cleanly
        """
        self._run_flag.clear()