#!/usr/bin/python
# (C) 2016 Alvaro Alea Fernandez <alvaroNO_SPAMalea@gmail.com>
# Distributed under GPL V2 License
# check https://github.com/aleasoft/ossw-importerwatchface for lastest version
#
# class BinaryReader by Yony Kochinski with MIT License from
# http://code.activestate.com/recipes/577610-decoding-binary-files/ 

import sys
import struct
import base64
import math

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

# EMPIEZA EL PROGRAMA

if len(sys.argv) > 1:
   fname = sys.argv[1]
else:
   fname = 'dial.bin'

sys.stderr.write("Abriendo archivo ")
sys.stderr.write(fname)
sys.stderr.write("\n")

binaryReader = BinaryReader(fname)
magic = binaryReader.read('uint32')
if magic == 0x5c090b0a:
  sys.stderr.write("Parece un watchface")
  nid = hex(binaryReader.read('uint8'))
  tipo = binaryReader.read('uint8')
  
  if len(sys.argv) > 2:
     sid = sys.argv[2]
  else:
     sid = "Imported Digital ID=" + nid
     #sid.append(nid)

  sys.stderr.write(", ID=")
  sys.stderr.write(nid)

  if tipo == 0x01:  
      offbgh = binaryReader.read('uint8')
      offfechah = binaryReader.read('uint8')
      offnumh = binaryReader.read('uint8')

      sys.stderr.write(" de tipo digital\n")

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



      # PROCESAMOS LA HORA
      if offnumh != 0:
          binaryReader.seek(offnumh)
      offH1 = binaryReader.read('uint16')
      offH2 = binaryReader.read('uint16')
      offM1 = binaryReader.read('uint16')
      offM2 = binaryReader.read('uint16')
      H1x = binaryReader.read('uint8')
      H1y = binaryReader.read('uint8')
      H2x = binaryReader.read('uint8')
      H2y = binaryReader.read('uint8')
      M1x = binaryReader.read('uint8')
      M1y = binaryReader.read('uint8')
      M2x = binaryReader.read('uint8')
      M2y = binaryReader.read('uint8')
      H1w = binaryReader.read('uint8')
      H1h = binaryReader.read('uint8')
      H2w = binaryReader.read('uint8')
      H2h = binaryReader.read('uint8')
      M1w = binaryReader.read('uint8')
      M1h = binaryReader.read('uint8')
      M2w = binaryReader.read('uint8')
      M2h = binaryReader.read('uint8')

      if offH1 != offM1:
        hasMres = 1
        Mresn = 'num2'
      else:
        hasMres = 0
        Mresn = 'num'
      spaceH = H2x - H1x - H1w
      spaceM = M2x - M1x - M1w

      if offH1 != offH2:
         sys.stderr.write("NUMEROS DE HORA DIFERENTES NO ESTA SOPORTADO\n")
      if offM1 != offM2:
         sys.stderr.write("NUMEROS DE MINUTO DIFERENTES NO ESTA SOPORTADO\n")
      if H1y != H2y:
         sys.stderr.write("NUMEROS DE HORA EN DIAGONAL NO ESTA SOPORTADO\n")
      if H1y != H2y:
         sys.stderr.write("NUMEROS DE MINUTOS EN DIAGONAL NO ESTA SOPORTADO\n")

      num1bin= bytearray()
      num1bin.append(0x03)
      num1bin.append(0x00)
      num1bin.append(H1w)
      num1bin.append(H2h)
      binaryReader.seek(offH1)
      c = H1h * math.ceil( H1w / 8 ) * 10
      while c>0:
         num1bin.append(binaryReader.read('uint8'))
         c = c-1
      num1str=base64.b64encode(num1bin)

      if hasMres == 1:
         num2bin= bytearray()
         num2bin.append(0x03)
         num2bin.append(0x00)
         num2bin.append(M1w)
         num2bin.append(M1h)
         binaryReader.seek(offM1)
         c = M1h * math.ceil( M1w / 8 ) * 10
         while c>0:
            num2bin.append(binaryReader.read('uint8'))
            c = c-1
         num2str=base64.b64encode(num2bin)



# AHORA IMPRIMIMOS EL ARCHIVO JSON
#sys.exit()
sys.stdout.write('{\n   "type": "watchset",\n   "name": "')
sys.stdout.write(sid)
print('",\n   "apiVersion": 1,\n   "data": {')
print('\t"screens": [\n\t\t{\n\t\t   "id": "watchface",\n\t\t   "controls": [')

