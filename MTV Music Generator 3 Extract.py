import struct
import os

true = True
false = False
null = None

def cstring(f):
	cstr = ''
	byte = f.read(1)
	if byte:
		byte = struct.unpack("B", byte)[0]
		if byte == 0:
			return false
		while byte and byte != 0:
			# Can't use struct.unpack("c"... so use struct.unpack("B"... and convert type
			cstr += chr(byte)
			byte = struct.unpack("B", f.read(1))[0]
		return cstr
	else:
		return false

def synchsafe(in2):
        out = 127
        mask = 127
        while mask ^ 2147483647:
                out = in2 & ~mask
                out <<= 1
                out |= in2 & mask
                mask = ((mask + 1) << 8) - 1
                in2 = out
        return out

def writeLIST(i, f, WAVELISTLength):
        f.write(bytes("LIST", "UTF-8"))
        f.write(struct.pack("<I", WAVELISTLength))
        f.write(bytes("INFO", "UTF-8"))
        # Genre
        f.write(bytes("IGNR", "UTF-8"))
        f.write(struct.pack("<I", 1 + len(i[1]["Genre"])))
        f.write(bytes(i[1]["Genre"], "UTF-8"))
        f.write(struct.pack("B", 00))
        if len(i[1]["Genre"]) % 2 == 0:
                f.write(struct.pack("B", 00))
        # Source
        f.write(bytes("IART", "UTF-8"))
        f.write(struct.pack("<I", 1 + len(i[1]["Source"])))
        f.write(bytes(i[1]["Source"], "UTF-8"))
        f.write(struct.pack("B", 00))
        if len(i[1]["Source"]) % 2 == 0:
                f.write(struct.pack("B", 00))
        # Title
        f.write(bytes("INAM", "UTF-8"))
        f.write(struct.pack("<I", 1 + len(i[0])))
        f.write(bytes(i[0], "UTF-8"))
        f.write(struct.pack("B", 00))
        if len(i[0]) % 2 == 0:
                f.write(struct.pack("B", 00))
        # Software
        f.write(bytes("ISFT", "UTF-8"))
        f.write(struct.pack("<I", 22))
        f.write(bytes("MTV Music Generator 3", "UTF-8"))
        f.write(struct.pack("B", 00))
        # Copyright
        f.write(bytes("ICOP", "UTF-8"))
        f.write(struct.pack("<I", 40))
        f.write(bytes("Copyright 2004 by MTV Music Generator 3", "UTF-8"))
        f.write(struct.pack("B", 00))

def writeID3v2(i, f, WAVEID3v2Length):
        f.write(bytes("ID3 ", "UTF-8"))
        f.write(struct.pack("<I", WAVEID3v2Length))
        f.write(bytes("ID3", "UTF-8"))
        f.write(struct.pack("B", 4))
        f.write(struct.pack("B", 0))
        f.write(struct.pack("B", 0))
        f.write(struct.pack(">I", synchsafe(97 + len(i[1]["Genre"]) + len(i[1]["Source"]) + len(i[0]))))
        # Genre
        f.write(bytes("TCON", "UTF-8"))
        f.write(struct.pack(">I", 1 + synchsafe(len(i[1]["Genre"]))))
        f.write(struct.pack("B", 0))
        f.write(struct.pack("B", 0))
        f.write(struct.pack("B", 0))
        f.write(bytes(i[1]["Genre"], "UTF-8"))
        # Source
        f.write(bytes("TPE1", "UTF-8"))
        f.write(struct.pack(">I", 1 + synchsafe(len(i[1]["Source"]))))
        f.write(struct.pack("B", 0))
        f.write(struct.pack("B", 0))
        f.write(struct.pack("B", 0))
        f.write(bytes(i[1]["Source"], "UTF-8"))
        # Title
        f.write(bytes("TIT2", "UTF-8"))
        f.write(struct.pack(">I", 1 + synchsafe(len(i[0]))))
        f.write(struct.pack("B", 0))
        f.write(struct.pack("B", 0))
        f.write(struct.pack("B", 0))
        f.write(bytes(i[0], "UTF-8"))
        # BPM
        f.write(bytes("TBPM", "UTF-8"))
        f.write(struct.pack(">I", 1 + synchsafe(len(str(i[1]["BPM"])))))
        f.write(struct.pack("B", 0))
        f.write(struct.pack("B", 0))
        f.write(struct.pack("B", 0))
        f.write(bytes(str(i[1]["BPM"]), "UTF-8"))
        # Copyright
        f.write(bytes("TCOP", "UTF-8"))
        f.write(struct.pack(">I", 40))
        f.write(struct.pack("B", 0))
        f.write(struct.pack("B", 0))
        f.write(struct.pack("B", 0))
        f.write(bytes("Copyright 2004 by MTV Music Generator 3", "UTF-8"))

