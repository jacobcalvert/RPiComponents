"""
    @file EEPROM_24CXX
    @module RPiComponents.EEPROM_24CXX
    @author Jacob Calvert <jacob+info@jacobncalvert.com>
    @date April, 2015
    @brief Controls for I2C based 24CXX EEPROMs

    This module contains neccessary logic to read from and write to
    24CXX series EEPROMs over I2C.
"""
import smbus
import time


class BasicEEPROM(object):
    """
        ADDRESS_MODE_16BIT: the EEPROM storage address mode for devices that support 16 bits of storage selection
                            these typically have a selectable range of [0, 32768]
        ADDRESS_MODE_8BIT: the EEPROM storage address mode for devices that support 8 bits of storage selection
                            these typically have a selectable range of [0, 16383]
    """
    ADDRESS_MODE_16BIT = 0
    ADDRESS_MODE_8BIT = 1

    def __init__(self, base_address, address_mode, i2c_bus_num):
        """

        @param base_address:  the base address of the I2C device for which your using (usually 0x50)
        @param address_mode:  either BasicEEPROM.ADDRESS_MODE_16BIT or BasicEEPROM.ADDRESS_MODE_8BIT
        @param i2c_bus_num:   the I2C bus number you're using. corresponds to /dev/i2c-X X is the number you'd use
        """
        self._bus_num = i2c_bus_num
        self._base_addr = base_address
        self._addr_mode = address_mode
        self._bus = smbus.SMBus(self._bus_num)

    @staticmethod
    def usleep(us):
        """
        a microsecond sleep function
        @param us: number of microseconds to sleep
        """
        time.sleep(us * 10**(-6))

    def _write_one_byte(self, byte):

        result = self._bus.write_byte(self._base_addr, byte)
        if result is not None and result < 0:
            print "BasicEEPROM error in _write_one_byte()"
        BasicEEPROM.usleep(10000)
        return result

    def _write_three_bytes(self, bytes_lst):
        result = self._bus.write_word_data(self._base_addr, bytes_lst[0], (bytes_lst[2] << 8) | bytes_lst[1])
        if result is not None and result < 0:
            print "BasicEEPROM error in _write_three_bytes()"
        BasicEEPROM.usleep(10000)
        return result

    def _write_two_bytes(self, bytes_lst):
        result = self._bus.write_byte_data(self._base_addr, bytes_lst[0], bytes_lst[1])
        if result is not None and result < 0:
            print "BasicEEPROM error in _write_two_bytes()"
        BasicEEPROM.usleep(10000)
        return result

    def write_byte(self, addr, byte):
        """
        write one byte to the EEPROM at the specified address
        @param addr: the EEPROM storage address
        @param byte: the byte value
        """
        result = 0
        if self._addr_mode == BasicEEPROM.ADDRESS_MODE_8BIT:
            bytes_lst =[addr & 0x0ff, byte]
            result = self._write_two_bytes(bytes_lst)
        elif self._addr_mode == BasicEEPROM.ADDRESS_MODE_16BIT:
            bytes_lst = [(addr >> 8) & 0x0ff, addr & 0x0ff, byte]
            result = self._write_three_bytes(bytes_lst)
        if result is not None and result < 0:
            print "BasicEEPROM error in write_byte()"
        return result

    def read_byte(self, addr):
        """
        read one byte from EEPROM storage at the address specified
        @param addr: the EEPROM storage address to read from
        @return: the value at the specified EEPROM storage address
        """
        result = 0
        if self._addr_mode == BasicEEPROM.ADDRESS_MODE_8BIT:
            addr &= 0xff
            result = self._write_one_byte(addr)
        elif self._addr_mode == BasicEEPROM.ADDRESS_MODE_16BIT:
            addr_lst = [(addr >> 8) & 0x0ff, addr & 0x0ff]
            result = self._write_two_bytes(addr_lst)
        if result is not None and result < 0:
            print "BasicEEPROM error in read_byte()"

        BasicEEPROM.usleep(10)
        byte = self._bus.read_byte(self._base_addr)
        return byte

    def write_bytes(self, addr_start, bytes_lst):
        """
        write N bytes to the EEPROM storage starting at addr_start
        @param addr_start: the starting address
        @param bytes_lst: a list() of bytes to be written
        """
        for i in range(len(bytes_lst)):
            result = self.write_byte(addr_start+i, bytes_lst[i])
            if result is not None and result < 0:
                print "BasicEEPROM error in write_bytes()"

    def read_bytes(self, addr_start, length):
        """
        read lenght bytes from the EEPROM storage starting with addr_start
        @param addr_start: the starting address to begin reading
        @param length: the length of bytes to read
        @return: a list of read bytes
        """
        bytes_lst = list()

        for i in range(length):
            bytes_lst.append(self.read_byte(addr_start+i))

        return bytes_lst

    def write_string(self, addr_start, string):
        """
        write an ASCII string to the EEPROM storage starting with addr_start
        @param addr_start: the starting address
        @param string:  the string to write
        """
        def to_byte(c):
            c = ord(c)
            return int(c)
        bytes_lst = map(to_byte, string)
        return self.write_bytes(addr_start, bytes_lst)

    def read_string(self, addr_start, length):
        """
        read a number of bytes from EEPROM storage as a string
        @param addr_start: the starting address
        @param length: the number of bytes to read
        @return: a string
        """
        bytes_lst = self.read_bytes(addr_start, length)
        char_lst = map(chr, bytes_lst)
        return "".join(char_lst)

    def fill_space(self, addr_begin, addr_end, fill_content=0):
        """
        fill the space between addr_begin and addr_end with fill_content
        @param addr_begin: the starting address
        @param addr_end:  the ending address
        @param fill_content: the fill byte value
        """
        for i in range(addr_begin, addr_end):
            self.write_byte(i, fill_content)

