import sys
import time
import re


# from pyaxidraw import axidraw
from nextdraw import NextDraw

#defaults
defaultAcceleration = 50
defaultDrawingSpeed = 60
defaultMovingSpeed = 85
defaultPenDownHeight = 42
defaultPenDownSpeed = 10
defaultPenUpHeight = 60
defaultPenUpSpeed = 30

#values
fileName = "NONE"
scaleFactor = 1

offsetX = 0
offsetY = 0

penDownHeight = defaultPenDownHeight  	# https://bantam.tools/nd_py/#pen_pos_down
penDownSpeed = defaultPenDownSpeed		# https://bantam.tools/nd_py/#pen_rate_lower
penUpHeight = defaultPenUpHeight		# https://bantam.tools/nd_py/#pen_pos_up
penUpSpeed = defaultPenUpSpeed			# https://bantam.tools/nd_py/#pen_rate_raise

acceleration = defaultAcceleration 		# https://bantam.tools/nd_py/#accel
drawingSpeed = defaultDrawingSpeed		# https://bantam.tools/nd_py/#speed_pendown
movingSpeed = defaultMovingSpeed		# https://bantam.tools/nd_py/#speed_penup

handling = 0			# https://bantam.tools/nd_py/#handling
# 1 - Technical drawing.
# 2 - Handwriting
# 3 - Sketching
# 4 - Constant speed

showProgress = True

def print_arguments():
	print("-scale : multiplier for print scale (1=A4, 2=A3, etc)")
	print("-mode : handling mode (1-4) overwrites values for acc, s, m")
	print("-acc : acceleration (1 - 100)")
	print("-s : drawing speed (1 - 100)")
	print("-m : moving speed (1 - 100)")
	print("-pdh : pen down height (0 - 100)  (lower numbers = lower pen, default 42)")
	print("-pds : pen down speed (1 - 100)")
	print("-puh : pen up height (0 - 100)  (lower numbers = lower pen, default 60)")
	print("-pus : pen up speed (1 - 100)")
	print('-ox : offset x')
	print('-oy : offset y')
	
	print("-hp : hide progress text")
	print("-h : help")


def seconds2time(raw):

	hours = 0
	minutes = 0
	seconds = 0

	while raw > 3600:
		hours += 1
		raw -= 3600

	while raw > 60:
		minutes += 1
		raw -= 60

	seconds = raw


	min_s = str(minutes)
	if minutes < 10:
		min_s = "0"+str(minutes)

	sec_s = str(int(seconds))
	if seconds < 10:
		sec_s = "0" + str(int(seconds))

	return str(hours) + ":" + min_s + ":" + sec_s

	
#get arguments
if (len(sys.argv) >= 2):

	# first argument should always be file name
	fileName = sys.argv[1]

	if fileName == '-h' or fileName == '-help':
		print_arguments()
		sys.exit();

	print("opening ", fileName)

	#after that it could be a mix of commands
	i = 2
	while i < len(sys.argv):
		arg = sys.argv[i]
		if (i < len(sys.argv) - 1):
			val = sys.argv[i+1]
		i += 2
		#print("arg:",arg,"  val:",val)
		if arg == "-scale":
			scaleFactor = float(val)

		elif arg == "-mode":
			handling = int(val)

		elif arg == "-acc":
			acceleration = float(val)

		elif arg == "-s":
			drawingSpeed = float(val)
		
		elif arg == "-m":
			movingSpeed = float(val)

		elif arg == "-pds":
			penDownSpeed = float(val)

		elif arg == "-pus":
			penUpSpeed = float(val)

		elif arg == "-pdh":
			penDownHeight = float(val)
		
		elif arg == "-puh":
			penUpHeight = float(val)

		elif arg == "-hp":
			showProgress = False
			i -= 1	#no value for this option

		elif arg == "-ox":
			offsetX = float(val)

		elif arg == "-oy":
			offsetY = float(val)

		elif arg == "-h" or arg == "-help":
			print_arguments()
			sys.exit();

		else:
			print("i don't know this command:",arg)
			sys.exit();
		

print("scale: ", scaleFactor)
print("handling mode: ", handling)
print("acceleration: ", acceleration)
print("drawing speed: ", drawingSpeed)
print("moving speed: ", movingSpeed)
print("pen down speed: ", penDownSpeed)
print("pen down height: ", penDownHeight)
print("pen up speed: ", penUpSpeed)
print("pen up height: ", penUpHeight)


def parseGCodeLine(line):
	# Remove comments (text within parentheses)
	lineWithoutComments = re.sub(r'\(.*?\)', '', line).strip()

	# If line is empty after removing comments, return None
	if not lineWithoutComments:
		return None

	# Split the line into parts
	parts = lineWithoutComments.split()

	# Extract the command (first part)
	if not parts:
		return None

	command = parts[0]

	# Create a dictionary to store parameters
	params = {"command": command}

	# Parse remaining parameters
	for part in parts[1:]:
		# Match parameter with its value (e.g., P250, X281)
		match = re.match(r'([A-Z])(-?\d+(?:\.\d+)?)', part)
		if match:
			paramName = match.group(1)
			paramValue = float(match.group(2))
			params[paramName] = paramValue
	
	return params



#do our thing
file = open(fileName)
fileLines = file.readlines()
print("lines: ", len(fileLines))

nd1 = NextDraw()
nd1.interactive()

if not nd1.connect():         # Open serial port to NextDraw;
	print("not connected")
	quit()

nd1.options.model = 10  # Bantam Tools NextDraw™ 2234
nd1.options.units = 2 # mm

if handling > 0:
	nd1.options.handling = handling
	if drawingSpeed != defaultDrawingSpeed:
		nd1.options.speed_pendown = drawingSpeed
	if movingSpeed != defaultMovingSpeed:
		nd1.options.speed_penup = movingSpeed
	if acceleration != defaultAcceleration:
		nd1.options.accel = acceleration
else:
	nd1.options.accel = acceleration
	nd1.options.speed_pendown = drawingSpeed
	nd1.options.speed_penup = movingSpeed

nd1.options.pen_pos_down = penDownHeight
nd1.options.pen_pos_up = penUpHeight
nd1.options.pen_rate_lower = penDownSpeed
nd1.options.pen_rate_raise = penUpSpeed

nd1.update() # set the options

nd1.penup()
startTime = time.time()
lineCount = 0


for this_line in fileLines:
	lineCount += 1
	prc = float(lineCount) / float(len(fileLines))
	elapsedTime = time.time() - startTime
	timeLeft = (elapsedTime / prc) - elapsedTime

	progressStr = str(int(prc*100))
	if showProgress:
		print ("progress: " + progressStr + "  time: " + seconds2time(elapsedTime) + "  estimated time left: " + seconds2time(timeLeft))

	params = parseGCodeLine(this_line)

	if params == None:
		continue

	cmd = params["command"]
	
	if cmd == "M3" or cmd == "M03":
		nd1.pendown()

	if cmd == "M5" or cmd == "M05":
		nd1.penup()

	if cmd == "G4" or cmd == "G04":
		ms = params["P"]
		time.sleep(ms/1000)

	if cmd == "G0" or cmd == "G1":
		#we need X and Y
		xVal = offsetX + params["X"] * scaleFactor
		yVal = offsetY + params["Y"] * scaleFactor

		nd1.goto(xVal, yVal)


#cleanup
nd1.penup()
	
nd1.moveto(0,0)
nd1.disconnect()











