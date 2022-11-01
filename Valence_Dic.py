import csv
import spacy
import regex as re
from roman_number_tokinazation import tokenize_roman_numbers


# Set Dictionary
def getValenceDic():
    nlp = spacy.load("de_core_news_sm")
    # Apply special Tokanization Rules conserning Roman Numbers
    specialCases = tokenize_roman_numbers()
    for case in specialCases:
        nlp.tokenizer.add_special_case
    ValenceDic = {}
    with open("GermanPolarityClues-Negative-21042012.tsv", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter="\t")
        for row in reader:
            count = 0
            valence = 0
            matches = re.findall("[0-9](.[0-9]+)?]", str(row))
            for i in matches:
                count += 1
                valence = -(valence + i.group(0))
            try:
                ValenceDic[row[0]] = valence / count
            except ZeroDivisionError:
                ValenceDic[row[0]] = -1
    with open("GermanPolarityClues-Positive-21042012.tsv", newline="") as csvfile:
        reader = csv.reader(csvfile, delimiter="\t")
        for row in reader:
            count = 0
            valence = 0
            matches = re.findall("[0-9](.[0-9]+)?]", str(row))
            for i in matches:
                count += 1
                valence = valence + i.group(0)
            try:
                ValenceDic[row[0]] = valence / count
            except ZeroDivisionError:
                ValenceDic[row[0]] = 1
    return ValenceDic


def expandValenceDic(ValDic, file, window):
    newValDic = {}
    countDic = {}
    nlp = spacy.load("de_core_news_sm")
    # Apply special Tokanization Rules conserning Roman Numbers
    specialCases = tokenize_roman_numbers()
    for k, v in specialCases.items():
        special_case = v
        nlp.tokenizer.add_special_case(k, special_case)
    with open(file) as file_obj:
        reader_obj = list(csv.reader(file_obj, delimiter="\t"))
        for row in reader_obj:
            text = nlp(row[4])
            for token in text:
                if token.pos_ == "VERB" or token.pos_ == "ADJ":
                    List = []
                    ra = range(-window, window)
                    for i in ra:
                        try:
                            List.append(text[token.i + i])
                        except IndexError:
                            pass
                        valence = 0
                        for word in List:
                            if (
                                word.text in ValDic.keys()
                                and word.pos_ != "$"
                                and word.pos_ != "$."
                                and word.pos_ != "$("
                            ):
                                valence = valence + ValDic[word.text]
                        if valence != 0:
                            if token.text not in newValDic.keys():
                                newValDic[token.text] = 0
                                countDic[token.text] = 0
                            countDic[token.text] += 1
                            newValDic[token.text] = newValDic[token.text] + valence
    for k in newValDic.keys():
        newValDic[k] = newValDic[k] / countDic[k]
    return newValDic


new_valence_Dictionary = expandValenceDic(getValenceDic(), "processedRI_13Hefte.csv", 7)
print(new_valence_Dictionary)
sorted_Dic = sorted(new_valence_Dictionary.items(), key=lambda x: x[1], reverse=True)
with open("old_valence.csv", "w") as wf:
    old_dic = getValenceDic()
    for key_old in old_dic.keys():
        wf.write(key_old + "\t" + str(old_dic[key_old]) + "\n")
    for i_new in sorted_Dic:
        wf.write(i_new[0] + "\t" + str(i_new[1]) + "\n")
