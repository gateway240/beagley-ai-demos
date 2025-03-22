import time
import gpiod

from gpiod.line import Bias, Direction, Value

# Multiplexer Output - Drives Columns
OUT_S0 = 5
OUT_S1 = 18
# Multiplexer Input - Driving Rows
IN_S0 = 23
IN_S1 = 24
# Multiplexer Read - Get Polled Signal High or Low
READ_LINE = 25
my_chip = "/dev/gpiochip2"

keypad = [
            [1,2,3],
            [4,5,6],
            [7,8,9],
            ['*',0,'#']
         ] 

with gpiod.Chip(my_chip) as chip:
    info = chip.get_info()
    print(f"{info.name} [{info.label}] ({info.num_lines} lines)")

print("Keypad Layout: ")
print(*keypad, sep='\n')

with gpiod.request_lines(
    my_chip,
    consumer="MATRIX_KEYPAD_DRIVER",
    config={
       # OUT_S0: gpiod.LineSettings(
       #     direction=Direction.OUTPUT,
       #     output_value=Value.ACTIVE
       # ),
        OUT_S1: gpiod.LineSettings(
            direction=Direction.OUTPUT,
            output_value=Value.ACTIVE
        ),
       # IN_S0: gpiod.LineSettings(
       #     direction=Direction.OUTPUT,
       #     output_value=Value.INACTIVE
       # ),
       # IN_S1: gpiod.LineSettings(
       #     direction=Direction.OUTPUT,
       #     output_value=Value.INACTIVE
       # ),
       # READ_LINE: gpiod.LineSettings(
       #     direction=Direction.INPUT,
       #     bias=Bias.PULL_DOWN,
       # )
    },
) as request:
    print(request)
    print("Polling Matrix Keypad!")
    while True:
        print("ON!")
       # request.set_value(OUT_S0, Value.ACTIVE)
        request.set_value(OUT_S1, Value.ACTIVE)
       # request.set_value(IN_S0, Value.ACTIVE)
       # request.set_value(IN_S1, Value.ACTIVE)
        time.sleep(1)
#        num = request.get_value(READ_LINE)
#        print(f"Num: {num}")
        print("OFF!")
        request.set_value(OUT_S1, Value.INACTIVE)
        time.sleep(1)

        # request.set_value(LINE, Value.ACTIVE)

        # time.sleep(1)
        # print("OFF!")
        # request.set_value(LINE, Value.INACTIVE)
        # time.sleep(1)
