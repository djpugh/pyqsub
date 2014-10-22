#!/usr/bin/env python
"""pyqsub
=================================
Python module for running jobs on a cluster by David J Pugh (Bullard Laboratories, Department of Earth Sciences, University of Cambridge)

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

"""
import os,stat,subprocess,optparse,textwrap,glob
try:
    import argparse
    ARGPARSE=True
except:
    ARGPARSE=False
def isPath(string):
    if type(string)==list:
        for i,x in enumerate(string):
            string[i]=isPath(x)
        return string
    if not string:
        return string        
    elif ',' in string:
        #list
        files=string.lstrip('[').rstrip(']').split(',')
        for i,f in enumerate(files):
            files[i]=isPath(f)
        return files
    elif string and '*' in string and os.path.exists(os.path.abspath(os.path.split(string)[0])):
        return glob.glob(os.path.abspath(os.path.split(string)[0])+os.path.sep+os.path.split(string)[1])
    elif string and '*' not in string and os.path.exists(os.path.abspath(string)):
        if os.path.isdir(os.path.abspath(string)):
            return os.path.abspath(string)+os.path.sep
        return os.path.abspath(string)
    if ARGPARSE:
        raise argparse.ArgumentTypeError('Path: "'+string+'" does not exist')
    else:
        raise ValueError('Path: "'+string+'" does not exist')
def make_optstr(options,options_map,list_delimiter=','):
    optstr=[]
    for key in options.keys():        
        if 'qsub' in key:
            continue 
        elif key in options_map.keys() and not len(options_map[key]):
            optstr.append(str(options[key]))
        elif key in options_map.keys() and type(options[key])==list:
            optstr.append(options_map[key]+'='+list_delimiter.join(options[key]))#Is this optparse proof - works on cluster
        elif key in options_map.keys() and type(options[key])!=bool:
            optstr.append(options_map[key]+'='+str(options[key]))
        elif key in options_map.keys() and options[key]:
            optstr.append(options_map[key])
    optstr=' '.join(optstr)
    return optstr
def submit(options,options_map={},module_name=False,job_string=False,list_delimiter=','):
    """Submits job to cluster

    Creates a pbs file and submits the job to the cluster, renaming the pbs file according to the job name and job id.

    Args:
        options: dict of options and values
        options_map: dict mapping options to flags for job
        module_name: str module name for job
        list_delimiter: str value to separate lists [default=,]

    Optional Args:
        job_string: str alternate argument to options_map and module_name - provide the executable and arguments string for the qsub script itself.

    """
    if not module_name and not job_string:
        raise TypeError("One of module_name and job_string must be specified.")
    if not job_string and module_name and not len(options_map):
        raise UserWarning("job_string not specified and options_map length is 0, no option flags will be appended to the pbs script ")
    optstr=make_optstr(options,options_map,list_delimiter)
    qsub_script="#!/bin/bash\n##"+module_name.split('.')[0]+" qsub script\n#PBS -S /bin/sh\n#PBS -N "+str(options['qsub_N'])+"\n#PBS -l walltime="+str(options['qsub_walltime'])+'\n'
    qsub_script+='#PBS -V\n#PBS -l nodes='+str(options['qsub_nodes'])+':ppn='+str(options['qsub_ppn'])+'\n'
    if options['qsub_pmem']:
        qsub_script+='#PBS -l pmem='+str(int(options['qsub_pmem']))+'Gb\n'
    qsub_script+='#PBS -q '+options['qsub_q']+'\n'
    if options['qsub_M']:
        qsub_script+='#PBS -M '+options['qsub_M']+'\n#PBS -m '+options['qsub_m']+'\n'
    if job_string:
        qsub_script+=job_string
    else:
        if options.get('qsub_mpi',False): #MPI option if in options string
            qsub_script+='mpirun -n '+str(options.get('qsub_np',options['qsub_nodes']*options['qsub_ppn']))+' '
        qsub_script+='python -c "import '+module_name.split('.')[0]+'; '+module_name.split('.')[0]+'.__run__()" '+optstr+'\n'
    print 'Script:\n===============\n\n'+qsub_script
    open(options['qsub_N']+'_temp.pbs','w').write(qsub_script)
    os.chmod(options['qsub_N']+'_temp.pbs', stat.S_IRWXO| stat.S_IRWXG|stat.S_IRWXU)
    process=subprocess.Popen(["qsub",options['qsub_N']+"_temp.pbs"],stdout=subprocess.PIPE)
    out,err=process.communicate()
    print '\n===============\nSubmitted job: '+out
    os.rename(options['qsub_N']+'_temp.pbs',options['qsub_N']+'.p'+out.rstrip('\n').split('.')[0])
    return 0
