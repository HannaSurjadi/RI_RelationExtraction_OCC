# Relation Extraction OCC RI


## URIGrabber.py 
A helpful little snippet of code that takes the number of a Regest in either of the two forms #X-XXX or [XX] (Suppl) H. X n. X and returns the corresponding URI.

## RIspecificTokenitingRules.py
Contains the function tokenize_roman_numbers that specifies tokenizing Rules for roman numbers is personal titles such as "Friedrich III." and for Abrrvations such as 'd.J.' in different variations.

## preprocessing.py

Contains a primary and secondary preprocessing function. This preprocessing is customized for the RI-[XIII] volume and should be revisited before beeing applied to other ressources. 
