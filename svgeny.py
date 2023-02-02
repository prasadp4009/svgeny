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
  parameterDict ={}
  parameter_pattern = r"\s*#\(([^\)]+)\)"
  matches = re.findall(parameter_pattern, fileData, re.MULTILINE|re.DOTALL)
  logging.info(matches)
  return parameterDict

def getParameterDictForModule(module_name: str, fileData: str) -> dict:
  parameterDict ={}
  parameter_pattern = fr"{module_name}\s*#\(([^\)]+)\)"
  matches = re.findall(parameter_pattern, fileData, re.MULTILINE|re.DOTALL)
  if matches:
    parameterString = matches[0].replace("parameter","")
    parameterString = parameterString.strip()
    parameterList = parameterString.split(',')
    parameterList = [eachParam.strip() for eachParam in parameterList]
    for eachParam in parameterList:
      parameterName = ""
      parameterValue = ""
      parameterType = ""
      if "=" in eachParam:
        parameterName, parameterValue = eachParam.split("=")
        parameterName = parameterName.strip()
        parameterValue = parameterValue.strip()
        if " " in parameterName:
          parameterType, parameterName = parameterName.split()
      else:
        parameterName = eachParam
        if " " in parameterName:
          parameterType, parameterName = parameterName.split()
      parameterDict[parameterName] = {"type" : parameterType, "value": parameterValue}
      logging.info(f"Parameter Found in {module_name} -> Name: {parameterName}, Value: {parameterValue}, Type: {parameterType}")
  return parameterDict

def cleanStringOfMultiSpaces(stringToClean: str) -> str:
  return " ".join(stringToClean.strip().split())

def getPortDir(stringToCheck: str) -> str:
  stringPartList = cleanStringOfMultiSpaces(stringToCheck).split()
  if stringPartList[0] in ["input", "output", "inout", "interface"]:
    return stringPartList[0]
  else:
    return ""

def getPortWidth(portString:str) -> str:
  pattern = r"\[([^\]]+)\]"
  match = re.findall(pattern, portString, re.MULTILINE|re.DOTALL)
  if match:
    portWidth = "".join(match[0].split())
    logging.debug("Portwidth of "+portWidth+" found for: "+portString)
    return portWidth
  else:
    logging.debug("No portwidth found for: "+portString)
    return ""

def getIOPortDict(fileData:str) -> list:
  IOList = []
  portListString = ""
  module_name = ""
  module_name = getModuleNames(fileData)[0]
  with_parameter_pattern = fr"{module_name}\s*#\([^)]*\)[^()]*\(([^)]*)\)"
  without_parameter_pattern = fr"{module_name}\s*\(([^\)]+)\)"
  matches_with_parameter = re.findall(with_parameter_pattern, fileData, re.MULTILINE|re.DOTALL)
  matches_without_parameter = re.findall(without_parameter_pattern, fileData, re.MULTILINE|re.DOTALL)
  logging.debug(matches_with_parameter)
  logging.debug(matches_without_parameter)
  if not matches_with_parameter and not matches_without_parameter:
    logging.warning(f"No IOs found for module: {module_name}")
    return IOList
  else:
    matches = matches_with_parameter or matches_without_parameter
    logging.debug(matches)
    portListString = matches[0]
    logging.debug(portListString)
  portList = portListString.split(',')
  portList = [eachPort.strip() for eachPort in portList]
  portList = [" ".join(eachPort.split()) for eachPort in portList]
  portList = [re.sub("\[([^\]]+)\]"," ["+getPortWidth(eachPort)+"] ",eachPort) if getPortWidth(eachPort) else eachPort for eachPort in portList]
  portList = [" ".join(eachPort.split()) for eachPort in portList]
  portList = [eachPort.replace("=", " = ") for eachPort in portList]
  logging.debug(portList)
  previousPortInfo = {"portDir":"","portType":"","portWidth":""}
  for port in portList:
    portDir   = "" #getPortDir(port)
    portType  = ""
    portWidth = "" #getPortWidth(port)
    portName  = ""
    portValue = ""
    portSegments = port.split()
    if "=" in portSegments:
      portValue = portSegments[-1]
      portSegments.remove(portValue)
      portSegments.remove("=")
    # Capturing the portName from the list
    portName = portSegments[-1]
    # Solving for other port parameters
    if len(portSegments) == 1:
      portDir = previousPortInfo["portDir"]
      portType = previousPortInfo["portType"]
      portWidth = previousPortInfo["portWidth"]
    else:
      portDir = getPortDir(port)
      portWidth = getPortWidth(port)
      portSegments.remove(portName)
      if portDir:
        portSegments.remove(portDir)
      if portWidth:
        portSegments.remove("["+portWidth+"]")
      portType = " ".join(portSegments)
    IOList.append({"portName":portName, "portDir":portDir, "portType":portType, "portWidth":portWidth, "portValue":portValue})
    previousPortInfo = {"portDir":portDir,"portType":portType,"portWidth":portWidth}
    logging.debug(f"=>>>>>>>>>>> Port Name: {portName}, Dir: {portDir}, Type: {portType}, Width: {portWidth}, Value: {portValue}")
  logging.debug(IOList)
  return IOList