def parser_group(module_name,group,default_nodes=1,default_ppn=8,default_pmem=1,default_walltime="24:00:00",default_queue="auto",*kwargs):
    """Adds parser group for qsub arguments

    Args
        module_name: str Module name for help strings and default job name.
        group: argparser argument group object generated using parser.add_argument_group() or optparse.OptionGroup object
        default_nodes: int number of nodes to use as default for qsub script (#PBS -l nodes)[default=1]
        default_ppn: int number of processors per node to use as default for qsub script (#PBS -l ppn) [default=8]
        default_pmem: float physical memory size in Gb for qsub script (#PBS -l pmem) [default=1]
        default_walltime: str default walltime string for qsub (#PBS -l walltime) [default=24:00:00]
        default_queue: str default queue to use for qsub (#PBS -q queue) [default=auto]

    Returns
        group: argparse or optparse argument group

    """ 
    if ARGPARSE:
        group.add_argument("-q","--qsub","--pbs",default=False,help="Flag to set "+module_name+" to submit to cluster",action='store_true',dest="qsub")
        group.add_argument("--nodes",default=default_nodes,help="Set number of nodes to use for job submission. [default="+str(default_nodes)+"]",type=int,dest="qsub_nodes")
        group.add_argument("--ppn",default=default_ppn,help="Set ppn to use for job submission. [default="+str(default_ppn)+"]",type=int,dest="qsub_ppn")
        group.add_argument("--pmem",default=default_pmem,help="Set pmem (Gb) to use for job submission.  [default="+str(default_pmem)+"Gb]",type=float,dest="qsub_pmem")
        group.add_argument("--email",default=False,help="Set user email address.",type=str,dest="qsub_M")
        group.add_argument("--emailoptions",default="bae",help="Set PBS -m mail options. Requires email address using -M. [default=bae]",type=str,dest="qsub_m")
        group.add_argument("--name",default=module_name,help="Set PBS -N job name options. [default="+module_name+"]",type=str,dest="qsub_N")
        group.add_argument("--walltime",default=default_walltime,help="Set PBS maximum wall time. Needs to be of the form HH:MM:SS. [default="+default_walltime+"]",type=str,dest="qsub_walltime")
        group.add_argument("--queue",default=default_queue,help="Set PBS -q Queue options. [default="+default_queue+"]",type=str,dest="qsub_q") 
        return group   
    else:
        group.add_option("-q","--qsub","--pbs",default=False,help="Flag to set "+module_name+" to submit to cluster",action='store_true',dest="qsub")
        group.add_option("--nodes",default=default_nodes,help="Set number of nodes to use for job submission. [default="+str(default_nodes)+"]",type=int,dest="qsub_nodes")
        group.add_option("--ppn",default=default_ppn,help="Set ppn to use for job submission. [default="+str(default_ppn)+"]",type=int,dest="qsub_ppn")
        group.add_option("--pmem",default=default_pmem,help="Set pmem (Gb) to use for job submission.  [default="+str(default_pmem)+"Gb]",type=float,dest="qsub_pmem")
        group.add_option("--email",default=False,help="Set user email address.",type=str,dest="qsub_M")
        group.add_option("--emailoptions",default="bae",help="Set PBS -m mail options. Requires email address using -M. [default=bae]",type=str,dest="qsub_m")
        group.add_option("--name",default=module_name,help="Set PBS -N job name options. [default="+module_name+"]",type=str,dest="qsub_N")
        group.add_option("--walltime",default=default_walltime,help="Set PBS maximum wall time. Needs to be of the form HH:MM:SS. [default="+default_walltime+"]",type=str,dest="qsub_walltime")
        group.add_option("--queue",default=default_queue,help="Set PBS -q Queue options. [default="+default_queue+"]",type=str,dest="qsub_q")   
        return group
