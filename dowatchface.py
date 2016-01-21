#!/usr/bin/python
# (C) 2016 Alvaro Alea Fernandez <alvaroNO_SPAMalea@gmail.com>
# Distributed under GPL V2 License
# check https://github.com/aleasoft/ossw-importerwatchface for lastest version
#
# class BinaryReader by Yony Kochinski with MIT License from
# http://code.activestate.com/recipes/577610-decoding-binary-files/ 

import sys
import struct

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
    
    def seek(self,offset):     #habra que ver si funciona (C) alea
        self.file.seek(offset)

    def __del__(self):
        self.file.close()

fname = sys.argv[1]

sys.stderr.write("Abriendo archivo ")
sys.stderr.write(fname)
sys.stderr.write("\n")
binaryReader = BinaryReader(fname)
magic = binaryReader.read('uint32')
if magic == 0x5c090b0a:
  sys.stderr.write("Parece un watchface")
  nid = hex(binaryReader.read('uint8'))
  tipo = binaryReader.read('uint8')
  sys.stderr.write(", ID=")
  sys.stderr.write(nid)
  if tipo == 0x01:  
      sys.stderr.write(" de tipo digital\n")
      offbgh = binaryReader.read('uint8')
      offfechah = binaryReader.read('uint8')
      offnumh = binaryReader.read('uint8')
      # leer BG si tiene, aqui lo suyo es un seek(offbgh)
      tam = 7
      while tam >0:
           binaryReader.read('uint8')
           tam -=1     
      if offbgh == 0x10:
         sys.stderr.write("y con foto de fondo en el offset=")
         offbg = binaryReader.read('bui16')
         sys.stderr.write(hex(offbg))
         sys.stderr.write("\n")
         binaryReader.read('bui16')
         niidea1 = binaryReader.read('bui16')
         tam = 10
         while tam >0:
             binaryReader.read('uint8')
             tam -=1
      # otro hack en lugar de seek(0x30)
      if offnumh == 0x30:
         tam = 16
         while tam >0:
             binaryReader.read('uint8')
             tam -=1
      # leer numeros, si es digital, aqui lo suyo es un seek(offnumh)
      offH1 = binaryReader.read('bui16')
      offH2 = binaryReader.read('bui16')
      offM1 = binaryReader.read('bui16')
      offM2 = binaryReader.read('bui16')

      sys.stderr.write( "H1=" )
      sys.stderr.write( hex(offH1) )
      sys.stderr.write( "\nH2=" )
      sys.stderr.write( hex(offH2) )
      sys.stderr.write( "\nM1=" )
      sys.stderr.write( hex(offM1) )
      sys.stderr.write( "\nM2=" )
      sys.stderr.write( hex(offM2) )
      sys.stderr.write( "\n" )
      if offH1 != offM1:
	hasMres = 1
        Mresn = 'num2'
      else:
	hasMres = 0
        Mresn = 'num'

      H1x = binaryReader.read('uint8')
      H1y = binaryReader.read('uint8')
      H2x = binaryReader.read('uint8')
      H2y = binaryReader.read('uint8')
      M1x = binaryReader.read('uint8')
      M1y = binaryReader.read('uint8')
      M2x = binaryReader.read('uint8')
      M2y = binaryReader.read('uint8')
 
      sys.stderr.write( "H1 x=" )
      sys.stderr.write( str(H1x) )
      sys.stderr.write( " , y=" )
      sys.stderr.write( str(H1y) )
      sys.stderr.write( "\nH2 x=" )
      sys.stderr.write( str(H2x) )
      sys.stderr.write( " , y=" )
      sys.stderr.write( str(H2y) )
      sys.stderr.write( "\nM1 x=" )
      sys.stderr.write( str(M1x) )
      sys.stderr.write( " , y=" )
      sys.stderr.write( str(M1y) )
      sys.stderr.write( "\nM2 x=" )
      sys.stderr.write( str(M2x) )
      sys.stderr.write( " , y=" )
      sys.stderr.write( str(M2y) )
      sys.stderr.write( "\n" )

      H1sx = binaryReader.read('uint8')
      H1sy = binaryReader.read('uint8')
      H2sx = binaryReader.read('uint8')
      H2sy = binaryReader.read('uint8')
      M1sx = binaryReader.read('uint8')
      M1sy = binaryReader.read('uint8')
      M2sx = binaryReader.read('uint8')
      M2sy = binaryReader.read('uint8')
 
      sys.stderr.write( "H1 sx=" )
      sys.stderr.write( str(H1sx) )
      sys.stderr.write( " , sy=" )
      sys.stderr.write( str(H1sy) )
      sys.stderr.write( "\nH2 sx=" )
      sys.stderr.write( str(H2sx) )
      sys.stderr.write( " , sy=" )
      sys.stderr.write( str(H2sy) )
      sys.stderr.write( "\nM1 sx=" )
      sys.stderr.write( str(M1sx) )
      sys.stderr.write( " , sy=" )
      sys.stderr.write( str(M1sy) )
      sys.stderr.write( "\nM2 sx=" )
      sys.stderr.write( str(M2sx) )
      sys.stderr.write( " , sy=" )
      sys.stderr.write( str(M2sy) )
      sys.stderr.write( "\n" )

      spaceH = H2x - H1x - H1sx
      spaceM = M2x - M1x - M1sx

      sys.stderr.write( "Space H=" )
      sys.stderr.write( str(spaceH) )
      sys.stderr.write( " , Space M=" )
      sys.stderr.write( str(spaceM) )
      sys.stderr.write( "\n" )
      
      # Estamos en 0x28

