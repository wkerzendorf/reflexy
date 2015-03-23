# This file is part of Reflex
# Copyright (C) 2010 European Southern Observatory
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import optparse
from gettext import gettext as _
import re
import sys
import json
import os

try:
    import pyfits

    def evalChecksum(filename):
        (mode, ino, dev, nlink, uid, gid, size,
         atime, mtime, ctime) = os.stat(filename.name)
        checksum = str(mtime*1000) + str(
            size)  # times 1000 to be compatible with java
        header = pyfits.open(filename.name)[0].header
        md5 = header.get('DATAMD5')
        if md5 is not None:
            checksum = checksum + str(md5).strip()
        cksum = header.get('CHECKSUM')
        if cksum is not None:
            checksum = checksum + str(cksum).strip()
            datasum = header.get('DATASUM')
            if datasum is not None:
                checksum = checksum + str(datasum).strip()
        return checksum
except:
    def evalChecksum(filename):
        return None


def parseSof(sof):
    """
    This method parses the SoF passed on the command line to
    a SetOfFiles object
    A Set of files include a number of FitsFiles objects and a
    dataset name.
    The format for sof is an ASCII format like this:
    datasetname|file1.fits;PRO_CATG1;PURPOSE1:PURPOSE2,file2;PRO_CAT2;PURPOSE1
    Use this method to parse a command line option which contains a sof.
    """
    files = list()
    dataset_name = sof[:sof.index('|')]
    only_sof = sof[sof.index('|')+1:]
    if len(only_sof) == 0:
        return SetOfFiles(dataset_name, files)
    sof_splitted = only_sof.split(',')
    for frame in sof_splitted:
        name = frame[0:frame.find(";")]
        category = frame[(frame.find(";")+1):(frame.rfind(";"))]
        purposes = frame[(frame.rfind(";"))+1:].split(':')
        files.append(FitsFile(name, category, None, purposes))
    return SetOfFiles(dataset_name, files)


def parseSofJson(sof):
    """
    This method parses the SoF passed by the PythonActor (in JSON format) to
    a SetOfFiles object.
    Use this method if the sof comes from within Reflex.
    """
    files = list()
    for f in sof['files']:
        files.append(FitsFile(f['name'], f['category'],
                              f['checksum'], f['purposes']))
    return SetOfFiles(sof['datasetName'], files)


def parseSop(sop_text):
    """
    This method parses the SoP passed on the command line to
    a list of parameters
    """
    p = re.compile('(.*):(.*)=(.*)')
    sop = list()
    sop_splitted = sop_text.split(',')
    for parameter in sop_splitted:
        m = p.match(parameter)
        if m is None:
            raise Exception("Token is not a valid parameter: " + parameter)
        else:
            param_recipe = m.group(1)
            param_displayname = m.group(2)
            param_value = m.group(3)
        sop.append(RecipeParameter(param_recipe,
                                   param_displayname, "", "",
                                   value=param_value))
    return sop


def parseSopJson(sop):
    """
    This method parses the SoP passed by the PythonActor to
    a list of parameters
    """
    params = list()
    for p in sop:
        params.append(RecipeParameter(displayName=p['display_name'],
                                      name=p.get('name', None),
                                      description=p.get('description', None),
                                      recipe=p['recipe'],
                                      value=p.get('value', None)))

    return params


class SetOfFiles:
    """
    Simple class that contains information about a set of files,
    its category and the dataset name they belong to.
    """

    def __init__(self, datasetName, files):
        self.datasetName = datasetName
        self.files = files

    def __len__(self):
        return len(self.files)

    def __eq__(self, other):
        return isinstance(other, SetOfFiles) and \
               vars(self) == vars(other)

    def toJSON(self):
        ret = dict()
        ret['class'] = 'org.eso.domain.SetOfFiles'
        ret['datasetName'] = self.datasetName
        ret['files'] = [f.toJSON() for f in self.files]
        return ret

    def __str__(self):
        val = 'Dataset Name: ' + self.datasetName + ', Files: '
        val += ', '.join(map(str, self.files))
        return val


class FitsFile:
    """
    Simple class that contains information about the filename
    and its category
    """

    def __init__(self, name, category, checksum=None, purposes=None):
        if purposes is None:
            purposes = list()
        self.name = name
        self.category = category
        self.purposes = purposes
        self.checksum = checksum

    def __eq__(self, other):
        return isinstance(other, FitsFile) and \
               vars(self) == vars(other)

    def toJSON(self):
        ret = dict()
        ret['class'] = 'org.eso.domain.FitsFile'
        ret['name'] = self.name
        ret['category'] = self.category
        ret['purposes'] = self.purposes
        ret['checksum'] = self.checksum
        return ret

    def __str__(self):
        return 'Name: ' + self.name + ', Category: ' + self.category


class RecipeParameter:
    """
    Simple class that contains the definition of a recipe parameter
    """

    def __init__(self, recipe="", displayName="", name="", group="",
                 description="", value=""):
        self.recipe = recipe
        self.displayName = displayName
        self.name = name
        self.group = group
        self.description = description
        self.value = value

    def __eq__(self, other):
      return isinstance(other, RecipeParameter) and \
             vars(self) == vars(other)

    def toJSON(self):
        ret = dict()
        ret['class'] = 'org.eso.domain.RecipeParameter'
        ret['display_name'] = self.displayName
        ret['name'] = self.name
        ret['description'] = self.description
        ret['recipe'] = self.recipe
        ret['value'] = self.value
        return ret

    def __str__(self):
        return 'Name: ' + self.recipe + "." + self.displayName + ', Group: ' + self.group + ', Value : ' + self.value


