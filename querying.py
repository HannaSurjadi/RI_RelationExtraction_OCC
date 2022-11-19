import rdflib

filename

g = rdflib.Graph()

result = g.parse(filename, format "turle")

positivEmotions = ['admiration', 'gratitude', 'happy-for', 'sorry-for']
negativeEmotions = [ 'reproach', 'anger', 'gloating', 'pity']

beliebtheitQuery = """
SELECT ?halfDec count(distinct(?posEm))as ?posEmCount count(disctinct(?negEm)) as ?negEmCount
WHERE ?Agent ri:feels ?posEm
      ?posEm ri:towoards ri:F00001419.
      ?Agent ?negEm ri:F00001419.
      ?negEm ri:towoards ri:F00001419.
      ?posEm rdfs:isDefinedBy ?uri.
      ?negEm rdfs:isDefinedBy ?uri.
      ?uri dcterms.date ?date.
      {
      {?posEm rdfs:subPropertyOf occ:admiration.}
      UNION
      {?posEm rdfs:subPropertyOf occ:gratitude.}
      UNION
      {?posEm rdfs:subPropertyOf occ:happy-for.}
      UNION
      {?posEm rdfs:subPropertyOf occ:sorry-for.}
      UNION
      }
      {
      {?negEm rdfs:subPropertyOf occ:reproach.}
      UNION
      {?negEm rdfs:subPropertyOf occ:anger.}
      UNION
      {?negEm rdfs:subPropertyOf occ:gloating.}
      UNION
      {?negEm rdfs:subPropertyOf occ:pity.}
      UNION
      }
BIND(xsd:integer(YEAR(?date)/5) = ?halfDec)
GROUP BY ?halfDec
ORDER BY ?date
"""

HaeufigeBeziehungen ="""
SELECT ?Agent ?emotionscore ?year  ?emotioncount
WHERE ?Agent ri:feels ?posEm
      ?posEm ri:towoards ri:F00001419.
      ?Agent ?negEm ri:F00001419.
      ?negEm ri:towoards ri:F00001419.
      ?posEm rdfs:isDefinedBy ?uri.
      ?negEm rdfs:isDefinedBy ?uri.
      ?uri dcterms.date ?date.
      {
      {?posEm rdfs:subPropertyOf occ:admiration.}
      UNION
      {?posEm rdfs:subPropertyOf occ:gratitude.}
      UNION
      {?posEm rdfs:subPropertyOf occ:happy-for.}
      UNION
      {?posEm rdfs:subPropertyOf occ:sorry-for.}
      UNION
      }
      {
      {?negEm rdfs:subPropertyOf occ:reproach.}
      UNION
      {?negEm rdfs:subPropertyOf occ:anger.}
      UNION
      {?negEm rdfs:subPropertyOf occ:gloating.}
      UNION
      {?negEm rdfs:subPropertyOf occ:pity.}
      UNION
      }
BIND(YEAR(?date) as ?Year)
BIND(IF(?Agent ri:feels ?posEm.
    && ?posEm ri:towards ri:F00001419.
    && ?posEm rdfs:isDefinedBy ?uriONE.
    && ?uriONE dcterms.date ?year.
    && ?negEm ri:towards ri:F00001419.
    && ?negEm rdfs:isDefinedBy ?uriTWO.
    && ?uriONE dcterms.date ?year., COUNT(?posEm)-COUNT(?negEm) as ?emotionscore)
BIND (IF ?Agent re:feels ?posEm && ?Agent re:feels ?negEm, (COUNT(?posEm)-COUNT(?posEm)) as ?emotionscount)
GROUP BY ?Agent ?emotionscore ?year
ORDER BY ?emotioncount
"""