def extractWHD():
        # WHD
        wbd = {}
        f = open("F:\\MTV Music Generator 3\\outputx.whd", "rb")
        f.seek(8, 0)
        wbdOffset = f.read(4)
        while wbdOffset:
                wbdLength = f.read(4)
                if wbdLength:
                        f.seek(8, 1)
                        wbdFilename = cstring(f)
                        if wbdFilename:
                                wbd[wbdFilename] = {"Offset": struct.unpack("<I", wbdOffset)[0], "Length": struct.unpack("<I", wbdLength)[0]}
                                print("WHD - File at Offset: " + str(wbd[wbdFilename]["Offset"]))
                                f.seek(63 - len(wbdFilename), 1)
                        else:
                                break
                else:
                        break
                wbdOffset = f.read(4)
        f.close()

        # WBD
        f = open("F:\\MTV Music Generator 3\\outputx.wbd", "rb")
        for i in wbd.items():
                if i[0] != "":
                        outputxfile = "F:\\MTV Music Generator 3\\" + i[0]
                        if not os.path.exists(os.path.split(outputxfile)[0]):
                                os.makedirs(os.path.split(outputxfile)[0])
                        f2 = open(outputxfile, "wb+")
                        f.seek(i[1]["Offset"], 0)
                        print("WHD - Writing File: " + i[0])
                        f2.write(f.read(i[1]["Length"]))
        f.close()

