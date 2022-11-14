import spacy
import csv
import random
import regex as re
from Subject_Objekt_Entity_Allignment import getRI_ID
from RI_specificTokenizingRules import rules
from agentFondness import makeAgentFondness, getAgentFondness



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
    with open("new_valence.csv", "r") as rf:
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
                    return [row[4], BezugsRegest]
                else:
                    number = BezugsRegest
                    m = re.search("n. [0-9]+", number)
                    Regest = m.group(0).replace("n. ", "")
                    Regest = int(Regest)
                    BezugsRegest = Regest - 1
                    BezugsRegest = number.replace(str(Regest), str(BezugsRegest))



def get_Action_Dic(number, token):
    ValenceDic = get_valence_Dic()
    ActionDic = {
        "Text": token.text,
        "pos": token.pos_,
        "form": token.morph.to_dict(),
        "subtree":token.subtree,
        "negation": False
    }
    if token.text in ValenceDic.keys():
        ActionDic["valence"] = ValenceDic[token.text]
    for child in token.children:
        if child.dep_ == "ng":
            ActionDic["negation"] = True
    return ActionDic


def getObjektOrSubjektDic(token, s, number, ValenceDic):
    Dic = {
        "Text": token.text,
        "pos": token.pos_,
        "form": token.morph.to_dict(),
        "RI_ID": getRI_ID(number, token),
    }
    try:
        if token.text == "Kaiser":
            Dic["RI_ID"] = "F00001419"
        elif token.text == "Friedrich" and s[token.i - 1].text == "Kaiser":
            Dic["RI_ID"] = "F00001419"
    except IndexError:
        pass
    if token.pos_ != 'PROPN':
        for i in token.children:
            SubValence = 0
            if i.text in ValenceDic.keys() and (s[i.i -1] == token or s[i.i +1] == token) and token.pos_ != 'PROPN':
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
                                ActionDic = get_Action_Dic(number, token)
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
    global unexp_list
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
    alternativeRegest = False
    SubjectDic = False
    ObjectDic = False
    ActionDic = False
    global ValenceDic
    ValenceDic = get_valence_Dic()
    nlp = spacy.load("de_core_news_lg")
    if "desgleichen" in text or "Desgleichen" in text:
        alternativeRegest = desgleichenTripleChange(number, file)
    # Apply special Tokanization Rules conserning Roman Numbers
    specialCases = rules()
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
        if len(alternativeRegest) != 0:
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
            for t in getTriplesProceedingFromSubject(s, number, ValenceDic):
                triples.append(t)
            for t in getTriplesProceedingFromObjectsGEGEN(s, number, ValenceDic):
                triples.append(t)
            for t in getTriplesProceedingFromObjectsZWISCHEN(s, number, ValenceDic):
                triples.append(t)
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
            unexp = False
            try:
                if s[token.i-1].text in unexp_list or s[token.i+1].text in unexp_list:
                    unexp = True
            except IndexError:
                pass
            # Defines the Action trough the found verb
            ActionDic = get_Action_Dic(number, token)
            # Goes through all direct children of the verb and finds subjects
            for child1 in token.children:
                if child1.dep_ == 'sb':
                    # Defines the SubjectDic through the found subject
                    SubjectDic = getObjektOrSubjektDic(child1, s, number, ValenceDic)
                    # goes through the direct children of the verb again and finds objects
                    for child2 in token.children:
                        if child2.dep_ == 'oa' or child2.dep_ == 'da':
                            for i in getTriplesProceedingFromSubjectSUB(child2, number, SubjectDic, ActionDic, s, unexp):
                                triples.append(i)
                        if child2.pos_ == 'VERB':
                            try:
                                valence = ValenceDic[child2.text]
                            except KeyError:
                                valence = 0
                            ActionDic['Text'] = ActionDic['Text'] + ' ' + child2.text
                            try:
                                ActionDic['valence'] = (float(ActionDic['valence']) + float(valence))
                            except KeyError:
                                pass
                            for child3 in child2.children:
                                if child3.dep_ == 'oa' or child3.dep_ == 'da':
                                    for i in getTriplesProceedingFromSubjectSUB(child3, number, SubjectDic, ActionDic, s, unexp):
                                        triples.append(i)
    return triples


