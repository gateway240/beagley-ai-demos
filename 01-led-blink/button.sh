#!/bin/bash
while :
do
	if (( $(gpioget --bias=pull-down $(gpiofind GPIO18)) == 0))
	then
	echo ”Button Pressed!”
	fi
done
