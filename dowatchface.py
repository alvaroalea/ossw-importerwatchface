#!/usr/bin/python3
# (C) 2016 Alvaro Alea Fernandez <alvaroNO_SPAMalea@gmail.com>
# Distributed under GPL V2 License
# Version 0.1.2 - 2016/01/25
# check https://github.com/aleasoft/ossw-importerwatchface for lastest version
#
# class BinaryReader by Yony Kochinski with MIT License from
# http://code.activestate.com/recipes/577610-decoding-binary-files/ 

import math
import sys 
import getopt
import struct
import base64

class BinaryReaderEOFException(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return 'Not enough bytes in file to satisfy read request'

class BinaryReader:
    # Map well-known type names into struct format characters.
    typeNames = {
        'int8'   :'b',
        'uint8'  :'B',
        'int16'  :'h',
        'uint16' :'H',
        'int32'  :'i',
        'uint32' :'I',
        'int64'  :'q',
        'uint64' :'Q',
        'float'  :'f',
        'double' :'d',
        'char'   :'s',
        'bui16'  :'>H'}

    def __init__(self, fileName):
        self.file = open(fileName, 'rb')
        
    def read(self, typeName):
        typeFormat = BinaryReader.typeNames[typeName.lower()]
        typeSize = struct.calcsize(typeFormat)
        value = self.file.read(typeSize)
        if typeSize != len(value):
            raise BinaryReaderEOFException
        return struct.unpack(typeFormat, value)[0]
    
    def seek(self,offset):     
        self.file.seek(offset)

    def __del__(self):
        self.file.close()

# funciones

def printhelp():
    sys.stderr.write('(C) 2016 Alvaro Alea Fernandez <alvaroNO_SPAMalea@gmail.com>\n');
    sys.stderr.write('Distributed under GPL V2 License\n')
    sys.stderr.write('Check https://github.com/aleasoft/ossw-importerwatchface for lastest version\n')
    sys.stderr.write('\n USAGE:\n%s  [options] binary_input_file > json_output_file\n' % sys.argv[0])
    sys.stderr.write('\nWhere options will be:\n')
    sys.stderr.write('\t-l --lang=es - default EN for english translations of date, or es for spanish (more to come)\n')
    sys.stderr.write('\t-h --help       - for this help\n')
    sys.stderr.write('\t-o --out=file  - default is standar output, use for indicate a file\n')
    sys.stderr.write('\t-n --name=text  - default is automatically generated, use for indicate the name of watchface to show in the list of watchfaces.\n')

# EMPIEZA EL PROGRAMA
outtofile = 0
sid = ""
try:
    opts, args = getopt.getopt(sys.argv[1:],"hl:o:n:",["help","lang=","out=","name="])
except getopt.GetoptError as e:
    sys.stderr.write(str(e))
    sys.stderr.write('\n')
    printhelp()
    sys.exit(2)

for opt, arg in opts:
    if opt in ("-h","--help"):
        printhelp()
        sys.exit()
    elif opt in ("-o", "--out"):
        outfile = arg
        outtofile = 1
    elif opt in ("-l", "--lang"):
        if arg == "es":
            lang = "ES"
        else:
            lang == "EN"
    elif opt in ("-n","--name"):
        sid = arg

if len(args) >= 1:
    fname = args[0]
else:
    sys.stderr.write("No se especifico archivo, ")
    fname = 'dial.bin'

sys.stderr.write("Abriendo archivo ")
sys.stderr.write(fname)
sys.stderr.write("\n")

#FIXME: test for error on opening.


binaryReader = BinaryReader(fname)
magic = binaryReader.read('uint32')
if magic != 0x5c090b0a:
    sys.stderr.write("No es un watchface.\n")
    sys.exit(2)

sys.stderr.write("Parece un watchface")
nid = hex(binaryReader.read('uint8'))
tipo = binaryReader.read('uint8')

if sid == "":
    sid = "Imported Digital ID=" + nid
sys.stderr.write(", ID=")
sys.stderr.write(nid)

if tipo != 0x01:
    sys.stderr.write(", pero no esta soportado.\n")
    sys.exit(2)

sys.stderr.write(" de tipo digital\n")

offbgh = binaryReader.read('uint8')
offfechah = binaryReader.read('uint8')
offnumh = binaryReader.read('uint8')

# PROCESAMOS EL FONDO
if offbgh != 0x00:
    binaryReader.seek(offbgh)
    bgw = binaryReader.read('uint8')
    bgh = binaryReader.read('uint8')
    bgx = binaryReader.read('uint8')
    bgy = binaryReader.read('uint8')
    offbg = binaryReader.read('bui16')

    sys.stderr.write("y con foto de fondo\n")

    bgbin= bytearray()
    bgbin.append(0x01)
    bgbin.append(0x00)
    bgbin.append(bgw)
    bgbin.append(bgh)
    binaryReader.seek(offbg)
    c = bgh * math.ceil( bgw / 8 )
    while c>0:
        bgbin.append(binaryReader.read('uint8'))
        c = c-1
    bgstr=base64.b64encode(bgbin)

# PROCESAMOS EL CALENDARIO
if offfechah !=0:
    binaryReader.seek(offfechah)
    Fformat = binaryReader.read('uint8')
    Fu2 = binaryReader.read('uint8') # desconocido
    Fx = binaryReader.read('uint8')
    Fy = binaryReader.read('uint8')
    # Fformat = 0x00 -> mes (numero) dia (numero) yo creo que el relog 106 es mentira el png tiene diethering en los numeros.
    # Fformat = 0x01 -> semana (letra) mes (letra) dia (numero)
    # Fformat = 0x02 -> semana (letra) dia (numero) mes (letra)
    # Fformat = 0x03 -> mes (letra) dia (numero)  semana (letra)
    # Fformat = 0x04 -> dia (numero) mes (letra) semana (letra)
    # Fformat = 0x05 -> mes (letra) dia (numero) 
    # Fformat = 0x06 -> dia (numero) mes (letra)
    if Fformat == 0x00:
        Fw = 14
        Fh = 20
        Fs = 2
        Ft = 2
        Fwg = 15
        Fxg = Fx + Fw + Fs + Fw
        Fx2 = Fx + Fw + Fs + Fw + Fwg
    else:
        sys.stderr.write('EL CALENDARIO AUN NO ESTA SOPORTADO\n')


if offnumh != 0:
    binaryReader.seek(offnumh)
    digits = [ {"offset":0,"use":1, "x":0, "y":0, "w":0, "h":0, "space":0, "range":"0-9","conv":"tens","bitmap":"", "res":"num" ,"hres":1, "pro":"hour"}, \
               {"offset":0,"use":1, "x":0, "y":0, "w":0, "h":0, "space":0, "range":"0-9","conv":"ones","bitmap":"", "res":"num2","hres":1, "pro":"hour"}, \
               {"offset":0,"use":1, "x":0, "y":0, "w":0, "h":0, "space":0, "range":"0-9","conv":"tens","bitmap":"", "res":"num1","hres":1, "pro":"minutes"}, \
               {"offset":0,"use":1, "x":0, "y":0, "w":0, "h":0, "space":0, "range":"0-9","conv":"ones","bitmap":"", "res":"num3","hres":1, "pro":"minutes"} ]
    for c in range(4):
        digits[c]["offset"] = binaryReader.read('uint16')
    for c in range(4):
        digits[c]["x"] = binaryReader.read('uint8')
        digits[c]["y"] = binaryReader.read('uint8')
    for c in range(4):
        digits[c]["w"] = binaryReader.read('uint8')
        digits[c]["h"] = binaryReader.read('uint8')

    if digits[1]["offset"] == digits[0]["offset"]:
         digits[1]["hres"]=0
         digits[1]["res"]=digits[0]["res"]

    if digits[2]["offset"] == digits[0]["offset"]:
         digits[2]["hres"]=0
         digits[2]["res"]=digits[0]["res"]
    elif digits[2]["offset"] == digits[1]["offset"]:
         digits[2]["hres"]=0
         digits[2]["res"]=digits[1]["res"]

    if digits[3]["offset"] == digits[0]["offset"]:
         digits[3]["hres"]=0
         digits[3]["res"]=digits[0]["res"]
    elif digits[3]["offset"] == digits[1]["offset"]:
         digits[3]["hres"]=0
         digits[3]["res"]=digits[1]["res"]
    elif digits[3]["offset"] == digits[2]["offset"]:
         digits[3]["hres"]=0
         digits[3]["res"]=digits[2]["res"]

    for c in range(4):
       if digits[c]["hres"]!=0:
          num2bin= bytearray()
          num2bin.append(0x03)
          num2bin.append(0x00)
          num2bin.append(digits[c]["w"])
          num2bin.append(digits[c]["h"])
          binaryReader.seek(digits[c]["offset"])
          d = digits[c]["h"] * math.ceil( digits[c]["w"] / 8 ) * 10
          while d>0:
              num2bin.append(binaryReader.read('uint8'))
              d = d-1
          num2str=base64.b64encode(num2bin)
          digits[c]["bitmap"]=num2str.decode("utf-8")

    if ( digits[0]["y"] == digits[1]["y"] ) and ( digits[0]["res"] == digits[1]["res"]):
         digits[0]["space"] = digits[1]["x"] - digits[0]["x"] - digits[0]["w"]
         digits[0]["range"]="0-99"
         digits[1]["use"]=0
         digits[0]["conv"]=""
         digits[1]["conv"]=""
        

    if ( digits[2]["y"] == digits[3]["y"] ) and ( digits[2]["res"] == digits[3]["res"]):
         digits[2]["space"] = digits[3]["x"] - digits[2]["x"] - digits[2]["w"]
         digits[2]["range"]="0-99"
         digits[3]["use"]=0
         digits[2]["conv"]=""
         digits[3]["conv"]=""


# AHORA IMPRIMIMOS EL ARCHIVO JSON
if outtofile == 0:
    outfiler = sys.stdout
else:
    outfiler= open(outfile,'w')


outfiler.write('{0}\n   "type": "watchset",\n   "name": "{1}",'.format('{',sid))
outfiler.write('\n   "apiVersion": 1,\n   "data": {')
outfiler.write('\n\t"screens": [\n\t\t{\n\t\t   "id": "watchface",\n\t\t   "controls": [')

coma = 0
if offbgh != 0x0000:
    outfiler.write('\n\t\t\t{\n\t\t\t   "type": "image",')
    outfiler.write('\n\t\t\t   "position": {0}"x": {2}, "y": {3}{1},'.format('{','}',bgx,bgy))
    outfiler.write('\n\t\t\t   "style": {0}"width": {2}, "height": {3}{1},'.format('{','}',bgw,bgh))
    outfiler.write('\n\t\t\t   "image": {"type": "resource", "id": "bg"}\n\t\t\t}')
    coma = 1

# Time digits
for c in range(4):
    if digits[c]["use"]!=0:
       if coma == 1:
          outfiler.write(',')
       outfiler.write('\n\t\t\t{0}\n\t\t\t   "type": "number",\n\t\t\t   "numberRange": "{1}",'.format('{',digits[c]["range"]))
       outfiler.write('\n\t\t\t   "position": {0}"x": {2}, "y": {3}{1},'.format('{','}',digits[c]["x"],digits[c]["y"]))
       outfiler.write('\n\t\t\t   "style": {"type": "numbersFont", "numbersFont": {"type": "resource", "id": "')
       outfiler.write('{2}"{0}, "space": {3}, "leftPadded": true{1},'.format('}','}','num',digits[c]["space"]))
       outfiler.write('\n\t\t\t   "source": {0}"type": "internal", "property": "{1}"'.format('}',digits[c]["pro"]))
       if digits[c]["conv"]!="":
           outfiler.write(', "converter": "{1}"{0}'.format('}',digits[c]["conv"]))
       outfiler.write('\n\t\t\t}')

# The calendar
if ( offfechah !=0x00 ) and ( Fformat==0x00 ):
    outfiler.write('\n\t\t\t},')
    outfiler.write('\n\t\t\t{\n\t\t\t   "type": "number",\n\t\t\t   "numberRange": "0-99",')
    outfiler.write('\n\t\t\t   "position": {0}"x": {2}, "y": {3}{1},'.format('{','}',Fx,Fy))
    outfiler.write('\n\t\t\t   "style": {0}"type": "generated", "thickness": {1}'.format('{',Ft))
    outfiler.write(', "width": {0}, "height": {1}, "space": {2}'.format(Fw,Fh,Fs))
    outfiler.write(', "leftPadded": true},\n\t\t\t   "source": {"type": "internal", "property": "month"}\n\t\t\t},')
    
    outfiler.write('\n\t\t\t{0}\n\t\t\t   "type": "text",\n\t\t\t   "position": {1}"x": {2}'.format('{','{',Fxg))
    outfiler.write(', "y": {3}{0},\n\t\t\t   "size": {1}"width": {4}, "height": {5}{2},'.format('}','{','}',Fy,Fwg,Fh))
    outfiler.write('\n\t\t\t   "font": {"type": "builtin", "name": "smallRegular"},')
    outfiler.write('\n\t\t\t   "style": {"horizontalAlign": "center", "verticalAlign": "center", "multiline": "true"},')
    outfiler.write('\n\t\t\t   "source": {"type": "static", "value": "-"}\n\t\t\t},')
    
    outfiler.write('\n\t\t\t{\n\t\t\t   "type": "number",\n\t\t\t   "numberRange": "0-99",')
    outfiler.write('\n\t\t\t   "position": {0}"x": {2}, "y": {3}{1},'.format('{','}',Fx2,Fy))
    outfiler.write('\n\t\t\t   "style": {0}"type": "generated", "thickness": {1}'.format('{',Ft))
    outfiler.write(', "width": {1}, "height": {2}, "space": {3}, "leftPadded": true{0},'.format('{',Fw,Fh,Fs))
    outfiler.write('\n\t\t\t   "source": {"type": "internal", "property": "dayOfMonth"}')

outfiler.write('\n\t\t   ],\n\t\t   "defaultActions": "watchface",')
outfiler.write('\n\t\t   "settings": {"invertible": "true"}\n\t\t}\n\t],\n\t"resources": [')

# resource of BG
coma = 0
if offbgh != 0x0000:
    outfiler.write('\n{0}\n"id": "bg",\n"data":"{2}"\n{1}'.format('{','}',bgstr.decode("utf-8")))
    coma = 1
    
# resources of digitos
for c in range(4):
    if digits[c]["hres"]!=0:
       if coma == 1:
          outfiler.write(',')
       outfiler.write('\n{0}\n"id": "{2}",\n"data": "{3}"\n{1}'.format('{','}',digits[c]["res"],digits[c]["bitmap"]))
       coma = 1

# TAIL   
outfiler.write('\n\t]\n   }\n}')