def getTriplesProceedingFromSubjectSUB(child, number, SubjectDic, ActionDic, s, unexp):
     # creates or emties the triple Dicitonary so that no Object is adopted
     triples = []
     AgentObjectDic = None
     ObjectDic = None
     # from a former triple
     triple = {}
     # Defines the object as AgentObject
     AgentObjectDic = getObjektOrSubjektDic(child, s, number, ValenceDic)
     ActionWords = ActionDic['Text'].split(' ')
     for act in ActionWords:
         for t in s:
             if t.text == act:
                 for potOb in t.children:
                     if potOb.pos_ == 'NOUN' and potOb.dep_ in ['oa', 'oc', 'og', 'op', 'da'] and not getRI_ID(number, potOb) and not potOb.dep_ == 'sb':
                         ObjectDic = getObjektOrSubjektDic(potOb, s, number, ValenceDic)
                     elif potOb.pos_ == 'VERB':
                         for potOb2 in potOb.children:
                             if potOb2.pos_ == 'NOUN' and potOb2.dep_ in ['oa', 'oc', 'og', 'op', 'da'] and not getRI_ID(number, potOb2) and not potOb2.dep_ == 'sb':
                                 ObjectDic = getObjektOrSubjektDic(potOb2, s, number, ValenceDic)
     # appends triple to the triples list only if Subject and AgentObject
     # have RI_IDs and if Subject and AgentObject are not the same
     # if the a child has no RI-ID and it is found in the ValenceDictionary it is set as ObjectDic
     # In case there is a conjunction in the subtree of the AgentObject an other triple with the same Subjet and Object is added.
     triple = {'number': number}
     AgentObjectDic = getObjektOrSubjektDic(child, s, number, ValenceDic)
     print(child.text)
     print(child.head.text)
     if child.head.text == 'gegen':
         AgentObjectDic['Text'] = 'XgegenX ' + AgentObjectDic['Text']
     triple['Subject'] = SubjectDic
     triple['Action'] = ActionDic
     triple['Object'] = ObjectDic
     triple['AgentObject'] = AgentObjectDic
     triple['variables'] = {'unexp': unexp}
     if triple['Subject']['RI_ID'] and triple['AgentObject']['RI_ID'] and triple['Subject']['RI_ID']!= triple['AgentObject']['RI_ID']:
         if triple not in triples:
             triples.append(triple)
     headGegen = False
     for sub in child.subtree:
         if sub.dep_ == 'oa' or sub.dep_ == 'da' or sub.dep_ == 'nk' or sub.dep_ == 'ag' or sub.dep_ == 'oc' or sub.dep_ == 'og'  or sub.dep_ == 'nk' or sub.dep_ == 'cj':
             triple = {'number': number}
             if 'XgegenX' in AgentObjectDic['Text']:
                 headGegen = True
             AgentObjectDic = getObjektOrSubjektDic(sub, s, number, ValenceDic)
             if sub.head.text == 'gegen' or headGegen == True:
                 AgentObjectDic['Text'] = 'XgegenX ' + AgentObjectDic['Text']
             triple['Subject'] = SubjectDic
             triple['Action'] = ActionDic
             triple['Object'] = ObjectDic
             triple['AgentObject'] = AgentObjectDic
             triple['variables'] = {'unexp': unexp}
             if triple['Subject']['RI_ID'] and triple['AgentObject']['RI_ID'] and triple['Subject']['RI_ID']!= triple['AgentObject']['RI_ID']:
                 if triple not in triples:
                     triples.append(triple)
     return triples


def assembleTriples(triples):
    newTriples = []
    for t1 in triples:
        for t2 in triples:
            if not (isinstance(t1, list) or isinstance(t2, list)):
                if t1['Subject']['RI_ID'] == t2['Subject']['RI_ID'] and t1['Action'] == t2['Action'] and t1['Object'] == t2['Object'] and t1['AgentObject']['RI_ID'] == t2['AgentObject']['RI_ID']:
                    if t2['AgentObject']['Text'] not in t1['AgentObject']['Text']:
                        triples.remove(t2)
    newTriples.extend(triples)
    return newTriples


