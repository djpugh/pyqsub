"""pyqsub
=================================
Python module for running jobs on a cluster by David J Pugh

This module allows any python module to be easily submitted to run on a cluster or any other job. It provides basic python wrappers for qsub and a parser group for argparse or optparse.

How To Use
*********************************
This module is designed to be included in other modules to handle interacting with a cluster. There are two parts to the module:

    1. The parser_group() function, which returns either an argparse or optparse parser group object, depending on the value of ARGPARSE, with the correct flags and destinations for the submit function.
    2. The submit() function which uses subprocess to submit a pbs script to the cluster using qsub. 

parser_group()
---------------------------------
This function requires an appropriate parser group object depending on the value of ARGPARSE. It then adds arguments with default values as set in the function call for handling qsub jobs.

To include this in your code using argparse, add the following two lines to the end of your parser code::

    group=parser.add_argument_group('Cluster',description="\nCommands for using module_name on a cluster environment using qsub/PBS")
    group=qsub.parser_group(module_name='module_name',group=group,default_nodes=default_nodes,default_ppn=default_ppn,default_pmem=default_pmem,default_walltime=default_walltime,default_queue=default_queue) 

Using optparse::        

    group=optparse.OptionGroup(parser,'Cluster',description="\nCommands for using  module_name on a cluster environment using qsub/PBS")
    group=qsub.parser_group(module_name='module_name',group=group,default_nodes=default_nodes,default_ppn=default_ppn,default_pmem=default_pmem,default_walltime=default_walltime,default_queue=default_queue) 

Each of the options is prefixed by qsub (e.g. qsub_nodes for the nodes argument).

submit()
---------------------------------
This function requires a dictionary of the options and the dictionary of the mappings of the option names to the command line flags (options_map). The options_map can be easily generated using an argparse parser::
    
    options_map={}
    for option in parser._actions:
        if len(option.option_strings):
            i=0
            while i<len(option.option_strings) and '--' not in option.option_strings[i]:
                i+=1
            options_map[option.dest]=option.option_strings[i]

or for an optparse parser::
    
    options_map={}
    for option in parser.option_list:
        options_map[option.dest]=option.get_opt_string()
    
This returns an option_map that works between parsers using the longform flags --exampleflag (required for parser flags too)

submit() uses the options and options_map along with the module_name to create a pbs file to run module_name from the command line using module_name.__run__().
So the target module must have a method called __run__() that can act on sys.argv to parse and run the arguments.

All flags containing qsub are ignored in constructing the script, but all other options that are in the option_map are used.

submit() can take job_string as an argument instead. This is a custom job strings for the pbs script, allowing non-python programs to use the module as a simple wrapper function, or to be otherwise integrated.
In this case, the options argument needs to contain the qsub options and the options_map argument can be a blank delimiter, while the module_name corresponds to the desired default job_name.

This aspect of pyqsub can be called from the command line, try pyqsub -h for help.

-------------------------------------------

Copyright (c) 2015 David J Pugh

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS 
IN THE SOFTWARE.

"""
from __core__ import __run__,parser_group
if __name__=="__main__":
    __run__()