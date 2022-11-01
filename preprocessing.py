import csv
import regex as re

Kaiser = {
    "Kaiser Friedrich ": [
        "K. F.",
        "König F.",
        "KönigF.",
        "Kg.F.",
        "Kg. F.",
        "Friedrich III.",
        "K.F.",
        "F. ",
    ]
}

titel = {
    "König": ["Kg.", "Ks.", "K."],
    "Königin": ["Kgin."],
    "Könige": ["Kgg."],
    "Herzog": ["Hz.", "Hrz.", "Hzg."],
    "Herzögin": ["Hzn.", "Hzin."],
    "Herzöge": ["Hzz."],
    "Erzherzögin": ["Ehzn."],
    "Landgraf": ["Ldgrf."],
    "Markgraf": ["Mgf."],
    "Markgrafen": ["Mgff."],
    "Freigraf": ["Freigf."],
    "Pfalzgraf": ["Pfgr.", "Pfalzgf.", "PfGr.", "Pfgf."],
    "Grafen": ["Gff."],
    "Graf": ["Gf.", "gf."],
    "Grafschaft": ["Gft."],
    "Gräfin": ["Gfn."],
    "Burggraf": ["Bggf."],
    "Burggrafen": ["Bggff.", "BgGraf"],
    "Erzbischof": ["Eb.", "EB.", "Erzb.", "Ebs."],
    "Erzbischöfe": ["Ebb."],
    "Bischof": ["Bf.", "BF.", "B."],
    "Bischofs": ["Bfs.", "Bf.s"],
    "Bischöfe": ["Bff."],
    "Kurfürst": ["Kf."],
    "Kurfürsten": ["Kff."],
    "Bürger": ["Bg."],
    "Strafe": ["Pön"],
    "Doktor":["Dr.", "Dr. decr."]
}
Abbr = {
    "Herzog Maximillian": ["Herzog M.", "König M."],
    "von": ["v."],
    "Kloster": ["Kl."],
    "Sankt": ["St.", "S."],
    "Herzogtum": ["Hzt."],
    "sein Diener": ["s.D."],
    "Adressat": ["Adr."],
    "August": ["Aug."],
    "Diözese": ["Diöz."],
    "Dezember": ["Dez."],
    "April": ["Apr."],
    "Pfenning": ["'Pfd. Pf.'", "Pf."],
    "Pfund": ["Pfd."],
    "herzöglich": ["hzl."],
    "kaiserlich": ["ksl."],
    "königlich": ["kgl."],
    "heilige": ["hll."],
    "in": [" i."],
    "das heißt": ["i.e."],  # lat: "id est"
    "zum Teil": ["z.T."],
    "Gulden": ["fl. rh.", "Guldenrh.", "Guldenung.", "fl."],
    "römisch": ["röm."],
    "Unbekannt": ["N.N."],
    "Fürstentum": ["Ftm."],
    "sogenannte": ["sog."],
    "": [
        "(nach Kop.)",
        " ung.",
        "Sch.",
    ],  # (nach Kop.)Verweis auf Kopie; ung. - ungarische Goldgulden; Schweizer Pfenning
    "Königreich": ["Kgr."],
}


def preprocessing(file):
    with open(file) as file_obj:
        # Skips the heading
        # Using next() method
        heading = next(file_obj)
        # Create reader object by passing the file
        # object to reader method
        reader_obj = list(csv.reader(file_obj, delimiter="\t"))
        with open("processed" + str(file), "w") as writingFile:
            for row in reader_obj:
                writingFile.write(
                    row[0]
                    + "\t"
                    + row[1]
                    + "\t"
                    + row[2]
                    + "\t"
                    + row[3]
                    + "\t"
                    + del_Tags_resolveAbr(row[4])
                    + "\n"
                )


def del_Tags_resolveAbr(text):
    # (nach <link http://opac.regesta-imperiinde/lang_de/kurztitelsuche_r.php?kurztitel=chmel>Chmel).
    # (nach <span class='smallcaps'>CHMEL</span>)
    # m = re.search("\((\w+| +){3,}\)", text)
    # if m:
    # replacement = m.group(0).replace("(", ", ").replace(")", ",")
    # text = text.replace(m.group(0), replacement)
    # m_klammern = re.search("[a-z]+\([a-z]{1;3}\)[a-z]?+", text)
    # while m_klammern:
    # replacement = m.group(0).replace("(", "").replace(")", "")
    # text = text.replace(m_klammern, replacement)
    # m_klammern = re.search("[a-z]+([a-z]{1;3})[a-z]?+", text)
    while "[" in text or "]" in text:
        text = text.replace("[", "")
        text = text.replace("]", "")
    while "\\xa0ung" in text:
        text = text.replace("\\xa0ung", text)
    while "<em>" in text or "</em>" in text:
        text = text.replace("<em>", "")
        text = text.replace("</em>", "")
    while "<sup>" in text:
        text = text.replace("<sup>", "")
        text = text.replace("</sup>", "")
    while "\\xa0" in text:
        text = text.replace("\\xa0", "")
    for ListValue in Kaiser.values():
        key = str([k for k, v in Kaiser.items() if v == ListValue])
        key = key.strip("[]''")
        for i in ListValue:
            while i in text:
                text = text.replace(i, key)
    for ListValue in titel.values():
        key = str([k for k, v in titel.items() if v == ListValue])
        key = key.strip("[]''")
        for i in ListValue:
            while i in text:
                text = text.replace(i, key)
    for ListValue in Abbr.values():
        key = str([k for k, v in Abbr.items() if v == ListValue])
        key = key.strip("[]''")
        for i in ListValue:
            while i in text:
                text = text.replace(i, key)
    while "  " in text:
        text = text.replace("  ", " ")
    while ",," in text:
        text = text.replace(",,", ",")
    while ",," in text:
        text = text.replace(",,", ",")
    while "König&nbsp;" in text:
        text = text.replace("König&nbsp;", ",")
    return text


preprocessing("RI_13Hefte.csv")
