#!/usr/bin/env python3
from sys import argv
import xml.etree.ElementTree as ET 
import lxml.etree as etree
import re,sys
import xml.dom.minidom as md
from bs4 import BeautifulSoup
import xmltodict, json
# from utils import *

latestAHD = None

if len(argv)!=3:
  sys.exit("Usage: "+argv[0]+" input_flexis.txt output_tree.json")

with open(argv[1], 'r', encoding="utf-8") as file:
  
  print("reading text file", file=sys.stderr)
  contents = file.read()

  print("string replace", file=sys.stderr)
  # print(contents.find("<MFEXPORT"))
  # sys.exit()

  if contents.find("<MFEXPORT")!=0: # if the string does not start with 
    contents = "<MFEXPORT>\n" +  contents

  contents = contents+"</MFEXPORT>" # add root tag
  contents = contents.replace("&","&amp;") # fix &'s

  contents = contents.replace("<ZR>","\n") # fix <ZR>  <ZR/>
  contents = contents.replace("<BCURS>","[BCURS]")
  contents = contents.replace("<ECURS>","[ECURS]")

  # writing tmp.xml for testing
  # print("Writing to tmp.xml (should now be valid xml)")
  # with open("tmp.xml", 'w') as tmp:
  #   print(contents, file=tmp)


  print("xml from string", file=sys.stderr)
  xml = ET.fromstring(contents)

  # from here the XML should have a valid syntax
  # now improve the semantics by moving INRICHTING, REL, ABD as child of AHD
  print("processing records", file=sys.stderr)
  ahds = []
  for i in xml:

    if i.tag=='AHD':
      if latestAHD:
        ahds.append(latestAHD)   # don't mutate xml but create a new one

      latestAHD = i
    elif re.match(r'INRICHTING|REL|ABD', i.tag):  # add child to new AHD
      latestAHD.append(i)

    else:
      print("Unkown element: " + i.tag, file=sys.stderr)

  ahds.append(latestAHD) # add the final one

  result = ET.fromstring("<MFEXPORT/>")
  for i in ahds:
    result.append(i)

  # print("print using minidom", file=sys.stderr)
  # xmlstring = ET.tostring(result, encoding="utf8").decode("utf8")
  xmlstr = ET.tostring(result).decode()
  # newxml = md.parseString(xmlstr)
  # print(newxml.toprettyxml(indent='  ',newl=''))

  print("creating preview", file=sys.stderr)
  od = xmltodict.parse(xmlstr) # OrderedDict

  # save json for jstree
  outputfilename = argv[2]
  print(f"Writing to {outputfilename}")
  with open(outputfilename, "w") as f:
    json.dump(od, f, indent=4, ensure_ascii=False)

