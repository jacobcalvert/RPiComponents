RPiComponents is a wrapper for common applications in the RPi.GPIO library.

I got tired of writing gpio.output(some_pin, gpio.HIGH) a million times in a program
so I just wrapped that up into something nicer where I can now just say led.on() or led.off()

I have some ADC code for the MCP3008 ADC from MicroChip to put up where I bit-bang the SPI interface
to get data from it. The below examples are from my blog post [here](http://jacobncalvert.com/blog/post/raspberry-pi-and-gpio-updates).
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


def some_callback(some_arg0):
    print "Called some_callback with argument %s" % (some_arg0)

        
switch_pin_number = 6

switch = parts.Switch.ThreadedCallbackSwitch(switch_pin_number, callback=some_callback, callback_args=[1,2,3])

switch.start()

#  calling switch.start() starts a monitor thread that waits for a rising or falling edge
#  due to the switch changing state, it will then fire off callback with the arguments given
#  or if callback_args is None, it will simply call the callback

switch.stop()

#  switch.stop() properly terminates the monitor thread

parts.finalize()  # clean up after ourselves and reset the GPIO pins for some other use
```