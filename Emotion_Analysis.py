import spacy
import csv
import random
import regex as re
from Subject_Objekt_Entity_Allignment import getRI_ID
from roman_number_tokinazation import tokenize_roman_numbers


def random_samples_from_csv(file, number_of_samples):
    with open(file) as file_obj:
        # Create reader object by passing the file
        # object to reader method
        reader_obj = list(csv.reader(file_obj, delimiter="\t"))

        # Iterate over each row in the csv file
        # using reader object
        # Determin number of rows
        lenght = len(reader_obj)
        # create a list for the random line numbers
        random_lines = []
        # set a range of how many random examples you wish
        for i in range(number_of_samples):
            # find a random number in the line numbers
            random_lines.append(random.randrange(1, lenght))
            # for the random line numbers print the number and the content of the fourth
            # column - in this case 'summary'
        output = []
        for i in random_lines:
            output.append([i, reader_obj[i][0], reader_obj[i][4]])
        return output


def getTextFromNumber(number, file):
    with open(file) as rf:
        reader_obj = rf.readlines()
        for row in reader_obj:
            row = row.split("\t")
            if row[0] == number:
                return row[4]


def get_valence_Dic():
    ValenceDic = {}
    # Load the ValenceDic from the cvs file.
    with open("old_valence.csv", "r") as rf:
        read_obj = csv.reader(rf, delimiter="\t")
        for row in read_obj:
            ValenceDic[row[0]] = row[1]
    return ValenceDic


def desgleichenTripleChange(number, file):
    m = re.search("n. [0-9]+", number)
    Regest = m.group(0).replace("n. ", "")
    Regest = int(Regest)
    BezugsRegest = Regest - 1
    BezugsRegest = number.replace(str(Regest), str(BezugsRegest))
    with open(file, "r") as rf:
        readerObj = rf.readlines()
        for row in reversed(readerObj):
            row = row.split("\t")
            if BezugsRegest.strip('\n \t') == row[0].strip('\n \t'):
                if not 'Kaiser Friedrich desgleichen an' in row[4]:
                    print(row[4])
                    return [row[4], BezugsRegest]
                else:
                    number = BezugsRegest
                    m = re.search("n. [0-9]+", number)
                    Regest = m.group(0).replace("n. ", "")
                    Regest = int(Regest)
                    BezugsRegest = Regest - 1
                    BezugsRegest = number.replace(str(Regest), str(BezugsRegest))



def get_Action_Dic(token):
    ValenceDic = get_valence_Dic()
    ActionDic = {
        "Text": token.text,
        "pos": token.pos_,
        "form": token.morph.to_dict(),
        "subtree":token.subtree
    }
    if token.text in ValenceDic.keys():
        ActionDic["valence"] = ValenceDic[token.text]
    return ActionDic


def getObjektOrSubjektDic(token, s, number, ValenceDic):
    Dic = {
        "Text": token.text,
        "pos": token.pos_,
        "form": token.morph.to_dict(),
        "RI_ID": getRI_ID(number, token),
    }
    try:
        if token.text == "Kaiser" and s[token.i + 1].text == "Friedrich":
            Dic["RI_ID"] = "F00001419"
        elif token.text == "Friedrich" and s[token.i - 1].text == "Kaiser":
            Dic["RI_ID"] = "F00001419"
    except IndexError:
        pass
    try:
        Dic["valence"] = get_valence_Dic()[token.text]
    except KeyError:
        for i in list(token.subtree):
            SubValence = 0
            if i.text in ValenceDic.keys():
                SubValence = SubValence + float(ValenceDic[i.text])
            Dic["valence"] = SubValence
    return Dic


