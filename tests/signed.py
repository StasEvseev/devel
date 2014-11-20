import sys
import os.path as _p
sys.path.insert(0, _p.abspath(_p.join(_p.dirname(_p.abspath(sys.argv[0])), '..')))
from logs import lg
from lib import bpio
from crypt import key
from crypt import signed
from lib import settings
from lib import misc

bpio.init()
lg.set_debug_level(18)
settings.init()
key.InitMyKey()
print 'reading'
data1 = bpio.ReadBinaryFile(sys.argv[1])
print '%d bytes long, hash: %s' % (len(data1), misc.BinaryToAscii(key.Hash(data1)).strip()) 
p1 = signed.Packet(
    'Data', misc.getLocalID(), misc.getLocalID(), 'SomeID', data1, 'RemoteID:abc')
print 'serialize', p1
print '  Command:', p1.Command, type(p1.Command)
print '  OwnerID:', p1.OwnerID, type(p1.OwnerID)
print '  CreatorID:', p1.CreatorID, type(p1.CreatorID)
print '  PacketID:', p1.PacketID, type(p1.PacketID)
print '  Date:', p1.Date, type(p1.Date)
print '  Payload:', len(p1.Payload), misc.BinaryToAscii(key.Hash(p1.Payload)).strip(), type(p1.Payload) 
print '  RemoteID:', p1.RemoteID, type(p1.RemoteID)
print '  Signature:', p1.Signature, type(p1.Signature)
src1 = p1.Serialize()
print len(src1), 'bytes long' 
# print len(p1.Payload), misc.BinaryToAscii(key.HashMD5(p1.Payload))
p2 = signed.Unserialize(src1)
print 'unserialize', p2
print '  Command:', p2.Command, type(p2.Command)
print '  OwnerID:', p2.OwnerID, type(p2.OwnerID)
print '  CreatorID:', p2.CreatorID, type(p2.CreatorID)
print '  PacketID:', p2.PacketID, type(p2.PacketID)
print '  Date:', p2.Date, type(p2.Date)
print '  Payload:', len(p2.Payload), misc.BinaryToAscii(key.Hash(p2.Payload)).strip(), type(p2.Payload) 
print '  RemoteID:', p2.RemoteID, type(p2.RemoteID)
print '  Signature:', p2.Signature, type(p2.Signature)
src2 = p2.Serialize()
print len(src2), 'bytes long' 
# print len(p2.Payload), misc.BinaryToAscii(key.HashMD5(p2.Payload))
print 'compare'
data2 = p2.Payload
print data2 == data1
open('1', 'wb').write(src1)
open('2', 'wb').write(src2)
print src1 == src2
p3 = signed.Unserialize(src2)
print 'unserialize', p3
print '  Command:', p3.Command, type(p3.Command)
print '  OwnerID:', p3.OwnerID, type(p3.OwnerID)
print '  CreatorID:', p3.CreatorID, type(p3.CreatorID)
print '  PacketID:', p3.PacketID, type(p3.PacketID)
print '  Date:', p3.Date, type(p3.Date)
print '  Payload:', len(p3.Payload), misc.BinaryToAscii(key.Hash(p3.Payload)).strip(), type(p3.Payload) 
print '  RemoteID:', p3.RemoteID, type(p3.RemoteID)
print '  Signature:', p3.Signature, type(p3.Signature)
src3 = p3.Serialize()
print len(src3), 'bytes long' 

    
    