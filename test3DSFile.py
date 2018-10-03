#coding=utf-8

import struct, os.path
import copy
import re
import ctypes
import sys
import os
import string

class process3DSFile(object):
    def __init__(self, fileName_in):
        self.fileName_in = fileName_in
        self.total = os.path.getsize(self.fileName_in)
        print 'total =', self.total
        self.fp_in = open(self.fileName_in, "rb")
        self.pos_in = 0
        self.count = 0

    def readWrite(self, size):
        self.fp_in.seek(self.pos_in)
        buffer = self.fp_in.read(size)
        self.fp_out.seek(self.pos_out)
        self.fp_out.write(buffer)
        self.pos_in = self.pos_in + size
        self.pos_out = self.pos_out + size
        return buffer

    def processFile(self):
        while self.pos_in < self.total:
            #chunkID = self.fp_in.read(2)
            length = struct.unpack("<HI", self.fp_in.read(6))
            print "chunkID = %x, length = %x %d" % (length[0], length[1], length[1])
            raw_input()
            if length[0] == 0x4D4D:
                print '0x4D4D'
                pass

            elif length[0] == 0x3D3D:
                print '0x3D3D'
                pass
            elif length[0] == 0x4000: # name
                print '0x4000'
                i = 0
                name = ''
                while True:
                    str = self.fp_in.read(1)
                    i = i + 1
                    if str == '\0':
                        break
                    name = name + str
                print 'name =', name, i
            elif length[0] == 0x4100:
                print '0x4100'
                pass
            elif length[0] == 0x4110:   #Vertices
                print '0x4110'
                if length[1] == 0:
                    continue
                else:
                    buffer = struct.unpack('<h', self.fp_in.read(2))
                    print 'num =', buffer[0]
                    total = buffer[0]
                    i = 0
                    while i < total:
                        buffer = struct.unpack('<3f', self.fp_in.read(12))
                        print 'point =', buffer[0], buffer[1], buffer[2]
                        i = i + 1
            elif length[0] == 0x4120:  # polygons
                print '0x4120'
                if length[1] == 0:
                    continue
                else:
                    buffer = struct.unpack('<h', self.fp_in.read(2))
                    print 'num =', buffer[0]
                    total = buffer[0]
                    i = 0
                    while i < total:
                        buffer = struct.unpack('<4h', self.fp_in.read(8))
                        print 'polygon =', buffer[0], buffer[1], buffer[2], buffer[3]
                        i = i + 1
            elif length[0] == 0x4140:
                print '0x4140'
                if length[1] == 0:
                    continue
                else:
                    buffer = struct.unpack('<h', self.fp_in.read(2))
                    print 'num =', buffer[0]
                    total = buffer[0]
                    i = 0
                    while i < total:
                        buffer = struct.unpack('<2f', self.fp_in.read(8))
                        print 'vertex =', buffer[0], buffer[1]
                        i = i + 1
            else:
                self.fp_in.seek(length[1] - 6, 1)





        """
        print 'header1 =', header1
        fmt = str(length - 6) + 's'
        str
        total1 = 0
        
        while (self.pos_in < total):
            buffer = self.readWrite(16)
            headPos2 = self.pos_out - 16
            header1 = struct.unpack(">4sxxxxQ", buffer)
            tag = header1[0]
            size = header1[1]
            type = self.readWrite(4)
            # print '   type =', type
            if type == 'FREF':
                # print 'header1 =', header1
                count = self.processRefFile(tag)
                total1 = total1 + count
                if count > 0:
                    str2 = struct.pack('>4sxxxxQ', header1[0], size + count)
                    self.fp_out.seek(headPos2)
                    self.fp_out.write(str2)
                    # print '    count =', count
                continue
        """


test = process3DSFile('spaceship.3ds')
test.processFile()
