import spacy
import csv
import datetime
from randomizer import random_samples_from_csv
from roman_number_tokinazation import tokenize_roman_numbers
from Emotion_Analysis import (
    getTriples,
    getVariablesFromSubject,
    getVariablesFromObject,
    ApplyEmotionModelRules,
    getTextFromNumber,
)
from agentFondness import makeAgentFondness, getAgentFondness
from getURI import getURLfromNumber


def ApplyEmotionModel(numOfSamples, file):
    EmotionCountDic = {
        "happy-for": 0,
        "resentment": 0,
        "gloating": 0,
        "sorry_for": 0,
        "satisfaction": 0,
        "fear-confirmed": 0,
        "relief": 0,
        "disappointment": 0,
        "joy": 0,
        "distress": 0,
        "gratification": 0,
        "remorse": 0,
        "gratitude": 0,
        "anger": 0,
        "admiration": 0,
        "pride": 0,
        "shame": 0,
        "reproach": 0,
    }
    now = datetime.datetime.now()
    nlp = spacy.load("de_core_news_sm")
    # Apply special Tokanization Rules conserning Roman Numbers
    specialCases = tokenize_roman_numbers()
    for k, v in specialCases.items():
        special_case = v
        nlp.tokenizer.add_special_case(k, special_case)
    Output_List = []
    # Takes a given number of randomized Regesta from 13_Hefte.csv
    samples = random_samples_from_csv(file, numOfSamples)
    # Iterates through the random samples (lines)
    with open("Output.csv", "w") as wf:
        writer = csv.writer(wf)
        for i in samples:
            if len(i) == 3:
                del i[0]
            doc = i[1]
            Triples = getTriples(i[0], doc, file)
            for tuple in Triples:
                makeAgentFondness(tuple)
                try:
                    tuple["Subject"]["agentFondness"] = getAgentFondness(tuple)[0]
                    tuple["Subject"]["agentFondness"] = getAgentFondness(tuple)[2]
                except TypeError:
                    pass
                em = None
                variables = getVariablesFromSubject(tuple)
                if not variables:
                    break
                emotions = ApplyEmotionModelRules(variables)
                em = str(emotions["Emotions"])
                em = em.replace("'", "").replace("[", "").replace("]", "")
                Sub_RI_ID = tuple["Subject"]["RI_ID"]
                Obj_RI_ID = tuple["Object"]["RI_ID"][0]
                if Sub_RI_ID and Obj_RI_ID and em:
                    EmotionCountDic = updateEmotionCountID(em, EmotionCountDic)
                    writer.writerow([
                        "ri:"
                        + str(Sub_RI_ID),
                        "occ:feels",
                        "_:"
                        + em
                        + "_"
                        + str(EmotionCountDic[em])])
                    writer.writerow([
                        "_:"
                        + em
                        + "_"
                        + str(EmotionCountDic[em]),
                        "occ:towards",
                        "ri:"
                        + str(Obj_RI_ID)])
                    writer.writerow([
                        "_:"
                        + em
                        + "_"
                        + str(EmotionCountDic[em]),
                        "rdfs:describedBy",
                        "<"
                        + str(getURLfromNumber(tuple["number"]))
                        + ">"])
            for tuple in Triples:
                makeAgentFondness(tuple)
                try:
                    tuple["Subject"]["agentFondness"] = getAgentFondness(tuple)[0]
                    tuple["Subject"]["agentFondness"] = getAgentFondness(tuple)[2]
                except TypeError:
                    pass
                em = None
                variables = getVariablesFromObject(tuple)
                if not variables:
                    break
                emotions = ApplyEmotionModelRules(variables)
                em = str(emotions["Emotions"])
                em = em.replace("'", "").replace("[", "").replace("]", "")
                Sub_RI_ID = tuple["Subject"]["RI_ID"]
                Obj_RI_ID = tuple["Object"]["RI_ID"]
                if Sub_RI_ID and Obj_RI_ID and em:
                    wf.write("> **Subjekt**:" + str(tuple["Subject"]) + "\n\n")
                    wf.write("> **Aktion**" + str(tuple["Action"]) + "\n\n")
                    wf.write("> **Objekt**" + str(tuple["Object"]) + "\n\n")
                    for k, v in emotions.items():
                        wf.write(str(k) + ":" + str(v) + "\n\n")
                    Sub_RI_ID = tuple["Subject"]["RI_ID"]
                    Obj_RI_ID = tuple["Object"]["RI_ID"][0]
                    if Sub_RI_ID and Obj_RI_ID:
                        writer.writerow([
                            "ri:"
                            + Sub_RI_ID,
                            "occ:feels",
                            "_:"
                            + em
                            + "_"
                            + str(EmotionCountDic[em])])
                        writer.writerow([
                            "_:"
                            + em
                            + "_"
                            + str(EmotionCountDic[em]),
                            "occ:towards",
                            "ri:"
                            + Obj_RI_ID])
                        writer.writerow([
                            "_:"
                            + em
                            + "_"
                            + str(EmotionCountDic[em]),
                            "rdfs:describedBy",
                            str(getURLfromNumber(tuple["number"]))])
    return 'DONE'


def updateEmotionCountID(em, Dic):
    Dic[em] += 1
    return Dic


with open("RDF_File.txt", "w") as wf:
    wf.writelines(ApplyEmotionModel(5, "processedRI_13Hefte.csv"))
