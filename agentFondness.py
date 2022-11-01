def makeAgentFondness(truple):
    with open("fondeness_log.csv", "w") as f:
        pass
    with open("fondeness_log.csv", "r+") as readWriteFile:
        reader = readWriteFile.readlines()
        data = []
        for r in reader:
            r = r.split("\t")
            print(r)
            if r[0] == tuple["Object"]["RI_ID"] and r[2] == tuple["Subject"]["RI_ID"]:
                if r[1] == "likes" and float(tuple["Action"]["Valance"]) < 0:
                    r[1] = "neutral"
                elif r[1] == "likes" and float(tuple["Action"]["Valance"]) > 0:
                    pass
                if r[1] == "dislikes" and float(tuple["Action"]["Valance"]) < 0:
                    pass
                elif r[1] == "dislikes" and float(tuple["Action"]["Valance"]) > 0:
                    r[1] = "neutral"
                if r[1] == "neutral" and float(tuple["Action"]["Valance"]) < 0:
                    r[1] = "dislikes"
                elif r[1] == "neutral" and float(tuple["Action"]["Valance"]) > 0:
                    r[1] = "likes"
            elif float(tuple["Action"]["Valance"]) < 0:
                readWriteFile.write(
                    tuple["Object"]["RI_ID"]
                    + "\t"
                    + "dislikes"
                    + "\t"
                    + tuple["Subject"]["RI_ID"]
                    + "\n"
                )
            elif float(tuple["Action"]["Valance"]) > 0:
                readWriteFile.write(
                    tuple["Object"]["RI_ID"]
                    + "\t"
                    + "likes"
                    + "\t"
                    + tuple["Subject"]["RI_ID"]
                    + "\n"
                )
            data.append(r)
        readWriteFile.writelines(data)


def getAgentFondness(tuple):
    Subject = False
    Object = False
    with open("fondeness_log.csv", "r+") as readWriteFile:
        reader = readWriteFile.readlines()
        for r in reader:
            r = r.split("\t")
            if r[0] == tuple["Object"]["RI_ID"] and r[2] == tuple["Subject"]["RI_ID"]:
                Object = r[1]
            elif r[0] == tuple["Subject"]["RI_ID"] and r[2] == tuple["Object"]["RI_ID"]:
                Subject = r[1]
    if Subject and Object:
        return Subject, Object