def EventAllignment(triples, sentences):
    Entities = []
    for tuple in triples:
        number = tuple["number"]
        if tuple["Object"]["RI_ID"]:
            Entities.append(tuple["Object"]["Text"])
        elif tuple["Subject"]["RI_ID"]:
            Entities.append(tuple["Subject"]["Text"])
        if not (
            (tuple["Object"]["RI_ID"] or tuple["Subject"]["RI_ID"])
            and "valence" not in tuple["Object"].keys()
        ):
            for s in sentences:
                entTokens = None
                for token in s:
                    if (
                        token.text == tuple["Object"]["Text"]
                        and not tuple["Object"]["RI_ID"]
                    ) or (
                        token.text == tuple["Subject"]["Text"]
                        and not tuple["Subject"]["RI_ID"]
                    ):
                        for subToken in token.subtree:
                            if subToken.pos_ == ("ADP"):
                                entTokens = []
                                ActionDic = get_Action_Dic(token)
                                for subToken in token.subtree:
                                    if subToken.text in Entities:
                                        entTokens.append(subToken)
                        if entTokens:
                            for ent1 in entTokens:
                                SubjectDic = getObjektOrSubjektDic(
                                    ent1, s, number, ValenceDic
                                )
                                for ent2 in entTokens:
                                    if ent1.text != ent2.text:
                                        ObjectDic = getObjektOrSubjektDic(
                                            ent2, s, number, ValenceDic
                                        )
                                        newTriple = {
                                            "number": number,
                                            "Subject": SubjectDic,
                                            "Action": ActionDic,
                                            "Object": ObjectDic,
                                        }
                                        if (
                                            newTriple not in triples
                                            and newTriple["Subject"]["RI_ID"]
                                            and newTriple["Object"]["RI_ID"]
                                        ):
                                            triples.append(newTriple)
    return triples


def getTriples(number, text, file):
    alternativeRegest = False
    SubjectDic = False
    ObjectDic = False
    ActionDic = False
    ActionAdditionDep = ["nk", "adc", "ag", "og", "pg", "oc", "ng", "da", "sb"]
    global ValenceDic
    ValenceDic = get_valence_Dic()
    nlp = spacy.load("de_core_news_lg")
    if "desgleichen" in text or "Desgleichen" in text:
        alternativeRegest = desgleichenTripleChange(number, file)
    # Apply special Tokanization Rules conserning Roman Numbers
    specialCases = tokenize_roman_numbers()
    for k, v in specialCases.items():
        special_case = v
        nlp.tokenizer.add_special_case(k, special_case)
        sentences = [i for i in nlp(text).sents]
    global sentence_ID
    sentence_ID = 0
    triples = []
    global sents_id_txt
    sents_id_txt = {}
    if alternativeRegest:
        PrimaryObject = text.split(' an ')[1]
        PrimaryObject = nlp(PrimaryObject)
        for t in PrimaryObject:
            t = getObjektOrSubjektDic(t, sentences[0], number, ValenceDic)
            if t['RI_ID']:
                PrimaryObject = t
                break
        alternativeRegest = getTriplesProceedingFromSubject(nlp(alternativeRegest[0]), alternativeRegest[1], ValenceDic)
        SubjectDic = alternativeRegest[0]["Subject"]
        ActionDic = alternativeRegest[0]["Action"]
        triple = {
            "number": number,
            "Subject": SubjectDic,
            "Action": ActionDic,
            "AgentObject": PrimaryObject,
        }
        return [triple]
    else:
        for s in sentences:
            sentence_ID += 1
            sents_id_txt[str(sentence_ID)] = s.text
            triples.append(getTriplesProceedingFromSubject(s, number, ValenceDic))
            print(triples)
            triples.append(getTriplesProceedingFromObjects(s, number, ValenceDic))
    triples = assembleTriples(triples)
    return triples