def __run__(inputArgs=[]):
    if ARGPARSE:
        class IndentedHelpFormatterWithNL(argparse.RawDescriptionHelpFormatter):
            def _format_action(self, action):
                # determine the required width and the entry label
                help_position = min(self._action_max_length + 2,
                                    self._max_help_position)
                help_width = self._width - help_position
                action_width = help_position - self._current_indent - 2
                action_header = self._format_action_invocation(action)

                # ho nelp; start on same line and add a final newline
                if not action.help:
                    tup = self._current_indent, '', action_header
                    action_header = '%*s%s\n' % tup

                # short action name; start on the same line and pad two spaces
                elif len(action_header) <= action_width:
                    tup = self._current_indent, '', action_width, action_header
                    action_header = '%*s%-*s  ' % tup
                    indent_first = 0

                # long action name; start on the next line
                else:
                    tup = self._current_indent, '', action_header
                    action_header = '%*s%s\n' % tup
                    indent_first = help_position

                # collect the pieces of the action help
                parts = [action_header]
                # if there was help for the action, add lines of help text
                if action.help:
                    help_text = self._expand_help(action)
                    help_lines = []
                    for para in help_text.split("\n"):
                        if not len(textwrap.wrap(para, help_width)):
                            help_lines.extend(' ')
                        else:
                            help_lines.extend(textwrap.wrap(para, help_width))

                    help_lines.extend(' ')
                    help_lines.extend(' ')
                    parts.append('%*s%s\n' % (indent_first, '', help_lines[0]))
                    for line in help_lines[1:]:
                        parts.append('%*s%s\n' % (help_position, '', line))

                # or add a newline if the description doesn't end with one
                elif not action_header.endswith('\n'):
                    parts.append('\n')

                # if there are any sub-actions, add their help as well
                for subaction in self._iter_indented_subactions(action):
                    parts.append(self._format_action(subaction))

                # return a single string
                return self._join_parts(parts)
        parser=argparse.ArgumentParser(prog='pyqsub',description="Submitting a job_string script to the cluster",formatter_class=IndentedHelpFormatterWithNL)
        parser.add_argument('-j','--job_string',type=str,dest='job_string',help="job_string to submit to cluster",default=False)
        parser.add_argument('-m','--module_name',type=str,dest='module_name',help="module_name to submit to cluster",default=False)
        group=parser.add_argument_group('Cluster',description="\nCommands for  submitting to a cluster environment using qsub/PBS")
        group=parser_group(module_name='pyqsub',group=group) 
        #For testing
        if inputArgs:
            options,unknown=parser.parse_known_args(inputArgs)
        else:
            options,unknown=parser.parse_known_args()
        options=vars(options)
        options['unknown']=' '.join(unknown)
    else:
        class IndentedHelpFormatterWithNL(optparse.IndentedHelpFormatter):
            def format_description(self, description):
                if not description: return ""
                desc_width = self.width - self.current_indent
                indent = " "*self.current_indent
            # the above is still the same
                bits = description.split('\n')
                formatted_bits = [
                  textwrap.fill(bit,
                    desc_width,
                    initial_indent=indent,
                    subsequent_indent=indent)
                  for bit in bits]
                result = "\n".join(formatted_bits) + "\n"
                return result

            def format_option(self, option):
                # The help for each option consists of two parts:
                #   * the opt strings and metavars
                #   eg. ("-x", or "-fFILENAME, --file=FILENAME")
                #   * the user-supplied help string
                #   eg. ("turn on expert mode", "read data from FILENAME")
                #
                # If possible, we write both of these on the same line:
                #   -x    turn on expert mode
                #
                # But if the opt string list is too long, we put the help
                # string on a second line, indented to the same column it would
                # start in if it fit on the first line.
                #   -fFILENAME, --file=FILENAME
                #       read data from FILENAME
                result = []
                opts = self.option_strings[option]
                opt_width = self.help_position - self.current_indent - 2
                if len(opts) > opt_width:
                  opts = "%*s%s\n" % (self.current_indent, "", opts)
                  indent_first = self.help_position
                else: # start help on same line as opts
                  opts = "%*s%-*s  " % (self.current_indent, "", opt_width, opts)
                  indent_first = 0
                result.append(opts)
                if option.help:
                  help_text = self.expand_default(option)
                # Everything is the same up through here
                  help_lines = []
                  for para in help_text.split("\n"):
                    if not len(textwrap.wrap(para, self.help_width)):
                        help_lines.extend(' ')
                    else:
                        help_lines.extend(textwrap.wrap(para, self.help_width))
                  help_lines.extend(' ')
                  help_lines.extend(' ')
                # Everything is the same after here
                  result.append("%*s%s\n" % (
                    indent_first, "", help_lines[0]))
                  result.extend(["%*s%s\n" % (self.help_position, "", line)
                    for line in help_lines[1:]])
                elif opts[-1] != "\n":
                  result.append("\n")
                return "".join(result)
        parser=optparse.OptionParser(prog='pyqsub',description=description+argparsedescription,formatter_class=IndentedHelpFormatterWithNL)
        parser.add_option('-j','--job_string',type=str,help="job_string to submit to cluster",dest='job_string',default=False)
        parser.add_option('-m','--module_name',type=str,help="module_name to submit to cluster",dest='module_name',default=False)
        group=optparse.OptionGroup(parser,'Cluster',description="\nCommands for submitting to a cluster environment using qsub/PBS")
        group=parser_group(module_name='pyqsub',group=group) 
        parser.add_option_group(group)    
        if inputArgs and len(inputArgs):
            (options,args)=parser.parse_args(inputArgs)
        else:
            (options,args)=parser.parse_args()
        options=vars(options)
        if not options['job_string'] and not options['module_name']:
            parser.error("job string or module name required")
        options['unknown']=' '.join(args)
    options['qsub']=True
    if options['module_name']:
        options['qsub_N']=options['module_name']
    submit(options,{'unknown':''},options['qsub_N'],options['job_string'])
if __name__=="__main__":
    __run__()
