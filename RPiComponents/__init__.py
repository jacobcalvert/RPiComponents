"""
    @file __init__
    @author Jacob Calvert <jacob+info@jacobncalvert.com>
    @date January, 2015
    @brief package root

    This file defines some module wide functions for controlling the GPIO
    pins.
"""
import RPi.GPIO as gpio
import BasicLogic
import LED
import L293DMotor
import Switch


def finalize():
    """
    cleans up the GPIO pins used
    call this directly before program exit to ensure things
    get reset properly on the board
    """
    gpio.cleanup()