# Function that takes a spacy-sentence-Object, the number of regest and a ValenceDictionary
# and returns a triple in the Form of a Dicitonary {number:'numer of regest', Subject: {...}, Action: {...}, Object: {...}, AgentObject: {...}}
def getTriplesProceedingFromSubject(s, number, ValenceDic):
    # Defines a List to save triples in
    triples = []
    # sets Variables for the quadtriple Dicionaries
    SubjectDic = None
    ActionDic = None
    # Goes through each toke in the sentence
    for token in s:
        # Goes trough all Verbs in the sentence
        if token.pos_ == 'VERB':
            # Defines the Action trough the found verb
            ActionDic = get_Action_Dic(token)
            # Goes through all direct children of the verb and finds subjects
            for child1 in token.children:
                if child1.dep_ == 'sb':
                    # Defines the SubjectDic through the found subject
                    SubjectDic = getObjektOrSubjektDic(child1, s, number, ValenceDic)
                    # goes through the direct children of the verb again and finds objects
                    for child2 in token.children:
                        if child2.pos_ == 'VERB':
                            try:
                                valence = ValenceDic[child2.text]
                            except KeyError:
                                valence = 0
                            ActionDic['Text'] = ActionDic['Text'] + ' ' + child2.text
                            ActionDic['valence'] = (float(ActionDic['valence']) + float(valence))
                            for child3 in child2.children:
                                if child3.dep_ == 'oa' or child3.dep_ == 'da':
                                    triples.extend(getTriplesProceedingFromSubjectSUB(child3, number, SubjectDic, ActionDic, s))
                        if child2.dep_ == 'oa' or child2.dep_ == 'da':
                            triples.extend(getTriplesProceedingFromSubjectSUB(child2, number, SubjectDic, ActionDic, s))
    print(triples)
    return triples


def getTriplesProceedingFromSubjectSUB(child, number, SubjectDic, ActionDic, s):
     # creates or emties the triple Dicitonary so that no Object is adopted
     triples = []
     ObjectDic = None
     AgentObjectDic = None
     # from a former triple
     triple = {}
     # save the number of regest in each triple, for the URI Grabber
     triple["number"] = number
     # Defines the object as AgentObject
     AgentObjectDic = getObjektOrSubjektDic(child, s, number, ValenceDic)
     # saves found Dictionaries in the triple
     triple['Subject'] = SubjectDic
     triple['Action'] = ActionDic
     triple['Object'] = ObjectDic
     triple['AgentObject'] = AgentObjectDic
     # appends triple to the triples list only if Subject and AgentObject
     # have RI_IDs and if Subject and AgentObject are not the same
     if triple['Subject']['RI_ID'] and triple['AgentObject']['RI_ID'] and triple['Subject']['RI_ID']!= triple['AgentObject']['RI_ID']:
         if triple not in triples:
             triples.append(triple)
     # if the Agent Object has no RI-ID and it is found in the ValenceDictionary it is set as triple['Object']
     elif not triple['AgentObject']['RI_ID']:
         ID = getRI_ID(number, child)
         if not ID:
             try:
                 valence = ValenceDic[child.text]
                 ObjectDic = getObjektOrSubjektDic(child, s, number, ValenceDic)
             except KeyError:
                 pass
     # In case there is a conjunction in the subtree of the AgentObject an other triple with the same Subjet and Object is added.
     for sub in child.subtree:
         if sub.dep_ == 'oa' or sub.dep_ == 'da' or sub.dep_ == 'nk' or sub.dep_ == 'ag' or sub.dep_ == 'oc' or sub.dep_ == 'og'  or sub.dep_ == 'nk' or sub.dep_ == 'cj':
             triple = {'number': number}
             AgentObjectDic = getObjektOrSubjektDic(sub, s, number, ValenceDic)
             triple['Subject'] = SubjectDic
             triple['Action'] = ActionDic
             triple['Object'] = ObjectDic
             triple['AgentObject'] = AgentObjectDic
             if triple['Subject']['RI_ID'] and triple['AgentObject']['RI_ID'] and triple['Subject']['RI_ID']!= triple['AgentObject']['RI_ID']:
                 if triple not in triples:
                     triples.append(triple)
     return triples


def assembleTriples(triplesList):
    newTriples = []
    for triples in triplesList:
        for t1 in triples:
            for t2 in triples:
                if not (isinstance(t1, list) or isinstance(t2, list)):
                    if t1['Subject'] == t2['Subject'] and t1['Action'] == t2['Action'] and t1['Object'] == t2['Object'] and t1['AgentObject']['RI_ID'] == t2['AgentObject']['RI_ID'] and t2['AgentObject']['RI_ID'] != None:
                        if t2['AgentObject']['Text'] not in t1['AgentObject']['Text']:
                            t1['AgentObject']['Text'] = t1['AgentObject']['Text'] + ' ' + t2['AgentObject']['Text']
                            triples.remove(t2)
        newTriples.extend(triples)
    return newTriples


