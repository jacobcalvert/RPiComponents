"""
    @file RF24
    @module RPiComponents.RF24
    @author Jacob Calvert <jacob+info@jacobncalvert.com>
    @date October, 2015
    @brief Control for the common 2.4 GHz NRF24L01+ transceiver


"""
from BasicLogic import *
import RPi.GPIO as gpio
import spidev
import utils.Delay as delay


class Radio(object):
    """
        This is the class for controlling an NRF24L01+ transceiver
        via SPI bus and a couple of GPIO pins
    """

    """
        COMMANDS holds the byte value of each command
    """
    COMMANDS = dict()
    COMMANDS["W_REGISTER"] = 0x20
    COMMANDS["R_REGISTER"] = 0x00
    COMMANDS["R_RX_PAYLOAD"] = 0x61
    COMMANDS["W_TX_PAYLOAD"] = 0xA0
    COMMANDS["FLUSH_TX"] = 0x71
    COMMANDS["FLUSH_RX"] = 0x72
    COMMANDS["REUSE_TX_PL"] = 0x73
    COMMANDS["R_RX_PL_WID"] = 0x60
    COMMANDS["W_TX_PAYLOAD_NOACK"] = 0xB0
    COMMANDS["NOP"] = 0xFF

    """
        REGISTERS holds the byte value of each register
    """
    REGISTERS = dict()
    REGISTERS["CONFIG"] = 0x00
    REGISTERS["EN_AA"] = 0x01
    REGISTERS["EN_RXADDR"] = 0x02
    REGISTERS["SETUP_ADDRW"] = 0x03
    REGISTERS["SETUP_RETR"] = 0x04
    REGISTERS["RF_CH"] = 0x05
    REGISTERS["RF_SETUP"] = 0x06
    REGISTERS["STATUS"] = 0x07
    REGISTERS["OBSERVE_TX"] = 0x08
    REGISTERS["RPD"] = 0x09
    REGISTERS["RX_ADDR_P0"] = 0x0A
    REGISTERS["RX_ADDR_P1"] = 0x0B
    REGISTERS["RX_ADDR_P2"] = 0x0C
    REGISTERS["RX_ADDR_P3"] = 0x0D
    REGISTERS["RX_ADDR_P4"] = 0x0E
    REGISTERS["RX_ADDR_P5"] = 0x0F
    REGISTERS["TX_ADDDR"] = 0x10
    REGISTERS["RX_PW_P0"] = 0x11
    REGISTERS["RX_PW_P1"] = 0x12
    REGISTERS["RX_PW_P2"] = 0x13
    REGISTERS["RX_PW_P3"] = 0x14
    REGISTERS["RX_PW_P4"] = 0x15
    REGISTERS["RX_PW_P5"] = 0x16
    REGISTERS["FIFO_STATUS"] = 0x17

    """
        BIT_MNEMONIC holds the bit number for selected bits
        of the devices' registers
    """
    BIT_MNEMONIC = dict()
    BIT_MNEMONIC["MASK_RX_DR"] = 6
    BIT_MNEMONIC["MASK_TX_DS"] = 5
    BIT_MNEMONIC["MASK_MAX_RT"] = 4
    BIT_MNEMONIC["EN_CRC"] = 3
    BIT_MNEMONIC["CRCO"] = 2
    BIT_MNEMONIC["PWR_UP"] = 1
    BIT_MNEMONIC["PRIM_RX"] = 0
    BIT_MNEMONIC["ENAA_P5"] = 5
    BIT_MNEMONIC["ENAA_P4"] = 4
    BIT_MNEMONIC["ENAA_P3"] = 3
    BIT_MNEMONIC["ENAA_P2"] = 2
    BIT_MNEMONIC["ENAA_P1"] = 1
    BIT_MNEMONIC["ENAA_P0"] = 0
    BIT_MNEMONIC["ERX_P5"] = 5
    BIT_MNEMONIC["ERX_P4"] = 4
    BIT_MNEMONIC["ERX_P3"] = 3
    BIT_MNEMONIC["ERX_P2"] = 2
    BIT_MNEMONIC["ERX_P1"] = 1
    BIT_MNEMONIC["ERX_P0"] = 0
    BIT_MNEMONIC["AW"] = 0
    BIT_MNEMONIC["ARD"] = 4
    BIT_MNEMONIC["ARC"] = 0
    BIT_MNEMONIC["PLL_LOCK"] = 4
    BIT_MNEMONIC["RF_DR"] = 3
    BIT_MNEMONIC["RF_PWR"] = 1
    BIT_MNEMONIC["LNA_HCURR"] = 0
    BIT_MNEMONIC["RX_DR"] = 6
    BIT_MNEMONIC["TX_DS"] = 5
    BIT_MNEMONIC["MAX_RT"] = 4
    BIT_MNEMONIC["RX_P_NO"] = 1
    BIT_MNEMONIC["TX_FULL"] = 0
    BIT_MNEMONIC["PLOS_CNT"] = 4
    BIT_MNEMONIC["ARC_CNT"] = 0
    BIT_MNEMONIC["TX_REUSE"] = 6
    BIT_MNEMONIC["FIFO_FULL"] = 5
    BIT_MNEMONIC["TX_EMPTY"] = 4
    BIT_MNEMONIC["RX_FULL"] = 1
    BIT_MNEMONIC["RX_EMPTY"] = 0


    def __init__(self, bus, port, ce, _int, numbering=gpio.BCM, _gpio=gpio):
        """

        :param bus: the SPI bus number
        :param port: the SPI port number
        :param ce: chip enable pin (NOT the SPI chip select)
        :param _int: the chip IRQ pin
        :param numbering: GPIO numbering scheme
        :param _gpio: which gpio to use
        :return: an instance of this class

        radio_1 = RF24.Radio(0, 0, 26, 19)

        """
        self._spi = spidev.SpiDev()
        self._spi.open(bus, port)
        self._ce = BasicToggleOutput(ce, numbering=numbering, _gpio=_gpio)
        self._int = ToggleInputCallback(_int, callback=self.interrupted, numbering=numbering, _gpio=_gpio, edge=_gpio.FALLING)

    def interrupted(self, pin):
        print "Rx'd interrupt"

        if self.is_data_ready():
            print "Data Ready"
        if self.is_txing():
            print "Data tx'd"

    def write_register(self, register, value):
        """
        writes value to register
        :param register: register number from Radio.REGISTERS
        :param value: an 8 bit value to write
        :return: None
        """
        # write register is 001AAAAA
        # where AAAAA is reg num
        cmd = Radio.COMMANDS["W_REGISTER"] | (0x1f & register)
        self._spi.xfer2([cmd, value])

    def read_register(self, register):
        """
        reads value from register
        :param register: register number from Radio.REGISTERS
        :return: value read from register
        """
        # read register is 000AAAAA
        # where AAAAA is reg num
        cmd = Radio.COMMANDS["R_REGISTER"] | (0x1f & register)
        result = self._spi.xfer2([cmd, 0])
        return result[1]

    def read_config(self):
        """
        reads configuration register
        :return: value of config register
        """
        return self.read_register(Radio.REGISTERS["CONFIG"])

    def write_config_bit(self, bit, val):
        """
        sets bit number 'bit' to val (0/1)
        :param bit: the bit number
        :param val: the value 0/1
        :return: None
        """
        if val == 0:
            self.write_register(Radio.REGISTERS["CONFIG"], self.read_config() & ~(1 << bit))
        else:
            self.write_register(Radio.REGISTERS["CONFIG"], self.read_config() | 1 << bit)

    def read_status(self):
        """
        reads and returns the status register
        :return: status register value
        """
        cmd = Radio.COMMANDS["NOP"]
        result = self._spi.xfer2([cmd])
        return result[0]

    def power_up(self):
        """
        powers up the radio
        :return:
        """
        self.write_config_bit(Radio.BIT_MNEMONIC["PWR_UP"], 1)

    def power_down(self):
        """
        powers down the radio
        :return:
        """
        self.write_config_bit(Radio.BIT_MNEMONIC["PWR_UP"], 0)

    def set_channel(self, ch):
        """
        set the radio channel
        :param ch: the new channel
        :return:
        """
        self.write_register(Radio.REGISTERS["RF_CH"], ch)

    def get_channel(self):
        """
        read the radio channel
        :return:
        """
        return self.read_register(Radio.REGISTERS["RF_CH"])

    def start_rx(self):
        """
        start rx mode
        :return:
        """
        # PRIM_RX is bit 0 in CONFIG
        # PRIM_RX=1 is RX mode
        self._ce.lo()
        self.write_config_bit(Radio.BIT_MNEMONIC["PRIM_RX"], 1)
        self._ce.hi()

    def start_tx(self):
        """
        start tx mode
        :return:
        """
        # PRIM_RX is bit 0 in CONFIG
        # PRIM_RX=0 is TX mode
        self._ce.lo()
        self.write_config_bit(Radio.BIT_MNEMONIC["PRIM_RX"], 0)
        self._ce.hi()

    def write_payload(self, payload):
        """
        write a payload to the device
        :param payload: a list of ints to be written
        :return:
        """
        self._spi.xfer2([Radio.COMMANDS["FLUSH_TX"]])
        cmd = [Radio.COMMANDS["W_TX_PAYLOAD"]] + payload
        self._spi.xfer2(cmd)

    def is_txing(self):
        """

        :return: T/F indicating is transmitting
        """
        config = self.read_config()
        if config % 2 == 0:
            return True
        return False

    def is_data_ready(self):
        """

        :return:T/F indicating is data ready for reading
        """
        status = self.read_status()
        if status & (1 << 6):
            return True

        return False

    def read_data(self, _len):
        """
        read the data from the RX FIFO
        :param _len: length of data to be read
        :return: list of data
        """
        data = self._spi.xfer2([Radio.COMMANDS["R_RX_PAYLOAD"]] + [0]*_len)
        self.write_register(Radio.REGISTERS["STATUS"], self.read_status() | 1<<6) # write a 1 in pos 6 to clear FIFO
        return data[1:]

    def set_payload_size(self, payload_sz, pipe=0):
        """
        set the payload size in range [0, 32]
        :param payload_sz: payload size
        :param pipe: pipe number
        :return:
        """
        if pipe == 0:
            self.write_register(Radio.REGISTERS["RX_PW_P0"], payload_sz)

    def setup_basic(self):
        """
        basic setup routine, can begin transmitting and receiving data
        between two radios with these settings immediately
        :return:
        """
        self.power_up()
        delay.sleep_ms(1.5)
        self.set_channel(104)
        self.set_payload_size(32)
        self.flush_all()
        self.start_rx()

    def flush_all(self):
        """
        flushes all FIFOs
        :return:
        """
        self._spi.xfer2([Radio.COMMANDS["FLUSH_RX"]])
        self._spi.xfer2([Radio.COMMANDS["FLUSH_TX"]])


    def write_str(self, _str):
        """
        write a string as a payload
        :param _str:
        :return:
        """
        data = map(ord, _str)
        if len(data) < 32:
            data += [0]* (32 - len(data))

        self.write_payload(data)
        self.start_tx()

    def read_str(self):
        """
        read a string as a payload
        :return:
        """
        if not self.is_data_ready():
            return ""
        else:
            _str = ""
            data = self.read_data(32)
            for d in data:
                if d != 0:
                    _str += chr(d)
            return _str

    @staticmethod
    def is_bit_set(byte, bit):
        return byte & (1<<bit)

    def print_summary(self):
        """
        debug
        :return:
        """
        self.print_status()
        self.print_config()

    def print_status(self):
        """
        debug
        :return:
        """
        status = self.read_status()
        print "----------------STATUS----------------"
        print "%-20s %s" % ("Data Ready", "Yes" if Radio.is_bit_set(status, 6) else "No")
        print "%-20s %s" % ("Data Sent", "Yes" if Radio.is_bit_set(status, 5) else "No")
        print "%-20s %s" % ("Max Retries", "Yes" if Radio.is_bit_set(status, 4) else "No")
        pipe = status & 0b00001110
        pipe >>= 1
        if pipe == 7:
             print "%-20s %s" % ("RX FIFOs Empty", "Yes")
        else:
             print "%-20s %s" % ("Pipe %d" %(pipe), "Data Ready")
        print "%-20s %s" % ("Tx FIFO Full", "Yes" if Radio.is_bit_set(status, 0) else "No")

        fifo_status = self.read_register(Radio.REGISTERS["FIFO_STATUS"])
        print "%-20s %s" % ("Tx Reuse", "Yes" if Radio.is_bit_set(fifo_status, 6) else "No")
        print "%-20s %s" % ("Tx Full", "Yes" if Radio.is_bit_set(fifo_status, 5) else "No")
        print "%-20s %s" % ("Tx Empty", "Yes" if Radio.is_bit_set(fifo_status, 4) else "No")
        print "%-20s %s" % ("Rx Full", "Yes" if Radio.is_bit_set(fifo_status, 1) else "No")
        print "%-20s %s" % ("Rx Empty", "Yes" if Radio.is_bit_set(fifo_status, 0) else "No")
        print "--------------END STATUS--------------"

    def print_config(self):
        """
        debug
        :return:
        """
        config = self.read_config()
        print "----------------CONFIG----------------"
        print "%-20s %s" % ("RX DR on IRQ", "Yes" if Radio.is_bit_set(config, 6) else "No")
        print "%-20s %s" % ("TX DS on IRQ", "Yes" if Radio.is_bit_set(config, 5) else "No")
        print "%-20s %s" % ("MAX RT on IRQ", "Yes" if Radio.is_bit_set(config, 4) else "No")
        print "%-20s %s" % ("CRC Enabled", "Yes" if Radio.is_bit_set(config, 3) else "No")
        print "%-20s %s" % ("CRC Encoding", "1 Byte" if Radio.is_bit_set(config, 2) else "2 Bytes")
        print "%-20s %s" % ("Power Status", "Powered Up" if Radio.is_bit_set(config, 1) else "Powered Down")
        print "%-20s %s" % ("Mode", "RX" if Radio.is_bit_set(config, 0) else "TX")
        print "--------------END CONFIG--------------"