def extractDBD():
        # opening data from dbbody.dbd requires the WBD to be extracted first
        # open the SampleBase
        f = open("F:\\MTV Music Generator 3\\Database\\dbheader.dbh", "rb")
        dbdGenres = []
        dbdCategories = []
        f.seek(12, 0)
        for i in range (0, 4):
                dbdCategories.append(cstring(f))
                f.seek(31 - len(dbdCategories[-1]), 1)
        dbdSubcategories = {}
        dbdSources = {}
        f.seek(144, 0)
        genrePos = f.tell()
        # there are only ten genres, genre one is zero
        while len(dbdGenres) < 10:
                dbdGenres.append(cstring(f))
                print("DBD - Genre: " + dbdGenres[-1])
                # subcategories need to be by category, per genre, and the actual values are in a list not a dictionary
                dbdSubcategories[dbdGenres[-1]] = {}
                f.seek(39 - len(dbdGenres[-1]), 1)
                for i in dbdCategories:
                        categoryPos = f.tell()
                        # the subcategories for this category for this genre
                        dbdSubcategories[dbdGenres[-1]][i] = []
                        while f.tell() - categoryPos < 192:
                                dbdSubcategory = cstring(f)
                                # if there's no string here, it's on to the sources and then the next genre
                                if dbdSubcategory == false:
                                        break
                                print("DBD - " + i + " Subcategory: " + dbdSubcategory)
                                dbdSubcategories[dbdGenres[-1]][i].append(dbdSubcategory)
                                f.seek(31 - len(dbdSubcategory), 1)
                        f.seek(192 + categoryPos, 0)
                f.seek(1, 1)
                categoryPos = f.tell()
                dbdSources[dbdGenres[-1]] = []
                dbdSource = cstring(f)
                while dbdSource != false and f.tell() - genrePos < 1072:
                        print("DBD - " + dbdGenres[-1] + " Source: " + dbdSource)
                        dbdSources[dbdGenres[-1]].append(dbdSource)
                        f.seek(31 - len(dbdSource), 1)
                        dbdSource = cstring(f)
                f.seek(1072 + genrePos, 0)
                genrePos = f.tell()
                continue
        
        dbd = {}
        dbdBits = 16
        dbdFrequency = 48000
        f.seek(10866, 0)
        # could use the length of the file - or not ;)
        while f.tell() < 220320:
                dbdBars = struct.unpack("<H", f.read(2))[0]
                dbdGenre = dbdGenres[struct.unpack("<I", f.read(4))[0]]
                dbdCategory = dbdCategories[struct.unpack("<I", f.read(4))[0]]
                dbdSubcategory = dbdSubcategories[dbdGenre][dbdCategory][struct.unpack("<I", f.read(4))[0]]
                dbdSource = dbdSources[dbdGenre][struct.unpack("<I", f.read(4))[0]]
                f.seek(8, 1)
                dbdLength = struct.unpack("<I", f.read(4))[0]
                # a bar is two beats, the length is in bytes and two bytes make one sample, there are 48000 samples in one second, and we need them per minute so we divide by 60
                dbdOffset = struct.unpack("<I", f.read(4))[0]
                f.seek(4, 1)
                dbdName = cstring(f)
                print("DBD - Name: " + dbdName)
                dbd[dbdName] = {"Length": dbdLength,
                                      "Offset": dbdOffset,
                                      "Genre": dbdGenre,
                                      "Category": dbdCategory,
                                      "Subcategory": dbdSubcategory,
                                      "Source": dbdSource}
                if dbdGenre == "House":
                        dbd[dbdName]["BPM"] = 125
                elif dbdGenre == "Trance":
                        dbd[dbdName]["BPM"] = 137
                elif dbdGenre == "Techno":
                        dbd[dbdName]["BPM"] = 138
                elif dbdGenre == "Drum & Bass":
                        dbd[dbdName]["BPM"] = 174
                elif dbdGenre == "Hip Hop":
                        dbd[dbdName]["BPM"] = 125
                elif dbdGenre == "UK Garage":
                        dbd[dbdName]["BPM"] = 138
                elif dbdGenre == "Snoop":
                        dbd[dbdName]["BPM"] = 97
                elif dbdGenre == "Outkast":
                        dbd[dbdName]["BPM"] = 125
                elif dbdGenre == "Sean Paul":
                        dbd[dbdName]["BPM"] = 100
                elif dbdGenre == "Fabolous":
                        dbd[dbdName]["BPM"] = 82
                else:
                        dbd[dbdName]["BPM"] = ""
                f.seek(21 - len(dbdName), 1)
        f.close()

        f2 = open("F:\\MTV Music Generator 3\\Database\\dbbody.dbd", "rb")
        for i in dbd.items():
                if i[0] and i[0] != "":
                        samplebasedir = "F:\\MTV Music Generator 3\\Database\\" + i[1]["Genre"] +  "\\" + i[1]["Category"] +  "\\" + i[1]["Subcategory"] +  "\\" + i[0] +  ".wav"
                        if not os.path.exists(os.path.split(samplebasedir)[0]):
                                os.makedirs(os.path.split(samplebasedir)[0])
                        f = open(samplebasedir, "wb+")
                        # need to fetch from dbbody first
                        f.write(bytes("RIFF", "UTF-8"))
                        # write file size
                        WAVERIFFLength = 36 + i[1]["Length"] + 16
                        WAVELISTLength = 109 + len(i[1]["Genre"]) + len(i[1]["Source"]) + len(i[0])
                        if len(i[1]["Genre"]) % 2 == 0:
                                WAVELISTLength += 1
                        if len(i[1]["Source"]) % 2 == 0:
                                WAVELISTLength += 1
                        if len(i[0]) % 2 == 0:
                                WAVELISTLength += 1
                        WAVEID3v2Length = 105 + len(i[1]["Genre"]) + len(i[1]["Source"]) + len(i[0])
                        f.write(struct.pack("<I", WAVERIFFLength + WAVELISTLength + WAVEID3v2Length))
                        f.write(bytes("WAVE", "UTF-8"))
                        f.write(bytes("fmt ", "UTF-8"))
                        # Chunk Size
                        f.write(struct.pack("<I", 16))
                        # Codec (PCM)
                        f.write(struct.pack("<H", 1))
                        # Channels
                        f.write(struct.pack("<H", 1))
                        # Sample Rate measured in Hz
                        f.write(struct.pack("<I", dbdFrequency))
                        # Sample Rate measured in bytes
                        f.write(struct.pack("<I", int(dbdFrequency*dbdBits/8)))
                        # Block alignment
                        f.write(struct.pack("<H", int(dbdBits/8)))
                        # Bits Per Sample
                        f.write(struct.pack("<H", dbdBits))
                        # Unused Extra Data
                        #f.write(struct.pack("<H", 0))
                        f.write(bytes("data", "UTF-8"))
                        f.write(struct.pack("<I", i[1]["Length"]))
                        print("DBD - Sample at Offset: " + str(i[1]["Offset"]))
                        f2.seek(i[1]["Offset"], 0)
                        f.write(f2.read(dbd[i[0]]["Length"]))
                        writeLIST(i, f, WAVELISTLength)
                        writeID3v2(i, f, WAVEID3v2Length)
        f.close()

extractWHD()
extractDBD()
