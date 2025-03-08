#!/bin/bash
while :
do
	if (( $(gpioget --bias=pull-up $(gpiofind GPIO18)) == 0))
	then
		gpioset $(gpiofind GPIO14)=1
	else
		gpioset $(gpiofind GPIO14)=0
	fi
done
