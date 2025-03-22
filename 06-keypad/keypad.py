import time
import gpiod

# Multiplexer Output - Drives Columns OUT_S0 = 'GPIO5'
OUT_S0 = 'GPIO5'
OUT_S1 = 'GPIO6'
# Multiplexer Input - Driving Rows IN_S0 = 'GPIO23'
IN_S0 = 'GPIO23' 
IN_S1 = 'GPIO24'
# Multiplexer Read - Get Polled Signal High or Low
READ_LINE = 'GPIO18'

keypad = [
            [1,2,3],
            [4,5,6],
            [7,8,9],
            ['*',0,'#']
         ] 
CONSUMER = 'matrix-keypad'

gpio_col_s0 = gpiod.find_line(OUT_S0)
gpio_col_s1 = gpiod.find_line(OUT_S1)
gpio_row_s0 = gpiod.find_line(IN_S0)
gpio_row_s1 = gpiod.find_line(IN_S1)
gpio_read_line = gpiod.find_line(READ_LINE)

gpio_col_s0.request(consumer=CONSUMER, type=gpiod.LINE_REQ_DIR_OUT, default_val=0)
gpio_col_s1.request(consumer=CONSUMER, type=gpiod.LINE_REQ_DIR_OUT, default_val=0)
gpio_row_s0.request(consumer=CONSUMER, type=gpiod.LINE_REQ_DIR_OUT, default_val=0)
gpio_row_s1.request(consumer=CONSUMER, type=gpiod.LINE_REQ_DIR_OUT, default_val=0)
gpio_read_line.request(consumer=CONSUMER, type=gpiod.LINE_REQ_DIR_IN, flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP,default_val = 0)

print("Keypad Layout: ")
print(*keypad, sep='\n')

def setCol(index):
    if index == 0:
        gpio_col_s0.set_value(1)
        gpio_col_s1.set_value(0)
    elif index == 1:
        gpio_col_s0.set_value(0)
        gpio_col_s1.set_value(1)
    elif index == 2:
        gpio_col_s0.set_value(1)
        gpio_col_s1.set_value(1)
    time.sleep(0.1)

def setRow(index):
    if index == 0:
        gpio_row_s0.set_value(0)
        gpio_row_s1.set_value(0)
    elif index == 1:
        gpio_row_s0.set_value(0)
        gpio_row_s1.set_value(1)
    elif index == 2:
        gpio_row_s0.set_value(1)
        gpio_row_s1.set_value(0)
    elif index == 3:
        gpio_row_s0.set_value(1)
        gpio_row_s1.set_value(1)
    time.sleep(0.1)

print("Polling Matrix Keypad!")
while True:
    rows = 4
    cols = 3
    for j in range(cols):
        setCol(j)
        for i in range(rows):
            key = keypad[i][j]
            setRow(i)
            num = gpio_read_line.get_value()
            if num == 0:
                print(f'key: {key} pushed!')
                continue
            # print(row[j])
    time.sleep(0.005)

