This project is the Electronic Code Simulator. The purpose of this is to simulate both
basic circuit components and microprocessors that can be programmed through AVR 
Assembler.

The project should be run through "driver.py"

The only required library is NumPy. 

The only shortcut command is '1', which will pull up a sample circuit that uses
the sample assembly code in this project. 

There are other commands such as:

'v': Changes the mode to add DC voltage
'b': Changes the mode to add AC voltage
'r': Changes the mode to add a resistor
'w': Changes the mode to add a wire
's': Changes the mode to add an oscilloscope

Currently, the only assembly commands the simulator can handle are:
and, or, ldi, in, out, mov and lsr

When creating a new microprocessor, click on the giant '+' on the side of the screen.
The # of pins must be between 18 and 76
The names of the input/output pin series must be a single uppercase letter from A-Z
An example of a valid input for the pin series is 'A C' or 'D E'.