class Logger(object):
    """
    Logger that writes both on terminal and on file
    """

    def __init__(self, file, filename):
        self.terminal = file
        self.log = open(filename, "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def writelines(self, messages):
        self.terminal.write(messages)
        self.log.write(messages)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.terminal.close()
        self.log.close()

class OutputParser(optparse.OptionParser):
    """
    Extension of the OptionParser that allows to define "outputs"
    """

    def format_option_help(self, formatter=None):
        if formatter is None:
            formatter = self.formatter
        formatter.store_option_strings(self)
        result = []
        result.append(formatter.format_heading(_("outputs")))
        formatter.indent()
        if self.option_list:
            options = optparse.OptionContainer.format_option_help(
                self, formatter)
            options = re.sub('.*--help.*\n', '', options)
            result.append(options)
            result.append("\n")
        for group in self.option_groups:
            result.append(group.format_help(formatter))
            result.append("\n")
        formatter.dedent()
        # Drop the last "\n", or the header if no options or option groups:
        return "".join(result[:-1])

    def format_help(self, formatter=None):
        if formatter is None:
            formatter = self.formatter
        result = ['\n']
        result.append(self.format_option_help(formatter))
        return "".join(result)



class ReflexParameters:
    """
    Simple class used to store Reflex parameters
    """
    pass



class ReflexEncoder(json.JSONEncoder):
    """
    Class used to convert Reflex objects into JSON objects
    """

    def default(self, obj):
        if isinstance(obj, (SetOfFiles, FitsFile, RecipeParameter)):
            return obj.toJSON()
        return json.JSONEncoder.default(self, obj)



class ReflexIOParser(optparse.OptionParser):
    """
    Extension of the OptionParser that includes and OutputParser
    for defining outputs
    """

    reserved_pars = ['input_parameters_file',
                     'output_parameters_file', 'stdout_file']

    def __init__(self):
        optparse.OptionParser.__init__(self)

        self.output_parser = OutputParser()

        self.add_option(
            "--input-parameters-file", dest="input_parameters_file")
        self.add_option(
            "--output-parameters-file", dest="output_parameters_file")

        self.add_option("--products-dir", dest="products_dir")

        # reserved option used for interactive mode of the PythonActor
        self.add_option("--stdout-file", dest="stdout_file")
        self.add_option("--stderr-file", dest="stderr_file")

    def format_help(self, formatter=None):
        help = optparse.OptionParser.format_help(self, formatter)
        help += self.output_parser.format_help(formatter)
        return help

    def add_input(self, *args, **kwargs):
        self.add_option(*args, **kwargs)

    def add_output(self, *args, **kwargs):
        self.output_parser.add_option(*args, **kwargs)

    def get_inputs(self):
        # our parameters: the evaluation order is:
        # default value, configuration file, command line
        pars = ReflexParameters()

        # extract the default values
        for key, value in self.defaults.iteritems():
            if value is not None:
                setattr(pars, key, value)
                # we reset the defaults in order to know if a command line
                # argument was passed
                self.defaults[key] = None

        # parse the command line
        self.parse_args()

        # replace standard error and output if needed
        if self.values.stdout_file is not None:
            sys.stdout = Logger(sys.stdout, self.values.stdout_file)
        if self.values.stderr_file is not None:
            sys.stderr = Logger(sys.stderr, self.values.stderr_file)

        # collect a list of valid command line options
        valid_options = list()
        for option in self.option_list:
            if not option.dest in self.reserved_pars:
                valid_options.append(option.dest)

        # read parameters from input file
        if self.values.input_parameters_file is not None:
            input_file_pars = json.load(open(
                self.values.input_parameters_file), encoding='ascii')
            for key, value in input_file_pars.items():
                if key in valid_options:
                    if isinstance(value, str) or isinstance(value, unicode):
                        setattr(pars, key.encode(
                            'ascii'), value.encode('ascii'))
                    else:
                        # try to convert to Reflex objects
                        try:
                            jObj = parseSofJson(value)
                            setattr(pars, key.encode('ascii'), jObj)
                        except:
                            try:
                                jObj = parseSopJson(value)
                                setattr(pars, key.encode('ascii'), jObj)
                            except:
                                setattr(pars, key.encode('ascii'), value)
                else:
                    # fatal: invalid option
                    sys.stderr.write(
                        self.values.input_parameters_file + 
                        ": error: no such option: " + str(key) + "\n")
                    sys.exit(-1)

        # take command line options
        for key in dir(self.values):
            if key in valid_options:
                value = getattr(self.values, key)
                # if defined, overwrite the value in the input file
                if value is not None:
                    # try to convert to Reflex objects
                    try:
                        pVal = parseSof(value)
                        setattr(pars, key, pVal)
                    except:
                        try:
                            pVal = parseSop(value)
                            setattr(pars, key, pVal)
                        except:
                            setattr(pars, key, value)

        return pars

    def get_outputs(self):
        try:
            self.outputs
        except:
            self.outputs = self.output_parser.parse_args([])[0]
        return self.outputs

    def write_outputs(self):
        params = dict()
        for option in self.output_parser.option_list:
            if option.dest is not None and \
                self.outputs.__dict__[option.dest] is not None:
                params[option.dest] = self.outputs.__dict__[option.dest]

        if self.values.output_parameters_file is None:
            print json.dumps(params, sort_keys=True,
                             indent=2, encoding='ascii', cls=ReflexEncoder)
        else:
            out_file = open(self.values.output_parameters_file, 'w')
            json.dump(params, out_file, sort_keys=True,
                      indent=2, encoding='ascii', cls=ReflexEncoder)
            out_file.close()
