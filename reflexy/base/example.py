#!/usr/bin/env python

# import reflex module
import reflex

import sys

if __name__ == '__main__':

    # create an option parser
    parser = reflex.ReflexIOParser()

    # define inputs (Note: you must define at least long option)
    parser.add_input("-i", "--input1")
    parser.add_input("-j", "--input2")

    # define outputs (Note: you must define at least long option)
    parser.add_output("-o", "--output1")
    parser.add_output("-p", "--output2")

    # get inputs from the command line
    inputs = parser.get_inputs()
    # get output variables
    outputs = parser.get_outputs()

    # read inputs and assign outputs
    if hasattr(inputs, "input1"):
        outputs.output1 = inputs.input1
    else:
        outputs.output1 = 'test1'

    if hasattr(inputs, "input2"):
        outputs.output2 = inputs.input2
    else:
        outputs.output2 = 'test2'

    # print outputs
    parser.write_outputs()

    sys.exit()