# Finds [Ereignis]-gegen und zwischen[Ereignis]&[Ereignis] patterns.
def getTriplesProceedingFromObjects(s, number, ValenceDic):
    triples = []
    triple = {}
    triple["number"] = number
    for token in s:
        SubjectDic = False
        ActionDic = False
        AgentObjectDic = False
        try:
            if token.text == 'gegen' and s[token.i-1].pos_ == 'NOUN':
                try:
                    valence = ValenceDic[s[token.i-1].text]
                    ActionDic = get_Action_Dic(s[token.i-1])
                    ActionDic['Text'] = ActionDic['Text'] + ' gegen'
                    for gen in s[token.i-1].subtree:
                        if gen.dep_ == 'ag' or gen.dep_ == 'og' or gen.dep_ == 'pg':
                            SubjectDic = getObjektOrSubjektDic(gen, s, number, ValenceDic)
                    for potEnt in token.subtree:
                        ID = getRI_ID(number, potEnt)
                        if ID:
                            triple['Subject'] = SubjectDic
                            triple['Action'] = ActionDic
                            triple['Object'] = None
                            triple['AgentObject'] = getObjektOrSubjektDic(potEnt, s, number, ValenceDic)
                            triples.append(triple)
                except KeyError:
                    pass
        except IndexError:
            pass
        SubjectDic = False
        ActionDic = False
        AgentObjectDic = False
        try:
            if token.text == 'zwischen' and s[token.i-1].pos_ == 'NOUN':
                try:
                    valence = ValenceDic[s[token.i-1].text]
                    ActionDic = get_Action_Dic(s[token.i-1])
                    ActionDic['Text'] = ActionDic['Text'] + ' gegen'
                    for potEnt in token.subtree:
                        ID = getRI_ID(number, potEnt)
                        if ID and not SubjectDic:
                            SubjectDic = getObjektOrSubjektDic(potEnt, s, number, ValenceDic)
                            triple['Subject'] = SubjectDic
                            triple['Action'] = ActionDic
                            triple['Object'] = None
                        elif ID and not ID == SubjectDic['RI_ID']:
                            AgentObjectDic = getObjektOrSubjektDic(potEnt, s, number, ValenceDic)
                            triple['AgentObject'] = AgentObjectDic
                            if triple not in triples:
                                triples.append(triple)
                            AgentObjectDic = False
                except KeyError:
                    pass
        except IndexError:
            pass
    return triples



