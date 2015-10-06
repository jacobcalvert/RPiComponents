"""
    @file RangeFinders
    @module RPiComponents.RangeFinders
    @author Jacob Calvert <jacob+info@jacobncalvert.com>
    @date September, 2015
    @brief Control for various rangefinders


"""
import RPi.GPIO as gpio
import BasicLogic
import utils.Delay
import utils.Tolerance
import time


class UltraSonicHCSR04(object):
    def __init__(self, trig, echo, conv_func=None, numbering=gpio.BCM, _gpio=gpio):
        self._trigger = BasicLogic.BasicToggleOutput(trig, numbering, _gpio)
        self._echo = BasicLogic.BasicToggleInput(echo, numbering=numbering, _gpio=_gpio)
        self._trigger.lo()
        self._trig_time = 0
        self._conv = conv_func
        if conv_func is None:
            self._conv = UltraSonicHCSR04.default_conv_func

    @staticmethod
    def default_conv_func(uS):
        return uS*6751.968

    def sample(self):
        self._trigger.lo()
        self._trigger.hi()
        self._trig_time = time.time()
        utils.Delay.sleep_us(10)
        self._trigger.lo()
        start, end = time.time(), time.time()
        while not self._echo.sample():
            start = time.time()

        while self._echo.sample():
            end = time.time()

        time_diff = end-start

        return self._conv(time_diff)

    def get_approximate_distance(self, time_points=10, tolerance_percent=5):
        points = list()
        sleep_time = 60  # ms
        while time_points:
            time_points -= 1
            points.append(self.sample())
            utils.Delay.sleep_ms(sleep_time)
        final_pts = list()
        for i in range(1, len(points)):
            if utils.Tolerance.is_within_tol(points[i-1], points[i], tolerance_percent):
                final_pts.append(points[i-1])

        return sum(final_pts)/len(final_pts)


