# NextDraw GCode Reader

Adapted from `andymasteroffish/axidraw_gcode_reader`

This repo consists of 2 python scripts to help me use my NextDraw 2234 plotter with G-code files.  
To install the NextDraw python lib run this:

```
python3 -m pip install https://software-download.bantamtools.com/nd/api/nextdraw_api.zip
```

https://bantam.tools/nd_py/#options-interactive

## reader.py

| Flag   | Default Value | Description                                                                                                               |
| ------ | ------------- | ------------------------------------------------------------------------------------------------------------------------- |
| -scale | 1             | multiplier for print scale 1=A4, 2=A3, 3=A2, 4=A1                                                                         |
| -mode  |               | handling mode (1-4) - acts as presets for `acc`, `s`, `m` values (but specifying those values will still take precedence) |
| -acc   | 50            | acceleration (1-100) minimum of 35 recommended                                                                            |
| -s     | 60            | drawing speed (1-100) - speed while pen is down                                                                           |
| -m     | 85            | movement speed (1-100) - speed while pen is up                                                                            |
| -pdh   | 42            | pen down height (1-100) - lower is closer to the ground                                                                   |
| -pds   | 10            | pen down speed (1-100) - lower is slower                                                                                  |
| -puh   | 60            | pen up height (1-100) - lower is closer to the ground                                                                     |
| -pus   | 30            | pen up speed (1-100) - lower is slower                                                                                    |
| -h     | n/a           | help (prints all of the arguments)                                                                                        |

Notes for the 'mode' (aka handling) arg:  
https://bantam.tools/nd_py/#handling  
1 - Technical drawing  
2 - Handwriting  
3 - Sketching  
4 - Constant speed

Generally I'll use mode 4 and increase the draw speed e.g.

```
python3 reader.py ~/Projects/canvas-gcode/gcode/boids12-forcefield.nc -scale 1 -mode 4 -s 60
```

## mover.py

Used for calibration.

`python3 mover.py`

Use keyboard arrows to move the plotter head.  
Use space to toggle pen up/down.  
Use `q` to quit.  
Press enter after any of the above to send the command.
