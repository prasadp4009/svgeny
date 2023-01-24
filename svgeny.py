#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Copyright Mon 01/23/2023  Prasad Pandit
Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
File        : svgeny.py
Author      : Prasad Pandit
Email       : prasadp4009@gmail.com
Github      : https://github.com/prasadp4009
Description : svgeny is collection of SystemVerilog code parsing tools and
              functions to easily capture the info, clean-up SystemVerilog
              files for post-processing
Usage       : The tool requires Python 3x and uses standard Python libraries
              Run command -
                python svgeny.py -h
"""

import shutil
import sys
import os
import re
import argparse
import logging
from datetime import date

toolVersion = "svgeny v0"
moduleName = "na"
dirPath = "./"
inputFileList = []
today = date.today()
parser = argparse.ArgumentParser()
logging.basicConfig(format='SVGeny: [ %(levelname)-7s ] : %(message)s', level=logging.DEBUG)

def expandFilePath(fileName: str) -> str:
  if os.path.exists(os.path.expandvars(fileName)):
    return os.path.expandvars(fileName)
  else:
    logging.error("File not found: "+fileName)
    return ""

def remove_comments(string):
  pattern = r"(\".*?\"|\'.*?\')|(/\*.*?\*/|//[^\r\n]*$)"
  # first group captures quoted strings (double or single)
  # second group captures comments (//single-line or /* multi-line */)
  regex = re.compile(pattern, re.MULTILINE|re.DOTALL)
  def _replacer(match):
      # if the 2nd group (capturing comments) is not None,
      # it means we have captured a non-quoted (real) comment string.
    if match.group(2) is not None:
      return "" # so we will return empty to remove the comment
    else: # otherwise, we will return the 1st group
      return match.group(1) # captured quoted-string
  return regex.sub(_replacer, string)

def getModuleNames(fileData: str) -> list:
  module_pattern = r"^module\s+(\w+)"
  matches = re.findall(module_pattern, fileData, re.MULTILINE|re.DOTALL)
  for match in matches:
    logging.info("Found module: "+match)
  return matches

def getParameterDict(fileData: str) -> dict:
  # parameter_pattern =
  pass

def parserSetup():
  global parser
  global toolVersion
  parser.add_argument('-v', '--version', action='version',
                      version=toolVersion, help="Show svgeny version and exit")
  parser.add_argument('-f', '--fileinput', nargs='*', metavar='<file_input>', required=True,
                      type=str, help="Add the list of files to process")
  parser.add_argument('-d', '--dirpath', nargs=1, metavar='<dir_path>',
                      type=str, help="Directory under which output should be generated. Ex. -d ./myProjects/TB. Default is present working dir.")
  return parser.parse_args()

def main():
  """
  This is a main function
  It uses no arguments and executes based on
  parser input
  """
  global inputFileList
  args = parserSetup()
  if args.fileinput:
    for eachFile in args.fileinput:
      fileCheck = expandFilePath(eachFile)
      if fileCheck:
        inputFileList.append(fileCheck)
  for eachFile in inputFileList:
    with open(eachFile, 'r') as fileToProcess:
      fileData = fileToProcess.read()
      getModuleNames(fileData)

if __name__ == "__main__":
    main()