def getIOPortDictForModule(module_name: str, fileData:str) -> list:
  IOList = []
  portListString = ""
  with_parameter_pattern = fr"{module_name}\s*#\([^)]*\)[^()]*\(([^)]*)\)"
  without_parameter_pattern = fr"{module_name}\s*\(([^\)]+)\)"
  matches_with_parameter = re.findall(with_parameter_pattern, fileData, re.MULTILINE|re.DOTALL)
  matches_without_parameter = re.findall(without_parameter_pattern, fileData, re.MULTILINE|re.DOTALL)
  logging.debug(matches_with_parameter)
  logging.debug(matches_without_parameter)
  if not matches_with_parameter and not matches_without_parameter:
    logging.warning(f"No IOs found for module: {module_name}")
    return IOList
  else:
    matches = matches_with_parameter or matches_without_parameter
    logging.debug(matches)
    portListString = matches[0]
    logging.debug(portListString)
  portList = portListString.split(',')
  portList = [eachPort.strip() for eachPort in portList]
  portList = [" ".join(eachPort.split()) for eachPort in portList]
  portList = [re.sub("\[([^\]]+)\]"," ["+getPortWidth(eachPort)+"] ",eachPort) if getPortWidth(eachPort) else eachPort for eachPort in portList]
  portList = [" ".join(eachPort.split()) for eachPort in portList]
  portList = [eachPort.replace("=", " = ") for eachPort in portList]
  logging.debug(portList)
  previousPortInfo = {"portDir":"","portType":"","portWidth":""}
  for port in portList:
    portDir   = "" #getPortDir(port)
    portType  = ""
    portWidth = "" #getPortWidth(port)
    portName  = ""
    portValue = ""
    portSegments = port.split()
    if "=" in portSegments:
      portValue = portSegments[-1]
      portSegments.remove(portValue)
      portSegments.remove("=")
    # Capturing the portName from the list
    portName = portSegments[-1]
    # Solving for other port parameters
    if len(portSegments) == 1:
      portDir = previousPortInfo["portDir"]
      portType = previousPortInfo["portType"]
      portWidth = previousPortInfo["portWidth"]
    else:
      portDir = getPortDir(port)
      portWidth = getPortWidth(port)
      portSegments.remove(portName)
      if portDir:
        portSegments.remove(portDir)
      if portWidth:
        portSegments.remove("["+portWidth+"]")
      portType = " ".join(portSegments)
    IOList.append({"portName":portName, "portDir":portDir, "portType":portType, "portWidth":portWidth, "portValue":portValue})
    previousPortInfo = {"portDir":portDir,"portType":portType,"portWidth":portWidth}
    logging.debug(f"=>>>>>>>>>>> Port Name: {portName}, Dir: {portDir}, Type: {portType}, Width: {portWidth}, Value: {portValue}")
  logging.debug(IOList)
  return IOList

def parserSetup():
  global parser
  global toolVersion
  parser.add_argument('-v', '--version', action='version',
                      version=toolVersion, help="Show svgeny version and exit")
  parser.add_argument('-f', '--fileinput', nargs='*', metavar='<file_input>', required=True,
                      type=str, help="Add the list of files to process")
  parser.add_argument('-l', '--loglevel', nargs=1, metavar='<log_level>', required=False,
                      type=str, default= "INFO", choices=["INFO", "DEBUG"],help="Set Log Verbosity. For debugging Ex. -l DEBUG")
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
  global logging
  args = parserSetup()
  if args.loglevel:
    if args.loglevel[0] == "DEBUG":
      logging.basicConfig(format='SVGeny: [ %(levelname)-7s ] : %(message)s',level=logging.DEBUG)
    else:
      logging.basicConfig(format='SVGeny: [ %(levelname)-7s ] : %(message)s',level=logging.INFO)
  else:
    logging.basicConfig(format='SVGeny: [ %(levelname)-7s ] : %(message)s',level=logging.INFO)
  if args.fileinput:
    for eachFile in args.fileinput:
      fileCheck = expandFilePath(eachFile)
      if fileCheck:
        inputFileList.append(fileCheck)
  for eachFile in inputFileList:
    with open(eachFile, 'r') as fileToProcess:
      fileData = fileToProcess.read()
      getModuleNames(fileData)
      # getParameterDict(fileData)
      # getIOPortDictForModule("mod1",fileData)
      # getIOPortDictForModule("mod2",fileData)
      # getIOPortDictForModule("mod3",fileData)
      # getParameterDictForModule("mod2",fileData)
      getIOPortDict(fileData)

if __name__ == "__main__":
    main()