# Finds [Ereignis]-gegen und zwischen[Ereignis]&[Ereignis] patterns.
def getTriplesProceedingFromObjectsGEGEN(s, number, ValenceDic):
    Otriples = []
    triple = {}
    triple["number"] = number
    SubjectList = []
    ObjectList = []
    ActionDic = None
    for token in s:
        try:
            if token.text == 'gegen' and s[token.i-1].pos_ == 'NOUN':
                if not ActionDic:
                    ActionDic = get_Action_Dic(number, s[token.i-1])
                try:
                    valence = ValenceDic[s[token.i-1].text]
                except KeyError:
                    pass
                unexp = False
                for potObj in token.subtree:
                    if getRI_ID(number,potObj) and potObj not in ObjectList:
                        ObjectList.append(potObj)
                if s[token.i-1].text in unexp_list or s[token.i+2].text in unexp_list:
                    unexp = True
                for sub in s[token.i-1].children:
                    if (sub.pos_ == 'PROPN' or sub.pos_ == 'NOUN') and sub not in SubjectList:
                        SubjectList.append(sub)
                    else:
                        for potSub in sub.subtree:
                            if sub.dep_ == "da" and (sub.pos_ == 'PROPN' or sub.pos_ == 'NOUN') and sub not in SubjectList:
                                SubjectList.append(sub)
                        for anc in s[token.i-1].ancestors:
                            for sub in anc.children:
                                if (sub.pos_ == 'PROPN' or sub.pos_ == 'NOUN')and sub not in SubjectList:
                                    for potSub in sub.subtree:
                                        if getRI_ID(number,potSub):
                                            SubjectList.append(potSub)
                                else:
                                    for potSub in sub.subtree:
                                        if getRI_ID(number,potSub) and (sub.pos_ == 'PROPN' or sub.pos_ == 'NOUN')and sub not in SubjectList:
                                            SubjectList.append(potSub)
        except IndexError:
            pass
    for Object in ObjectList:
        while Object in SubjectList:
            SubjectList.remove(Object)
    for Object in ObjectList:
        for Subject in SubjectList:
            triple['Subject'] = getObjektOrSubjektDic(Subject, s, number, ValenceDic)
            triple['Action'] = ActionDic
            triple['Object'] = None
            triple['AgentObject'] = getObjektOrSubjektDic(Object, s, number, ValenceDic)
            triple['variables'] = {'unexp': unexp}
            if triple not in Otriples and triple['Subject']['RI_ID'] != triple['AgentObject']['RI_ID']:
                Otriples.append(dict(triple))
    return Otriples


def getTriplesProceedingFromObjectsZWISCHEN(s, number, ValenceDic):
    Otriples = []
    triple = {}
    triple["number"] = number
    SubjectList = []
    ObjectList = []
    ActionDic = None
    List = []
    for token in s:
        try:
            if token.text == 'zwischen':
                try:
                    valence = ValenceDic[s[token.i-1].text]
                except KeyError:
                    pass
                if not ActionDic:
                    ActionDic = get_Action_Dic(number, s[token.i-1])
                unexp = False
                if s[token.i-1].text in unexp_list or s[token.i+2].text in unexp_list:
                    unexp = True
                for potEnt in token.subtree:
                    ID = getRI_ID(number, potEnt)
                    if ID:
                        List.append(potEnt)
                for ent1 in List:
                    for ent2 in List:
                        if not getRI_ID(number, ent1) == getRI_ID(number, ent2):
                            triple['Subject'] = getObjektOrSubjektDic(ent1, s, number, ValenceDic)
                            triple['Action'] = ActionDic
                            triple['Object'] = None
                            triple['AgentObject'] = getObjektOrSubjektDic(ent2, s, number, ValenceDic)
                            if triple not in Otriples and triple['Subject']['RI_ID'] != triple['AgentObject']['RI_ID']:
                                Otriples.append(dict(triple))
        except IndexError:
            pass
    return Otriples



