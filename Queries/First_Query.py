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


FirstQuery_One = """
SELECT ?year (Count(?posE) as ?posEmCount)
WHERE {
    ri:F00001419 ri:feels ?posE .
    ?posE rdfs:isDefinedBy ?uri .
    ?uri ns1:date ?date .
    {?posE rdfs:subPropertyOf occ:admiration }
    UNION
    {?posE rdfs:subPropertyOf occ:gratitude }
    UNION
    {?posE rdfs:subPropertyOf occ:happy-for }
    UNION
    {?posE rdfs:subPropertyOf occ:sorry-for }
BIND(YEAR(?date) as ?year)
}
GROUP BY ?year
"""

FirstQuery_Two = """
SELECT ?year (Count(?negE) as ?negEmCount)
WHERE {
    ri:F00001419 ri:feels ?negE .
    ?negE rdfs:isDefinedBy ?uri .
    ?uri ns1:date ?date .
    {?negE rdfs:subPropertyOf occ:reproach }
    UNION
    {?negE  rdfs:subPropertyOf occ:anger }
    UNION
    {?negE  rdfs:subPropertyOf occ:gloating }
    UNION
    {?negE  rdfs:subPropertyOf occ:pity }
BIND(YEAR(?date) as ?year)
}
GROUP BY ?year
"""
qres = g.query(FirstQuery_One, initNs = { "ri": RI, "occ": OCC , "ns1": DCTERMS})
data = {}
for row in qres:
    data[str(row.year)] = str(row.posEmCount)
qres = g.query(FirstQuery_Two, initNs = { "ri": RI, "occ": OCC , "ns1": DCTERMS})
for row in qres:
    data[str(row.year)] = str(int(data[str(row.year)]) - int(row.negEmCount))
xList = []
yList = []
for item in data.items():
    xList.append(int(item[0]))
    yList.append(int(item[1]))
plt.xlabel("Jahreszahl")
plt.ylabel("Summe positiver & negativer Aktionen")
plt.plot(xList,yList)
plt.show()

SecondQuery ="""
SELECT ?month COUNT(?agent)as ?agentCount
WHERE {
    ri:F00001419 ri:feels ?negE .
    ?negE ri:toward ?Agent .
    ?negE rdfs:isDefinedBy ?uri .
    ?negE rdfs:subPropertyOf ?emotion .
    ?uri ns1:date ?date
BIND(YEAR(?date) as ?year)
FILTER(?year > '1450' && ?year < '1454')
}
GROUP BY ?agentCount
"""