def getVariablesFromSubject(triple):
    print(triple)
    # Setting variables
    # [distress,sorry_for,resentment,gloating,hope,fear,satisfaction,fear_confirmed,relief,dissapointment,pride,shame,admiration,reproach,love,hate,joy,gratification,remorse,gratitude,anger,shock,surprise]
    af, de, of, sp, op, oa, sr, sa, stat, unexp, = (
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
    )
    try:
        sub = triple["Subject"]
        act = triple["Action"]
        obj = triple["AgentObject"]
        sub_val = float(sub["valence"])
        if not sub_val:
            sub_val = 0
        act_val = float(act["valence"])
        if not act_val:
            act_val = 0
        obj_val = float(obj["valence"])
        if not obj_val:
            obj_val = 0
    except KeyError:
        return None
    if sub_val > 0:
        af = "liked"
    elif sub_val < 0:
        af = "not liked"
    else:
        af = "neutral"
    if act_val > 0.5:
        sa = "praiseworthy"
    elif act_val < -0.5:
        sa = "blameworthy"
    else:
        sa = "neutral"
    for t in act.values():
        if t == "PRON" or t == "PRF" or t == "PPOSS" or t == "PPOSS":
            de = "self"
        else:
            de = "other"
    if obj_val + act_val < 0:
        sr = "displeased"
        sp = "undesirable"
    elif obj_val + act_val > 0:
        sr = "pleased"
        sp = "desirable"
    else:
        sr = "neutral"
        sp = "neutral"
    if obj_val > 0:
        of = "liked"
        oa = "attractive"
    elif obj_val < 0:
        of = "not liked"
        oa = "not attractive"
    else:
        of = "neutral"
    if sp == "desirable" and oa == "not liked" and de == "other":
        op = "undesirable"
    elif sp == "undesirable" and oa == "not liked" and de == "other":
        op = "desirable"
    elif sp == "undesirable" and oa == "liked" and de == "other":
        op = "undesirable"
    elif sp == "desirable" and oa == "liked" and de == "other":
        op = "desirable"
    for i in conf_list:
        if i in act.values():
            stat = "confirmed"
    con_pos = []
    adv_List = []
    for i in act["subtree"]:
        con_pos.append(i.pos_)
        if i.pos_ == "ADV":
            adv_List.append(i.text)
        for adv in adv_List:
            if adv in conf_adv:
                stat = "confirmed"
            elif adv in uncon_adv:
                stat = "unconfirmed"
    if (
        "VVPP" in con_pos
        or "VAPP" in con_pos
        or "VAFIN" in con_pos
        or "VVPP" in con_pos
    ):
        stat = "confirmed"
    elif (
        "VVPP" in con_pos
        or "VAPP" in con_pos
        or "VAFIN" in con_pos
        or "VVPP" in con_pos
        and "NEG" in con_pos
    ):
        stat = "disconfirmed"
    for i in unexp_list:
        if i in sents_id_txt[str(sentence_ID)]:
            unexp = True
    variableDic = {
        "af": af,
        "sa": sa,
        "de": de,
        "sr": sr,
        "of": of,
        "sp": sp,
        "op": op,
        "oa": oa,
        "stat": stat,
        "unexp": unexp,
    }
    return variableDic


def getVariablesFromObject(triple):
    # Setting variables
    # [distress,sorry_for,resentment,gloating,hope,fear,satisfaction,fear_confirmed,relief,dissapointment,pride,shame,admiration,reproach,love,hate,joy,gratification,remorse,gratitude,anger,shock,surprise]
    af, de, sp, op, oa, sr, sa, stat, unexp, = (
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
        False,
    )
    sub = triple["Object"]
    act = triple["Action"]
    obj = triple["Subject"]
    sub_val = float(sub["valence"])
    if sub_val is None:
        sub_val = 0
    act_val = float(act["valence"])
    if act_val is None:
        act_val = 0
    obj_val = float(obj["valence"])
    if obj_val is None:
        obj_val = 0
    if sub_val > 0:
        af = "liked"
    elif sub_val < 0:
        af = "not liked"
    else:
        af = "neutral"
    if act_val > 0:
        sa = "praiseworthy"
    elif act_val < 0:
        sa = "blameworthy"
    else:
        sa = "neutral"
    for t in act.values():
        if t == "PRON" or t == "PRF" or t == "PPOSS" or t == "PPOSS":
            de = "other"
        else:
            de = "self"
    if obj_val + act_val < 0 and not(triple['Subject']['valence'] <= 0 or triple['Object']['af'] <= 0):
        sr = "displeased"
        sp = "undesirable"
    elif obj_val + act_val > 0 and not(triple['Subject']['valence'] <= 0 or triple['Object']['af'] <= 0):
        sr = "pleased"
        sp = "desirable"
    elif obj_val + act_val < 0 and not(triple['Subject']['valence'] >= 0 or triple['Object']['af'] >= 0):
        sr = "pleased"
        sp = "desirable"
    elif obj_val + act_val > 0 and not(triple['Subject']['valence'] <= 0 or triple['Object']['af'] <= 0):
        sr = "displeased"
        sp = "undesirable"
    else:
        sr = "neutral"
        sp = "neutral"
    if triple['Subject']['RI_ID'] == "F00001419":
        sp = "desirable"
    if obj_val > 0:
        oa = "attractive"
    elif obj_val < 0:
        oa = "not attractive"
    else:
        oa = "neutral"
    if act_val < 0 and de == "other":
        op = "undesirable"
    elif act_val > 0 and de == "other":
        op = "desirable"
    else:
        ope = 'neutral'
    for i in conf_list:
        print(act)
        if i in act["form"].keys():
            stat = "confirmed"
    con_pos = []
    adv_List = []
    for i in act["conformation"]:
        con_pos.append(i.pos_)
        if i.pos_ == "ADV":
            adv_List.append(i.text)
        for adv in adv_List:
            if adv in conf_adv:
                stat = "confirmed"
            elif adv in uncon_adv:
                stat = "unconfirmed"
    if (
        "VVPP" in con_pos
        or "VAPP" in con_pos
        or "VAFIN" in con_pos
        or "VVPP" in con_pos
    ):
        stat = "confirmed"
    elif (
        "VVPP" in con_pos
        or "VAPP" in con_pos
        or "VAFIN" in con_pos
        or "VVPP" in con_pos
        and "NEG" in con_pos
    ):
        stat = "disconfirmed"
    for i in unexp_list:
        if i in sents_id_txt[str(sentence_ID)]:
            unexp = True
    variableDic = {
        "af": af,
        "sa": sa,
        "de": de,
        "sr": sr,
        "of": of,
        "sp": sp,
        "oa": oa,
        "op": op,
        "stat": stat,
        "unexp": unexp,
    }
    return variableDic