def getVariablesFromSubject(triple):
    # Setting variables
    # [distress,sorry_for,resentment,gloating,hope,fear,satisfaction,fear_confirmed,relief,dissapointment,pride,shame,admiration,reproach,love,hate,joy,gratification,remorse,gratitude,anger,shock,surprise]
    sub = triple["Subject"]
    act = triple["Action"]
    try:
        obj = triple["Object"]
    except KeyError:
        pass
    Aobj = triple["AgentObject"]
    try:
        sub_val = float(sub["valence"])
    except KeyError:
        sub_val = 0
    try:
        act_val = float(act["valence"])
    except KeyError:
        act_val = 0
    try:
        act_val = act_val + float(obj["valence"])
    except (KeyError, TypeError):
        pass
    try:
        Aobj_val = float(Aobj["valence"])
    except KeyError:
        Aobj_val = 0
    if obj and 'XgegenX' in Aobj['Text']:
        if act_val < 0 and float(obj["valence"]) < 0:
            act_val = abs(act_val)
        elif act_val > 0 and float(obj["valence"]) < 0:
            act_val = float(act["valence"]) + abs(float(obj["valence"]))
    for t in act.values():
        if t == "PRON" or t == "PRF" or t == "PPOSS" or t == "PPOSS":
            de = "self"
        else:
            de = "other"
    if act_val > 0.5 and de == 'other':
        sa = "praiseworthy"
    elif act_val < -0.5 and de == 'other':
        sa = "blameworthy"
    else:
        sa = "neutral"
    try:
        op = float(triple['Object']['valence'])
    except (KeyError, TypeError):
        op = float(triple['Action']['valence'])
    if op > 0:
        op = 'desirable'
    elif op < 0:
        op = 'undesirable'
    else:
        op = 'neutral'
    if Aobj_val + act_val < 0:
        sr = "displeased"
        sp = "undesirable"
    elif Aobj_val + act_val > 0:
        sr = "pleased"
        sp = "desirable"
    else:
        sr = "neutral"
        sp = "neutral"
    if Aobj_val > 0:
        of = "liked"
    elif Aobj_val < 0:
        of = "not liked"
    else:
        of = "neutral"
    if sub['RI_ID'] == "F00001419":
        sp = 'desirable'
    for i in conf_list:
        if i in act.values():
            stat = "confirmed"
    con_pos = []
    adv_List = []
    if triple['Action']['pos'] == 'NOUN':
        stat = 'confirmed'
    elif triple['Action']['form']['Tense'] == 'Past':
        stat = 'confirmed'
    elif triple['Action']['form']['Tense'] == 'Pres':
        stat = 'unconfirmed'
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
    try:
        if triple['variables']['unexp']:
            unexp = True
        else:
            unexp = False
    except KeyError:
        unexp = False
    if Aobj_val < 0.5 and Aobj_val > -0.5:
        makeAgentFondness(triple)
        af = 'neutral'
        if act_val > 0:
            af = 'liked'
        else:
            af = 'not liked'
    else:
        if Aobj_val < -0.5:
            af = 'not liked'
        elif Aobj_val > 0.5:
            af = 'liked'
        else:
            af = getAgentFondness(triple)
            if af == None:
                makeAgentFondness(triple)
                af = makeAgentFondness(triple)
    variableDic = {
        "af": af,
        "sa": sa,
        "de": de,
        "sr": sr,
        "sp": sp,
        "op": op,
        "stat": stat,
        "unexp": unexp,
    }
    return variableDic


def getVariablesFromObject(triple, SubvariableDic):
    # Setting variables
    # [distress,sorry_for,resentment,gloating,hope,fear,satisfaction,fear_confirmed,relief,dissapointment,pride,shame,admiration,reproach,love,hate,joy,gratification,remorse,gratitude,anger,shock,surprise]
    sub = triple["AgentObject"]
    act = triple["Action"]
    try:
        obj = triple["Object"]
    except KeyError:
        pass
    Aobj = triple["Subject"]
    try:
        act_val = float(act["valence"])
    except KeyError:
        act_val = 0
    try:
        act_val = act_val + float(obj["valence"])
    except (KeyError, TypeError):
        pass
    try:
        sub_val = float(sub["valence"])
    except KeyError:
        sub_val = 0
    if SubvariableDic['de'] == 'self':
        de = 'other'
    else:
        de = 'self'
    try:
        sr = float(triple['Action']['valence']) + float(triple['AgentObject']['valence'])
        op = float(triple['Object']['valence'])
    except (KeyError, TypeError):
        sr = float(triple['Action']['valence'])
        op = float(triple['Action']['valence'])
    if op > 0:
        op = 'desirable'
    elif op < 0:
        op = 'undesirable'
    else:
        op = 'neutral'
    if sr > 0:
        sr = 'pleased'
        sp = 'desirable'
    else:
        sr = 'displeased'
        sp = 'undesirable'
    try:
        Aobj_val = float(Aobj["valence"])
    except KeyError:
        Aobj_val = False
    if obj and 'XgegenX' in Aobj['Text']:
        if act_val < 0 and float(obj["valence"]) < 0:
            act_val = abs(act_val)
        elif act_val > 0 and float(obj["valence"]) < 0:
            act_val = -abs(float(act["valence"])) + (float(obj["valence"]))
    if not Aobj_val:
        Aobj_val = 0
    if Aobj_val < 0.5 and Aobj_val > -0.5:
        makeAgentFondness(triple)
        if act_val > 0:
            af = 'liked'
        else:
            af = 'not liked'
    else:
        if Aobj_val < -0.5:
            af = 'not liked'
        elif Aobj_val > 0.5:
            af = 'liked'
        else:
            af = getAgentFondness(triple)
            if af == None and act_val < 0:
                makeAgentFondness(triple)
                af = 'neutral'
    if sub['RI_ID'] == "F00001419":
        sp = 'desirable'
    if act_val > 0.5 and de == 'other':
        sa = "praiseworthy"
    elif act_val < -0.5 and de == 'other':
        sa = "blameworthy"
    else:
        sa = "neutral"
    variableDic = {
        "af": af,
        "sa": sa,
        "de": de,
        "sr": sr,
        "sp": sp,
        "op": op,
        "stat": SubvariableDic['stat'],
        "unexp": SubvariableDic['unexp'],
    }
    return variableDic


