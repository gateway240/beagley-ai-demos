import time
import gpiod

from gpiod.line import Direction, Value

LINE = 14
my_chip = "/dev/gpiochip2"

with gpiod.Chip(my_chip) as chip:
    info = chip.get_info()
    print(f"{info.name} [{info.label}] ({info.num_lines} lines)")

with gpiod.request_lines(
    my_chip,
    consumer="LED",
    config={
        LINE: gpiod.LineSettings(
            direction=Direction.OUTPUT, output_value=Value.ACTIVE
        )
    },
) as request:
    while True:
        print("ON!")
        request.set_value(LINE, Value.ACTIVE)
        time.sleep(1)
        print("OFF!")
        request.set_value(LINE, Value.INACTIVE)
        time.sleep(1)
