RPiComponents is a wrapper for accessing harware functions in a better way. 

I got tired of writing gpio.output(some_pin, gpio.HIGH) a million times in a program
so I just wrapped that up into something nicer where I can now just say led.on() or led.off()

There are abstractions for many common hardware applications. To name a few:

* LEDs controlled by GPIO
* Switches with threaded interrupts
* L293D Motor controller with both PWM and basic on/off
* ADC (MCP3008 support) via SPI
* EEPROM (24CXX series support) via I2C/SMbus

The below examples are from my blog post [here](http://jacobncalvert.com/blog/post/raspberry-pi-and-gpio-updates).
To see more about my RPi stuff [visit my blog](http://jacobncalvert.com/blog/) and look for stuff with the [raspberry pi tag](http://jacobncalvert.com/blog/post/?tag=raspberry%20pi)

```python
import RPiComponents as parts
red_led_pin = 21  # using the BCM pin numbering
initial_brightness = 0  # initially off
red_led = parts.LED.FadableLED(red_led_pin, initial_brightness)
red_led.set_brightness(50)  # set the brightness to 50%
red_led.set_brightness(100) # '   '   '          '  100%
red_led.off()

motor_enable_pin = 21
motor_fwd_pin = 20
motor_rev_pin = 16


motor = parts.L293DMotor.VariableSpeedL293DMotor(motor_enable_pin, motor_fwd_pin, motor_rev_pin)
motor.enable()  # sets the motor controller enable bit to HIGH
motor.set_speed(50)  # sets the motor speed to 50% of it's max

motor.fwd()

motor.stop()

motor.rev(90)  # starts the motor in reverse at 90% of the max speed

motor.disable() # all speed and direction setting are kept but the motor will stop


def some_callback(pin_number):
    print "Called some_callback with argument %s" % (some_arg0)

        
switch_pin_number = 6

switch = parts.BasicLogic.ToggleInputCallback(switch_pin_number, callback=some_callback)

#  this adds a positive edge detection event callback on pin 6


parts.finalize()  # clean up after ourselves and reset the GPIO pins for some other use

#  now with ADC code!! Using the MicroChip MCP3008 ADC

adc = ADC.MCP3008()  # defaults to bus 0, chip 0, 500kHz operation

result = adc.read(adc.CH0)  # read the 10 bit data from CH0 in single ended operation

result = adc.read(adc.CH0_POS_CH1_NEG)  # read the 10 bit data of the range between CH0+ and CH1-

#  now with EEPROM support over I2C

e2prom_addr = 0x50
i2c_bus = 1 #  /dev/i2c-1
addr_mode = EEPROM_24CXX.BasicEEPROM.ADDRESS_MODE_16BIT
eeprom = EEPROM_24CXX.BasicEEPROM(e2prom_addr, addr_mode, i2c_bus)

eeprom.write_bytes(0, [1,2,3,4,5,6])  #  write the list of bytes to the storage device starting at storage position 0

eeprom.write_string(256, "Hello, World!!")  #  write the ASCII interpretation of the string start at position 256 

eeprom.read_string(256, len("Hello, World!!"))  #  returns the string stored at 256 and of length len(...)

eeprom.read_bytes(256, 10) # read 10 bytes from 256 -> 266


```