def ApplyEmotionModelRules(variableDic):
    emotion_List = []
    if variableDic["sr"] == "displeased" and variableDic["de"] == "self":
        emotion_List.append("distress")
    elif variableDic["sr"] == "displeased" and variableDic["de"] == "other" and variableDic["af"] == "liked":
        emotion_List.append("sorry_for")
    elif (
        variableDic["sr"] == "displeased"
        and variableDic["sp"] == "desirable"
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
    elif variableDic["sr"] == "pleased":
        emotion_List.append("joy")
    if "joy" in emotion_List and variableDic["unexp"]:
        emotion_List.append("suprise")
    elif "distress" in emotion_List and variableDic["unexp"]:
        emotion_List.append("shock")
    return emotion_List


def ApplyComplexEmotionModelRules(Subject_emotion_List, Object_emotion_List):
    # rules for complex emotion
    Subject_complex_List = []
    Object_complex_List = []
    if "joy" in Subject_emotion_List and "pride" in Subject_emotion_List:
        Subject_complex_List.append("gratification")
    elif "joy" in Subject_emotion_List and "pride" in Subject_emotion_List:
        Object_complex_List.append("gratification")
    elif "distress" in Subject_emotion_List and "shame" in Subject_emotion_List:
        Subject_emotion_List.append("remorse")
    elif "distress" in Object_emotion_List and "shame" in Object_emotion_List:
        Object_emotion_List.append("remorse")
    elif "joy" in Subject_emotion_List and "admiration" in Object_emotion_List:
        Subject_emotion_List.append("gratitude")
    elif "joy" in Object_emotion_List and "admiration" in Subject_emotion_List:
        Object_emotion_List.append("gratitude")
    elif "distress" in Subject_emotion_List and "reproach" in Object_emotion_List:
        Subject_emotion_List.append("anger")
    elif "distress" in Object_emotion_List and "reproach" in Subject_emotion_List:
        Object_emotion_List.append("anger")
    return [Subject_emotion_List, Object_emotion_List]


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

for i in getTriples(
  "[RI XIII] H. 7 n. 512",
  "Kaiser Friedrich teilt Bischof Heinrich von Münster, den Herzöge Johann von Kleve und Wilhelm von Jülich-Berg sowie Bürgermeistern und Rat der Stadt Köln und allen Reichsuntertanen mit, daß ausweislich vorgelegter Urkunden der Kölner Bürger Tilmann Schreinmacher von Attendorn vor Doktor Benedikt von Werlis als Kommissar des Kölner Offizials ein Urteil gegen den Münsteraner Bürger Bernhard Pape erwirkt habe und über diesen der geistliche Bann verhängt worden sei. Obwohl diese Sentenzen später von Dorktor Engelbert von Daun, Dechant zu Sankt Georg in Köln, als dem Subdelegierten des päpstlichen Kommissars Dr. Dietmar Berswort, Dechant an Sankt Kunibert in Köln, bestätigt worden seien, habe Pape sie mißachtet und sei das dem Kläger gehörige Geld schuldig geblieben. Da schließlich auch Bürgermeister und Rat der Stadt Münster Kaiser Friedrich's Befehl mißachteten, ihren Mitbürger zur Befolgung des Urteils und zur Rückzahlung seiner Schulden anzuhalten, gebietet er ihnen bei Strafe seiner Ungnade und einer je zur Hälfte an die kaiserlich Kammer und die Geschädigten fallenden Strafe von 30 Mark Gold, die Bürger, Einwohner und zugewanndten der Stadt Münster und ihre Güter allenthalben solange zu arrestieren, bis sie seinem Befehl gehorchen und der Kläger befriedigt ist.",
  "processedRI_13Hefte.csv",
):
    print(i)
    SVariables = getVariablesFromSubject(i)
    print('from Subject: ' + str(SVariables))
    SubjectPrimaryEmotions = ApplyEmotionModelRules(SVariables)
    OVariables = getVariablesFromObject(i, SVariables)
    print(' from Object: ' + str(OVariables))
    ObjectPrimaryEmotions = ApplyEmotionModelRules(OVariables)
    print(ApplyComplexEmotionModelRules(SubjectPrimaryEmotions, ObjectPrimaryEmotions))