def ApplyEmotionModelRules(variableDic):
    emotion_List = []
    if variableDic["sr"] == "displeased" and variableDic["de"] == "self":
        emotion_List.append("distress")
    elif variableDic["sr"] == "displeased" and variableDic["de"] == "other":
        emotion_List.append("sorry_for")
    elif (
        variableDic["sr"] == "displeased"
        and variableDic["op"] == "desirable"
        and variableDic["af"] == "not liked"
        and variableDic["de"] == "other"
    ):
        emotion_List.append("resentment")
    elif (
        variableDic["sr"] == "pleased"
        and variableDic["op"] == "undesirable"
        and variableDic["af"] == "not liked"
        and variableDic["de"] == "other"
    ):
        emotion_List.append("gloating")
    elif (
        variableDic["sr"] == "pleased"
        and variableDic["sp"] == "desirable"
        and variableDic["stat"] == "unconfirmed"
        and variableDic["de"] == "self"
    ):
        emotion_List.append("hope")
    elif (
        variableDic["sr"] == "displeased"
        and variableDic["sp"] == "undesirable"
        and variableDic["stat"] == "unconfirmed"
        and variableDic["de"] == "self"
    ):
        emotion_List.append("fear")
    elif (
        variableDic["sr"] == "pleased"
        and variableDic["sp"] == "desirable"
        and variableDic["stat"] == "confirmed"
        and variableDic["de"] == "self"
    ):
        emotion_List.append("satisfaction")
    elif (
        variableDic["sr"] == "displeased"
        and variableDic["sp"] == "undesirable"
        and variableDic["stat"] == "confirmed"
        and variableDic["de"] == "self"
    ):
        emotion_List.append("fear_confirmed")
    elif (
        variableDic["sr"] == "pleased"
        and variableDic["sp"] == "undesirable"
        and variableDic["stat"] == "disfirmed"
        and variableDic["de"] == "self"
    ):
        emotion_List.append("relief")
    elif (
        variableDic["sr"] == "displeased"
        and variableDic["sp"] == "desirable"
        and variableDic["stat"] == "disconfirmed"
        and variableDic["de"] == "self"
    ):
        emotion_List.append("dissapointment")
    elif (
        variableDic["sr"] == "pleased"
        and variableDic["sa"] == "praiseworthy"
        and variableDic["sp"] == "desirable"
        and variableDic["de"] == "self"
    ):
        emotion_List.append("pride")
    elif (
        variableDic["sr"] == "displeased"
        and variableDic["sa"] == "blameworthy"
        and variableDic["sp"] == "undesirable"
        and variableDic["de"] == "self"
    ):
        emotion_List.append("shame")
    elif (
        variableDic["sr"] == "pleased"
        and variableDic["sa"] == "praiseworthy"
        and variableDic["op"] == "desirable"
        and variableDic["de"] == "other"
    ):
        emotion_List.append("admiration")
    elif (
        variableDic["sr"] == "displeased"
        and variableDic["sa"] == "blameworthy"
        and variableDic["op"] == "undesirable"
        and variableDic["de"] == "other"
    ):
        emotion_List.append("reproach")
    elif (
        variableDic["sr"] == "pleased"
        and variableDic["of"] == "liked"
        and variableDic["sa"] == "praiseworthy"
        and variableDic["de"] == "other"
    ):
        emotion_List.append("love")
    elif (
        variableDic["sr"] == "displeased"
        and variableDic["of"] == "not liked"
        and variableDic["sa"] == "blameworthy"
        and variableDic["de"] == "other"
    ):
        emotion_List.append("hate")
    elif variableDic["sr"] == "pleased":
        emotion_List.append("joy")
    # rules for complex emotion
    if "joy" in emotion_List and "pride" in emotion_List:
        emotion_List.append("gratification")
    elif "distress" in emotion_List and "shame" in emotion_List:
        emotion_List.append("remorse")
    elif "joy" in emotion_List and "admiration" in emotion_List:
        emotion_List.append("gratitude")
    elif "distress" in emotion_List and "reproach" in emotion_List:
        emotion_List.append("anger")
    elif "distress" in emotion_List and variableDic["unexp"]:
        emotion_List.append("shock")
    elif "joy" in emotion_List and variableDic["unexp"]:
        emotion_List.append("suprise")
    output_Dic = {"Emotions": emotion_List, "Sentence": sents_id_txt[str(sentence_ID)]}
    print(
        "agent fondness (likes, not liked):"
        + str(variableDic["af"])
        + "\n"
        + "direction of emotion"
        + str(variableDic["de"])
        + "\n"
        + "object fondness (liked, not liked)"
        + str(variableDic["of"])
        + "\n"
        + "self presumtion:"
        + str(variableDic["sp"])
        + "\n"
        + "other presumtion (desirable/undesirable)"
        + str(variableDic["op"])
        + "\n"
        + "self reaction valence of event ~ desirability"
        + str(variableDic["sr"])
        + "\n"
        + "self-appraisal"
        + str(variableDic["sa"])
        + "\n"
        + "tense of verb:"
        + str(variableDic["stat"])
        + "\n"
        + "Expectation"
        + str(variableDic["unexp"])
    )
    return output_Dic


