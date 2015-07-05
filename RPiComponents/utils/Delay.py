"""
    @file Delay
    @module RPiComponents.utils.Delay
    @author Jacob Calvert <jacob+info@jacobncalvert.com>
    @date July, 2015
    @brief Time delay methods

"""
import time


def sleep_s(s):
    """
    sleep the current thread for the specified
    number of seconds
    :param s: seconds to sleep
    :return:
    """
    time.sleep(s)


def sleep_ms(ms):
    """
    sleep the current thread for the specified
    number of milliseconds
    :param ms: milliseconds to sleep
    :return:
    """
    sleep_s(ms * 10**-3)


def sleep_us(us):
    """
    sleep the current thread for the specified
    number of microseconds
    :param us: microeconds to sleep
    :return:
    """
    sleep_ns(us * 10**-3)


def sleep_ns(ns):
    """
    sleep the current thread for the specified
    number of nanoseconds
    :param ns: nanoseconds to sleep
    :return:
    """
    sleep_us(ns * 10**-3)