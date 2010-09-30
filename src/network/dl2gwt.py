import sys

for infile in sys.argv[1:]:
    outFile = ".".join(infile.split(".")[:-1])+".gwt"
    f = open(infile)
    f2 = open(outFile, "w")
    writeOn = False
    for line in f.readlines():
        if not writeOn:
            try:
                if line.split()[0].strip() == "N":
                    f2.write(line.split()[2].strip()+"\n")
                if line.strip() == "DATA:":
                    writeOn = True
            except:
                continue
        else:
            if line.startswith("!"):
                writeOn = False
                continue
            f2.write(line)
            
    f.close()
    f2.close()
