import rdflib
from rdflib import Graph, Literal, RDF, URIRef, BNode, RDFS
from rdflib.namespace import FOAF , XSD, Namespace, DCTERMS
import matplotlib.pyplot as plt

g = rdflib.Graph()
g.parse("finalOutput_WithLabel.json")
RI = Namespace("http://www.regesta-imperii.de/hypotheticalOntology/")
OCC = Namespace("http://sbmi.uth.tmc.edu/ontology/VEO#")
g.bind("ri", RI)
g.bind("occ", OCC)

positiveEmotions = ['admiration', 'gratitude', 'happy-for', 'sorry-for']
negativeEmotions = ['reproach', 'anger', 'gloating', 'pity']

## Magdeburger Türkensteuer
SecondQuery_One_III ="""
SELECT ?agentTwo (count(?agentTwo)as ?agentCount)
WHERE {
    ?agentOne ri:feels ?e .
    ?e ri:towards ?agentTwo .
    ?e rdfs:isDefinedBy ?uri .
    ?uri ns1:date ?date
BIND(YEAR(?date) as ?year)
FILTER(?year > 1474 && ?year < 1484)
}
GROUP BY ?agentTwo ?agentCount
ORDER BY Desc(?agentCount)
LIMIT 10
"""


qres = g.query(SecondQuery_One_III, initNs = { "ri": RI, "occ": OCC , "ns1": DCTERMS})
data = {}
for row in qres:
    data[str(row.agentTwo).split('/')[-1]] = str(row.agentCount)
for item in data.items():
    print(item)


AgentDic = {}
for key in data.keys():
    dict = {}
    SecondQuery_Two_A_III = """
    SELECT (YEAR(?date) as ?year) ?month (count(?e)as ?emCount)
    WHERE {
        {ri:F00001419 ri:feels ?e .
        ?e ri:towards ri:"""+key+""" .
        ?e rdfs:isDefinedBy ?uri .
        ?uri ns1:date ?date }
        UNION
        {ri:"""+key+""" ri:feels ?e .
        ?e ri:towards ri:F00001419.
        ?e rdfs:isDefinedBy ?uri .
        ?uri ns1:date ?date }
        {?e rdfs:subPropertyOf occ:admiration }
        UNION
        {?e rdfs:subPropertyOf occ:gratitude }
        UNION
        {?e rdfs:subPropertyOf occ:happy-for }
        UNION
        {?e rdfs:subPropertyOf occ:sorry-for }
    BIND(MONTH(?date) as ?month)
    FILTER(YEAR(?date) > 1474 && YEAR(?date) < 1484)
    }
    GROUP BY ?year ?month
    ORDER BY ?year ?month
    """
    qres = g.query(SecondQuery_Two_A_III, initNs = { "ri": RI, "occ": OCC , "ns1": DCTERMS})
    for row in qres:
        print(row)
        dict[str(row.year)+'_'+ str(row.month)] = str(row.emCount)
    SecondQuery_Two_B_III = """
    SELECT (YEAR(?date) as ?year) ?month (count(?e)as ?emCount)
    WHERE {
        {ri:F00001419 ri:feels ?e .
        ?e ri:towards ri:"""+key+""" .
        ?e rdfs:isDefinedBy ?uri .
        ?uri ns1:date ?date }
        UNION
        {ri:"""+key+""" ri:feels ?e .
        ?e ri:towards ri:F00001419.
        ?e rdfs:isDefinedBy ?uri .
        ?uri ns1:date ?date }
        {?e rdfs:subPropertyOf occ:reproach }
        UNION
        {?e  rdfs:subPropertyOf occ:anger }
        UNION
        {?e  rdfs:subPropertyOf occ:gloating }
        UNION
        {?e  rdfs:subPropertyOf occ:pity }
    BIND(MONTH(?date) as ?month)
    FILTER(YEAR(?date) > 1474 && YEAR(?date) < 1484)
    }
    GROUP BY ?year ?month
    ORDER BY ?year ?month
    """
    qres = g.query(SecondQuery_Two_B_III, initNs = { "ri": RI, "occ": OCC , "ns1": DCTERMS})
    for row in qres:
        print('EMOTION COUNT'+ row.emCount)
        try:
            dict[str(row.year)+'/'+ str(row.month)] = float(dict[str(row.year)+'/'+ str(row.month)]) - float(row.emCount)
        except KeyError:
            dict[str(row.year)+'/'+ str(row.month)] = float(row.emCount)
    AgentDic[key] = dict
Years = [1475,1476, 1477, 1478,1479, 1480, 1481, 1482, 1483]
Months = []
for y in Years:
    for month in (1,12):
        Months.append(str(y)+'_'+str(month))
monthsShort = []
for i in Months:
    monthsShort.append(i[2:])
f = plt.figure()
f.set_figwidth(4)
f.set_figheight(1)
for key in AgentDic.keys():
    label = key
    yList = []
    for month in Months:
        if month in list(AgentDic[key].keys()):
            print(AgentDic[key][month])
            yList.append(AgentDic[key][month])
        else:
            yList.append(0)
    plt.plot(monthsShort,yList, label = label)
plt.legend(title="RI ID", loc="right")
plt.xlabel("Jahr_Monat")
plt.ylabel("Summe positiver & negativer Aktionen an ID")
plt.show()