def saveEmotionOutput(file, outputList):
    with open(file, "w", newline="") as f:
        fieldnames = ["ID", "Emotions", "Sentence"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i in outputList:
            writer.writerow(i)


conf_list = ["Tense_past", "Tense_pres"]
uncon_adv = [
    "alsbald",
    "bald",
    "beinahe",
    "beizeiten",
    "bisher",
    "erst",
    "fast",
    "möglicherweise",
    "noch",
]
conf_adv = [
    "bereits",
    "endlich",
    "folglich",
    "hierauf",
    "hierdurch",
    "immer",
    "schon",
    "vormals",
]
unexp_list = [
    "plötzlich",
    "überraschung",
    "überraschend" "unerwartet",
    "abrupt",
    "unangemeldet",
    "ungeplant",
    "ungestüm",
    "rasch",
    "impulsiv",
    "nicht vereinbart",
    "überrumpeln",
    "augenblicklich",
    "unmittelbar",
    "unangekündigt",
    "ohne vorwarnung",
    "nicht vorstellbar",
    "nicht vorhersehbar",
    "unvorhergesehen",
    "eilig",
    "ausfallen",
    "unvermutet",
    "erstaunlich",
    "schnell",
]
for i in getTriples(
    "[RI XIII] H. 8 n. 328",
    "Kaiser Friedrich lädt im Streit zwischen Wetzlar und Johann von Seelbach aufgrund eines Urteils des Kammergerichts beide Parteien zu rechtlicher Verantwortung vor sich und gebietet den Wetzlarern, bei dieser Gelegenheit ihre Privilegien vorzulegen.",
    "processedRI_13Hefte.csv",
):
    print(i)
