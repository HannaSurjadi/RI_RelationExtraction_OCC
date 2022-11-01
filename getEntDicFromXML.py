import lxml.etree as ET
import regex as re
import os


def feDicFromXML(number):
    Dic = {}
    startfile = open("XML_Dic.txt", "w")
    startfile.write("Regest\tEnitäten")
    startfile.close()
    unimParents = ["section", "body", "document", "Inhalt", "nr", "Regestennummer"]
    for item in os.listdir("registry-f3-master/"):
        print(item)
        with open("registry-f3-master/" + item, "r") as f:
            root = ET.parse(f)
            Nennungen = root.iter("nr")
            for nr in Nennungen:
                if nr.attrib["type"] != "austOrt":
                    parList = []
                    Nennungsnr = nr.text
                    m = re.search("^#" + str(number) + "-", Nennungsnr)
                    if m:
                        par = None
                        ID = None
                        for i in nr.iterancestors():
                            if i.tag not in unimParents:
                                try:
                                    if i.attrib["typ"] != "ereignis":
                                        pass
                                except KeyError:
                                    pass
                                if not ID:
                                    ID = i.attrib["id"]
                                par = i.find("Inhalt").text
                                if par:
                                    par = par.replace("\n", "").replace("\t", "")
                                    par = re.sub("\s{2,}", " ", par)
                                    parList.append(par)
                        try:
                            if Nennungsnr in Dic.keys():
                                Dic[Nennungsnr] = (
                                    Dic[Nennungsnr].replace("}", "")
                                    + ","
                                    + '"'
                                    + ID
                                    + '"'
                                    + ": "
                                    + str(parList)
                                    + "}"
                                    )
                            else:
                                Dic[Nennungsnr] = (
                                    ": {" + '"' + ID + '"' + ": " + str(parList) + "}"
                                    )
                        except UnboundLocalError:
                            pass
    return Dic


def saveDictocsv(Dic, filename):
    with open(filename, "w") as f:
        for k, v in Dic.items():
            f.write(k + "\t" + v + "\n")


for num in range(36):
    saveDictocsv(feDicFromXML(num), "#" + str(num) + "_Enitäten.csv")

num = "CA"
saveDictocsv(feDicFromXML(num), "#" + num + "_Enitäten.csv")
