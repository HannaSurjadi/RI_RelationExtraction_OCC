# Relation Extraction OCC RI


## URIGrabber.py 
A helpful little snippet of code that takes the number of a Regest in either of the two forms #X-XXX or [XX] (Suppl) H. X n. X and returns the corresponding URI.

## RIspecificTokenitingRules.py
Contains the function tokenize_roman_numbers that specifies tokenizing Rules for roman numbers is personal titles such as "Friedrich III." and for Abrrvations such as 'd.J.' in different variations.

## preprocessing.py

Contains a primary and secondary preprocessing function. This preprocessing is customized for the RI-[XIII] volume and should be revisited before beeing applied to other ressources. 

## getEntDicFromXML.py

This is a function that takes the XML-indexes of the Regesta Imperii as an input which can be found at https://gitlab.rlp.net/adwmainz/regesta-imperii/lab/regesta-imperii-data/-/tree/main/data/indexes. The funktion returns pairs of Regestennummer-Entitätenliste-pairs.