#sys.exit()
# La parte donde imprimimos el JSON
sys.stdout.write('{\n   "type": "watchset",\n   "name": "Imported Digital ID=')
sys.stdout.write(nid)
print '",\n   "apiVersion": 1,\n   "data": {'
print '\t"screens": [\n\t\t{\n\t\t   "id": "watchface",\n\t\t   "controls": ['

if offbgh != 0x0000:
   print '\t\t\t{'
   print '\t\t\t   "type": "image",'
   print '\t\t\t   "position": {"x": 0, "y": 0},'
   print '\t\t\t   "style": {"width": 144, "height": 168},'
   print '\t\t\t   "image": {"type": "resource", "id": "bg"}'
   print '\t\t\t},'

print '\t\t\t{'
print '\t\t\t   "type": "number",'
print '\t\t\t   "numberRange": "0-99",'
sys.stdout.write('\t\t\t   "position": {"x": ')
sys.stdout.write( str(H1x) )
sys.stdout.write(', "y": ')
sys.stdout.write( str(H1y) )
print '},'
sys.stdout.write('\t\t\t   "style": {"type": "numbersFont", "numbersFont": {"type": "resource", "id": "num"}, "space": ')
sys.stdout.write( str(spaceH) )
print ', "leftPadded": true},'
print '\t\t\t   "source": {"type": "internal", "property": "hour"}'
print '\t\t\t},\n\t\t\t{'
print '\t\t\t   "type": "number",'
print '\t\t\t   "numberRange": "0-99",'
sys.stdout.write('\t\t\t   "position": {"x": ')
sys.stdout.write( str(M1x) )
sys.stdout.write(', "y": ')
sys.stdout.write( str(M1y) )
print '},'
sys.stdout.write('\t\t\t   "style": {"type": "numbersFont", "numbersFont": {"type": "resource", "id": "')
sys.stdout.write(Mresn)
sys.stdout.write('"}, "space": ')
sys.stdout.write( str(spaceM) )
print ', "leftPadded": true},'
print '\t\t\t   "source": {"type": "internal", "property": "minutes"}'
print '\t\t\t}\n\t\t   ],'
print '\t\t   "defaultActions": "watchface",'
print '\t\t   "settings": {"invertible": "true"}'
print '\t\t}\n\t],\n\t"resources": ['
print '[A RELLENAR]'
if offbgh != 0x0000:
   print 'BG RESOURCE' # resource de BG
print 'HOUR RESOURCE' # resource de Horas
if hasMres == 1:
   print 'MINUTE RESOURCE' # resource de Minutos
print '\t]\n   }\n}'