if offbgh != 0x0000:
   print('\t\t\t{\n\t\t\t   "type": "image",')
   sys.stdout.write('\t\t\t   "position": {"x": ')
   sys.stdout.write(str(bgx))
   sys.stdout.write(', "y": ')
   sys.stdout.write(str(bgy))
   print('},')
   sys.stdout.write('\t\t\t   "style": {"width": ')
   sys.stdout.write(str(bgw))
   sys.stdout.write(', "height": ')
   sys.stdout.write(str(bgh))
   print('},\n\t\t\t   "image": {"type": "resource", "id": "bg"}\n\t\t\t},')

print('\t\t\t{\n\t\t\t   "type": "number",\n\t\t\t   "numberRange": "0-99",')
sys.stdout.write('\t\t\t   "position": {"x": ')
sys.stdout.write( str(H1x) )
sys.stdout.write(', "y": ')
sys.stdout.write( str(H1y) )
print('},')
sys.stdout.write('\t\t\t   "style": {"type": "numbersFont", "numbersFont": {"type": "resource", "id": "num"}, "space": ')
sys.stdout.write( str(spaceH) )
print(', "leftPadded": true},\n\t\t\t   "source": {"type": "internal", "property": "hour"}')
print('\t\t\t},\n\t\t\t{\n\t\t\t   "type": "number",\n\t\t\t   "numberRange": "0-99",')
sys.stdout.write('\t\t\t   "position": {"x": ')
sys.stdout.write( str(M1x) )
sys.stdout.write(', "y": ')
sys.stdout.write( str(M1y) )
print('},')
sys.stdout.write('\t\t\t   "style": {"type": "numbersFont", "numbersFont": {"type": "resource", "id": "')
sys.stdout.write(Mresn)
sys.stdout.write('"}, "space": ')
sys.stdout.write( str(spaceM) )
print(', "leftPadded": true},\n\t\t\t   "source": {"type": "internal", "property": "minutes"}')

if ( offfechah !=0x00 ) and ( Fformat==0x00 ):
        print('\t\t\t},\n\t\t\t{\n\t\t\t   "type": "number",\n\t\t\t   "numberRange": "0-99",')
        print('\t\t\t   "position": {"x": ',end="")
        print(Fx,end="")
        print(', "y": ',end="")
        print(Fy,end="")
        print('},\n\t\t\t   "style": {"type": "generated", "thickness": ',end="")
        print(Ft,end="")
        print(', "width": ',end="")
        print(Fw,end="")
        print(', "height": ',end="")
        print(Fh,end="")
        print(', "space": ',end="")
        print(Fs,end="")
        print(', "leftPadded": true},\n\t\t\t   "source": {"type": "internal", "property": "month"}')
        print('\t\t\t},')
        
        print('\t\t\t{')
        print('\t\t\t   "type": "text",')
        print('\t\t\t   "position": {"x": ',end="")
        print(Fxg,end="")
        print(', "y": ',end="")
        print(Fy,end="")
        print('},')
        print('\t\t\t   "size": {"width": ',end="")
        print(Fwg,end="")
        print(', "height": ',end="")
        print(Fh,end="")
        print('},')
        print('\t\t\t   "font": {"type": "builtin", "name": "smallRegular"},')
        print('\t\t\t   "style": {"horizontalAlign": "center", "verticalAlign": "center", "multiline": "true"},')
        print('\t\t\t   "source": {"type": "static", "value": "-"}')
        print('\t\t\t},')
        
        print('\t\t\t{\n\t\t\t   "type": "number",')
        print('\t\t\t   "numberRange": "0-99",\n\t\t\t   "position": {"x": ',end="")
        print(Fx2,end="")
        print(', "y": ',end="")
        print(Fy,end="")
        print('},\n\t\t\t   "style": {"type": "generated", "thickness": ',end="")
        print(Ft,end="")
        print(', "width": ',end="")
        print(Fw,end="")
        print(', "height": ',end="")
        print(Fh,end="")
        print(', "space": ',end="")
        print(Fs,end="")
        print(', "leftPadded": true},\n\t\t\t   "source": {"type": "internal", "property": "dayOfMonth"}')


print('\t\t\t}\n\t\t   ],\n\t\t   "defaultActions": "watchface",')
print('\t\t   "settings": {"invertible": "true"}\n\t\t}\n\t],\n\t"resources": [')

# resource de BG
if offbgh != 0x0000:
   sys.stdout.write('{\n"id": "bg",\n"data": "')
   print(bgstr.decode("utf-8"),end="")
   print('"\n},') 

# resource de Horas
sys.stdout.write('{\n"id": "num",\n"data": "')
print(num1str.decode("utf-8"),end="")
print('"\n}',end="") 

# resource de Minutos
if hasMres == 1:
   sys.stdout.write(',\n{\n"id": "')
   sys.stdout.write(Mresn)
   sys.stdout.write('",\n"data": "')
   print(num2str.decode("utf-8"),end="")
   print('"\n}') 
else:
   sys.stdout.write('\n')

# TAIL   
print('\t]\n   }\n}')

