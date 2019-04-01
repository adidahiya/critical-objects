import os
import random

filename = "pikachu.jpg"
filesize = os.path.getsize("./" + filename)

# don't want to corrupt any bytes before this one
startDHT = 0
randByteLocation = 0
randByteValue = b'\x00'

with open(filename, "rb") as f:
    with open("new_" + filename, "wb") as g:
        byte = f.read(1)

        seenFirstDHT = False
        markerNext = False
        # num bytes
        i = 0

        while byte != b"":
            if markerNext and byte == b'\xc4' and not seenFirstDHT:
                print("DHT ********************************************************")
                seenFirstDHT = True

            if byte == b'\xff':
                markerNext = True
            else:
                markerNext = False

            if seenFirstDHT:
                startDHT = i
                randByteLocation = random.randint(startDHT, filesize - 1)

            g.seek(i)
            if i > 0 and i == randByteLocation:
                newByte = bytes([(byte[0] << 1) % 256])
                g.write(newByte)
            else:
                g.write(byte)

            i = i + 1
            byte = f.read(1)


