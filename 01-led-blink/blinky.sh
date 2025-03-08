#!/bin/bash
while :
do
	gpioset $(gpiofind GPIO14)=1
	sleep 1
	gpioset $(gpiofind GPIO14)=0
	sleep 1
done
