"""
    @file LCD
    @module RPiComponents.LCD
    @author Jacob Calvert <jacob+info@jacobncalvert.com>
    @date Jult, 2015
    @brief Basic LCD control for a common type of LCD

"""
from BasicLogic import *
from utils import Delay


class LCD1602A1(object):
    """
    The LCD1602A1 model is a 16x2 character LCD described here
    https://www.openhacks.com/uploadsproductos/eone-1602a1.pdf.
    This class models an OOP way to manage its features and
    utilize the LCD module with little to no effort.
    """

    class MarqueeText(object):
        DIRECTION_LEFT = 1
        DIRECTION_RIGHT = 2

    def __init__(self, enable, rw, rs, dbits):
        """

        :param enable: the LCD enable pin number
        :param rw: the LCD read/write pin number
        :param rs: the LCD register/select pin number
        :param dbits: the data bit pin numbers [0-3]
        :return:
        """
        self._EN = BasicToggleOutput(enable)
        self._EN.lo()
        self._RW = BasicToggleOutput(rw)
        self._RW.lo()
        self._RS = BasicToggleOutput(rs)
        self._RS.lo()
        self._DATA = [None]*4
        for i in range(4):
            self._DATA[i] = (BasicToggleOutput(dbits[i]))

        for databit in self._DATA:
            databit.lo()

        self.clear()

    def write(self, _byte, is_char=False):
        """
        write a command or character to the LCD module
        :param _byte: byte to be written
        :param is_char: boolean selecting if is false
        :return:
        """
        Delay.sleep_ms(10)

        bits = bin(_byte)[2:].zfill(8)
        if is_char:
            self._RS.hi()
        else:
            self._RS.lo()

        for databit in self._DATA:
            databit.lo()

        for i in range(4):
            if bits[i] == "1":
                self._DATA[::-1][i].high()

        self._EN.hi()
        self._EN.lo()

        for databit in self._DATA:
            databit.lo()

        for i in range(4, 8):
            if bits[i] == "1":
                self._DATA[::-1][i-4].high()

        self._EN.hi()
        self._EN.lo()

    def clear(self):
        """
        series of commands that clear
        and reset the interface
        :return:
        """
        self.write(0x33)
        self.write(0x32)
        self.write(0x28)
        self.write(0x0C)
        self.write(0x06)
        self.write(0x01)

    def write_str(self, _str, wrap=False):
        """
        writes the string to the display
        :param _str: the string to be written
        :param wrap: wrap or truncate the string
        :return:
        """
        if len(_str) > 32:
            _str = _str[:32]

        count = 0
        for c in _str:
            count += 1
            if c == "\n":
                self.write(0xC0)
            else:
                self.write(ord(c), True)

            if count == 16 and wrap:
                self.write(0xC0)

    def marquee_one_line(self, line, delay_ms, direction=MarqueeText.DIRECTION_LEFT, repeat=True):
        """
        ***EXPERIMENTAL***
        make the text marquee across the top line of the display
        :param line: the line to display
        :param delay_ms: the delay between steps in milliseconds
        :param direction: direction defined by  LCD1602A1.MarqueeText.Direction_* parameter, left or right
        :param repeat: repeat or scroll only once
        :return:
        """
        if len(line) < 16:
            line += (16-len(line))*' '
        orig_state = line
        while True:
            self.clear()
            self.write_str(line)
            if direction is self.MarqueeText.DIRECTION_LEFT:
                line = self._left_rotate(line)
            else:
                line = self._right_rotate(line)
            Delay.sleep_ms(delay_ms)

            if not repeat and line == orig_state:
                self.clear()
                break


    @staticmethod
    def _left_rotate(text):
        return text[1:] + text[0]


    @staticmethod
    def _right_rotate(text):
        return text[-1] + text[:-1]



