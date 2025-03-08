#!/bin/bash

PWMPIN="/dev/hat/pwm/GPIO14"
# PWMPIN="/sys/class/pwm/pwmchip3/pwm1"

# Set the PWM period and initalize duty cycle and enable
echo 1000 > "$PWMPIN/period"
echo 0 > "$PWMPIN/duty_cycle"
echo 0 > "$PWMPIN/enable"
sleep 1

# Ramp up the duty cycle from 1 to 500
for i in {1..500}; do
	echo "$i" > "$PWMPIN/duty_cycle"
	echo 1 > "$PWMPIN/enable"
	echo "$i"
        sleep 0.0005
done

# Ramp down the duty cycle from 500 to 1
for i in {500..1}; do
	echo "$i" > "$PWMPIN/duty_cycle"
	echo 1 > "$PWMPIN/enable"
	echo "$i"
	sleep 0.0005
done
