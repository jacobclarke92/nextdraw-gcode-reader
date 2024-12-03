import os
import sys

# from pyaxidraw import axidraw
from nextdraw import NextDraw


print('Starting move tool. Press enter after each command')
print('Arrows - move')
print('Space - pen up/down')
print('Q - quit')

python_version = sys.version_info[0]
# print("python version: "+str(python_version))

keepGoing = True
moveDist = 10.0
penUpHeight = 60
penDownHeight = 42
penDown = False


#get arguments
if (len(sys.argv) >= 2):
    i=1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        val = sys.argv[i+1]
        i += 2
        #print("arg:",arg,"  val:",val)
        if (arg == "-d"):
            moveDist = float(val)

        if (arg == "-pos_down"):
            penDownHeight = float(val)

        if (arg == "-h"):
            print("-d : move distance")
            print("-pos_down : pen down position (lower numbers = lower pen, default 45)")
            sys.exit()


print("move dist "+str(moveDist))
print("pen down height "+str(penDownHeight))

#connect axidraw
nd1 = NextDraw()
nd1.interactive()
nd1.options.model=10  # Bantam Tools NextDraw™ 2234

if not nd1.connect():         # Open serial port to NextDraw;
    print("not connected")
    quit()

nd1.options.units=2 # mm
nd1.options.pen_pos_down = penDownHeight
nd1.options.pen_pos_up = penUpHeight

nd1.update() # set the options

nd1.penup()

while(keepGoing):
    if python_version >= 3:
        inp = input()
    else:
        inp = raw_input()
    
    if inp == "q":
        keepGoing = False

    if inp == " ":
        print("space")
        penDown = not penDown
        if penDown:
            nd1.pendown()
        else:
            nd1.penup()

    if inp == 'h':
        nd1.penup()
        nd1.goto(0,0)

    #check for arrows by converting chars to int
    if ord(inp[0]) == 27:
        #up
        if ord(inp[2]) == 65:
            nd1.go(0,-moveDist)

        #down
        if ord(inp[2]) == 66:\
            nd1.go(0,moveDist)

        #right
        if ord(inp[2]) == 67:
            nd1.go(moveDist,0)

        #left
        if ord(inp[2]) == 68:
            nd1.go(-moveDist,0)

nd1.disconnect()