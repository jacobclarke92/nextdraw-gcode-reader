'''
https://axidraw.com/doc/py_api/

#TODO
[X] show percentage complete
[X] scaling options
[ ] a way to pause
[X] show times in HH:MM:SS



Commands to read:

M3 S# - set the pen height. 0 is up, 100 is max down (60 is probably better)
	(for this, I think anything above 0 can just be down)
G1 X# Y# - go to the given point
G0 X# Y# - go to the given point a fast as possible (not sure you need this either)

'''



import sys
import time
import re


# from pyaxidraw import axidraw
from nextdraw import NextDraw

#values
file_name = "NONE"
scale_factor = 1

#https://axidraw.com/doc/py_api/#speed_pendown
pen_down_speed = 25
pen_up_speed = 75
pen_down_height = 42  #axidraw default is 40
#https://axidraw.com/doc/py_api/#const_speed
use_const_speed = False
#https://axidraw.com/doc/py_api/#pen_delay_up
pen_up_delay = 100

#https://axidraw.com/doc/py_api/#pen_rate_lower
pen_rate_lower = 20
pen_rate_raise = 75

num_copies = 1
copies_spacing = 2.7

show_progress = True

def print_arguments():
	print("-scale : multiplier for print scale")
	print("-s or -speed : pen down speed")
	print("-up_speed : pen up speed")
	print("-const : move at constant speed")
	print("-pos_down : pen down height (0-100)  (lower numbers = lower pen, default 45)")
	print("-c or -copies: number of copies (horizontally)")
	print("-cs : copy spacing (horizontally in inches)")
	print("-text : slow setting for text (overrides -s, -up_speed, -pos_down, -pen_up_delay)")
	print("-d : pen up delay in millis (-500, 500)")
	print("-rl pen rate lower (1 to 100")
	print("-rr pen rate raise (1 to 100")
	print("-hp hide progress text")
	print("-h or -help: help")


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

	#first argument should always be file name
	file_name = sys.argv[1]

	if file_name == '-h' or file_name == '-help':
		print_arguments()
		sys.exit();

	print("opening ", file_name)

	#after that it could be a mix of commands
	i = 2
	while i < len(sys.argv):
		arg = sys.argv[i]
		if (i < len(sys.argv) - 1):
			val = sys.argv[i+1]
		i += 2
		#print("arg:",arg,"  val:",val)
		if arg == "-scale":
			scale_factor = float(val)

		elif arg == "-text":
			pen_down_speed = 3
			pen_up_speed = 10
			pen_down_height = 43
			pen_up_delay = 100
			i -= 1

		elif arg == "-s" or arg == "-speed":
			pen_down_speed = float(val)

		elif arg == "-up_speed":
			pen_up_speed = float(val)

		elif arg == "-pos_down":
			pen_down_height = float(val)

		elif arg == "-const":
			use_const_speed = True
			i -= 1	#no value for this option

		elif arg == "-d":
			pen_up_delay = int(val)

		elif arg == "-rl":
			pen_rate_lower = int(val)

		elif arg == "-rr":
			pen_rate_raise = int(val)

		elif arg == "-c" or arg == "-copeis":
			num_copies = int(val)

		elif arg == "-cs":
			copies_spacing = float(val)

		elif arg == "-hp":
			show_progress = False
			i -= 1	#no value for this option

		elif arg == "-h" or arg == "-help":
			print_arguments()
			sys.exit();

		

		else:
			print("i don't know this command:",arg)
			sys.exit();
		

print("scale: ",scale_factor)
print("pen down speed: ",pen_down_speed)
print("pen up speed: ",pen_up_speed)
print("use constant speed: ",use_const_speed)
print("pen down height: ",pen_down_height)
print("pen up delay: ",pen_up_delay)
print("pen rate raise: ",pen_rate_raise)
print("pen rate lower: ",pen_rate_lower)
print("copies: ",num_copies)
print("copies spacing: ",copies_spacing)


def parse_gcode_line(line):
	# Remove comments (text within parentheses)
	line_without_comments = re.sub(r'\(.*?\)', '', line).strip()

	# If line is empty after removing comments, return None
	if not line_without_comments:
		return None

	# Split the line into parts
	parts = line_without_comments.split()

	# Extract the command (first part)
	if not parts:
		return None

	command = parts[0]

	# Create a dictionary to store parameters
	params = {"command": command}

	# Parse remaining parameters
	for part in parts[1:]:
		# Match parameter with its value (e.g., P250, X281)
		match = re.match(r'([A-Z])(\d+(?:\.\d+)?)', part)
		if match:
			param_name = match.group(1)
			param_value = float(match.group(2))
			params[param_name] = param_value
	
	return params



#do our thing
file = open(file_name)
file_lines = file.readlines()
print("lines: ",len(file_lines))

nd1 = NextDraw()
nd1.interactive()
nd1.options.model = 10  # Bantam Tools NextDraw™ 2234

if not nd1.connect():         # Open serial port to NextDraw;
	print("not connected")
	quit()

nd1.options.units=2 # mm
nd1.options.speed_pendown = pen_down_speed
nd1.options.speed_penup = pen_up_speed
nd1.options.const_speed = use_const_speed
nd1.options.pen_pos_down = pen_down_height
nd1.options.pen_delay_up = pen_up_delay
nd1.options.pen_rate_lower = pen_rate_lower
nd1.options.pen_rate_raise = pen_rate_raise

nd1.update() # set the options

nd1.penup()

start_time = time.time()

pen_down = False
line_count = 0

for copy_id in range(0, num_copies):

	x_offset = copy_id * copies_spacing

	for this_line in file_lines:
		line_count += 1
		prc = float(line_count) / float(len(file_lines) * num_copies)
		elapsed_time = time.time() - start_time
		time_left = (elapsed_time / prc) - elapsed_time

		progress_str = str(int(prc*100))
		if show_progress:
			print ("progress: " + progress_str + "  time: " + seconds2time(elapsed_time) + "  estimated time left: " + seconds2time(time_left))

		#print(this_line[0:-1])	#chopping off the last character because it is a newlien char

		params = parse_gcode_line(this_line)

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
			x_val = params["X"]
			y_val = params["Y"]

			nd1.goto(x_val+x_offset, y_val)


	#cleanup
	nd1.penup()
	
nd1.moveto(0,0)
nd1.disconnect()











