#!/usr/bin/env python

import reflex
import sys

if __name__ == '__main__':

    parser = reflex.ReflexIOParser()

    parser.add_option("-i", "--input1", dest="input1")
    parser.add_option("-j", "--input2", dest="input2")

    parser.add_output("-o", "--output1", dest="output1")
    parser.add_output("-p", "--output2", dest="output2")

    inputs = parser.get_inputs()
    outputs = parser.get_outputs()

    if inputs.input1 is not None:
        outputs.output1 = inputs.input1
    else:
        outputs.output1 = 'test1'

    if inputs.input2 is not None:
        outputs.output2 = inputs.input2
    else:
        outputs.output2 = 'test2'

    raw_input("press a key:")

    parser.write_outputs()

    sys.exit()
