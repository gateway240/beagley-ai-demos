#!/bin/bash
while :
do
	if (( $(gpioget --bias=pull-up $(gpiofind GPIO18)) == 0))
	then
	echo ”Button Pressed!”
	fi
done
