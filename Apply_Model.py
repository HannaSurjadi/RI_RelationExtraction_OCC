import csv
import os
from rdflib import Graph, Literal, RDF, URIRef, BNode, RDFS
from rdflib.namespace import FOAF , XSD, Namespace, DCTERMS
from Emotion_Analysis import (
    getTriples,
    getVariablesFromSubject,
    getVariablesFromObject,
    ApplyEmotionModelRules,
    getTextFromNumber,
)

g = Graph()

RI = Namespace("http://www.regesta-imperii.de/hypotheticalOntology/")
OCC = Namespace("http://sbmi.uth.tmc.edu/ontology/VEO#")
g.bind("ri", RI)
g.bind("occ", OCC)
relevantEmotions = {'admiration': 0, 'reproach' : 0, 'anger' : 0, 'gratitude' : 0, 'happy-for' : 0, 'sorry-for' : 0, 'gloating' : 0, 'pity' : 0}
with open("finalInput.csv", 'r') as rf:
    reader = csv.reader(rf, delimiter='\t')
    for row in reader:
        try:
            RegestURI = URIRef(row[5])
            Date = row[2]
            Date = Literal(Date, datatype=XSD.date)
            Triples = getTriples(row[0], row[4], "finalInput.csv")
            for triple in Triples:
                Svariables = getVariablesFromSubject(triple)
                Ovariables = getVariablesFromObject(triple, Svariables)
                if not Svariables or not Ovariables:
                    pass
                else:
                    Semotions = ApplyEmotionModelRules(Svariables)
                    Oemotions = ApplyEmotionModelRules(Ovariables)
                    for em in Semotions:
                        if em in relevantEmotions.keys():
                            relevantEmotions[em] = relevantEmotions[em] + 1
                            bn = BNode()
                            S = RI[triple['Subject']['RI_ID']]
                            O = RI[triple['AgentObject']['RI_ID']]
                            emotion = OCC[em]
                            g.add((S, RI.feels, bn))
                            g.add((bn, RI.towards, O))
                            g.add((bn, RDFS.isDefinedBy, RegestURI))
                            g.add((RegestURI, DCTERMS.date, Date))
                            g.add((bn, RDFS.subPropertyOf, emotion))
                    for em in Oemotions:
                        if em in relevantEmotions.keys():
                            relevantEmotions[em] = relevantEmotions[em] + 1
                            bn = BNode(em + relevantEmotions[em])
                            S = RI[triple['Subject']['RI_ID']]
                            O = RI[triple['AgentObject']['RI_ID']]
                            emotion = OCC[em]
                            g.add((O, RI.feels, bn))
                            g.add((bn, RI.towards, S))
                            g.add((bn, RDFS.isDefinedBy, RegestURI))
                            g.add((RegestURI, DCTERMS.date, Date))
                            g.add((bn, RDFS.subPropertyOf, emotion))
        except (TypeError, ConnectionError):
            pass

with open("finalOutput.ttl", 'w') as wf:
    wf.write(g.serialize(format='ttl'))
with open("finalOutput.json", 'w') as wf:
    wf.write(g.serialize(format='json-ld', indent=4))
