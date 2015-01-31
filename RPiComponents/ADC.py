"""
    @file ADC
    @module RPiComponents.ADC
    @author Jacob Calvert <jacob+info@jacobncalvert.com>
    @date January, 2015
    @brief Basic ADC control for common ADC modules

"""
import spidev


class MCP3008(object):
    """
        To get more info on why these specific bit masks are being used
        look up http://www.microchip.com/wwwproducts/Devices.aspx?dDocName=en010530
        for the datasheet and SPI specs

        Examples
        @code
            adc = MCP3008()  # all defaults
            adc.read(MCP3008.CH0)  # reads the value on channel 0 w.r.t VRef
            adc.read(MCP3008.CH0_POS_CH1_NEG)  # reads the value difference between CH0+ and CH1-

        @endcode
    """

    CH0 = 0
    CH1 = 1
    CH2 = 2
    CH3 = 3
    CH4 = 4
    CH5 = 5
    CH6 = 6
    CH7 = 7
    CH0_POS_CH1_NEG = 8
    CH1_POS_CH0_NEG = 9
    CH2_POS_CH3_NEG = 10
    CH3_POS_CH2_NEG = 11
    CH4_POS_CH5_NEG = 12
    CH5_POS_CH4_NEG = 13
    CH6_POS_CH7_NEG = 14
    CH7_POS_CH6_NEG = 15

    def __init__(self, bus_select=0, chip_select=0, freq=500000):
        """
        MCP3008 ADC chip SPI interface

        @param bus_select select the SPI bus
        @param chip_select select the chip to drive
        @param freq max frequency of the SPI interface
        """
        self._spi = spidev.SpiDev()
        self._spi.open(bus_select, chip_select)
        self._spi.max_speed_hz = freq

    def read(self, channel_mode):
        """

        @param channel_mode a variable of type MCP3008.CHx or MCP3008.CHx_POS_CHy_NEG
                defines the mode and pins used for this read
        @return int the 10 bit value from [0,1023]
        """
        if channel_mode > 7 and channel_mode < 16:
             #  a little explanation here
            #  we're sending 3 bytes
            #  the first is 00000001
            #  the second is 0 + channel bitshifted left 4
            #     i.e diff channel mode channel 0+ channel 1- makes the second byte
            #     0000 + 0 << 4 = 00000000
            #  the third byte is all 0
            #  we will get back 3 bytes, and since there is 10 bit
            #  resolution on this chip, we need to get two bits from the
            #  second part of the result and the full byte of the last
            result = self._spi.xfer([1, (channel_mode-8) << 4, 0])
            byte1 = hex(result[1])[2:]  # stripping the 0x from the front
            byte2 = hex(result[2])[2:]

            return int((byte1+byte2), 16)  # return a base-10 repr of the hex value

        elif channel_mode < 8 and channel_mode > -1:
            #  a little explanation here
            #  we're sending 3 bytes
            #  the first is 00000001
            #  the second is 1000 + channel bitshifted left 4
            #     i.e single channel mode channel 0 makes the second byte
            #     1000 + 0 << 4 = 1000000
            #  the third byte is all 0
            #  we will get back 3 bytes, and since there is 10 bit
            #  resolution on this chip, we need to get two bits from the
            #  second part of the result and the full byte of the last

            result = self._spi.xfer([1, (8+channel_mode) << 4, 0])
            byte1 = hex(result[1])[2:]  # stripping the 0x from the front
            byte2 = hex(result[2])[2:]

            return int((byte1+byte2), 16)  # return a base-10 repr of the hex value

        else:
            print "Unknown channel selection %s" % (channel_mode)

    def __del__(self):
        self._spi.close()








