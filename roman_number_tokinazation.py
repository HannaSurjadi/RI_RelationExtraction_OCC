from spacy.symbols import ORTH
import spacy


def tokenize_roman_numbers():
    # Add special case rule
    RomanNumbers = {
        "I.": [{ORTH: "I."}],
        "(I.)": [{ORTH: "(I.)"}],
        "II.": [{ORTH: "II."}],
        "(II.)": [{ORTH: "(II.)"}],
        "III.": [{ORTH: "III."}],
        "(III.)": [{ORTH: "(III.)"}],
        "IV.": [{ORTH: "IV."}],
        "(IV.)": [{ORTH: "(IV.)"}],
        "V.": [{ORTH: "V."}],
        "(V.)": [{ORTH: "(V.)"}],
        "VI.": [{ORTH: "VI."}],
        "(VI.)": [{ORTH: "(VI.)"}],
        "VII.": [{ORTH: "VII."}],
        "(VII.)": [{ORTH: "(VII.)"}],
        "VIII.": [{ORTH: "VIII."}],
        "IX.": [{ORTH: "IX."}],
        "(IX.)": [{ORTH: "(IX.)"}],
        "X.": [{ORTH: "X."}],
        "XI.": [{ORTH: "XI."}],
        "(XI.)": [{ORTH: "(XI.)"}],
        "XII.": [{ORTH: "XII."}],
        "(XII.)": [{ORTH: "(XII.)"}],
        "XIII.": [{ORTH: "XIII."}],
        "(XIII.)": [{ORTH: "(XIII.)"}],
        "XIV.": [{ORTH: "XIV."}],
        "(XIV.)": [{ORTH: "(XIV.)"}],
        "XV.": [{ORTH: "XV."}],
        "(XV.)": [{ORTH: "(XV.)"}],
        "XVI.": [{ORTH: "XVI."}],
        "(XVI.)": [{ORTH: "(XVI.)"}],
        "XVII.": [{ORTH: "XVII."}],
        "(XVII.)": [{ORTH: "(XVII.)"}],
        "XVIII.": [{ORTH: "XVIII."}],
        "XIX.": [{ORTH: "XIX."}],
        "(XIX.)": [{ORTH: "(XIX.)"}],
        "XX.": [{ORTH: "XX."}],
        "(XX.)": [{ORTH: "(XX.)"}],
        "XXI.": [{ORTH: "XXI."}],
        "(XXI.)": [{ORTH: "(XXI.)"}],
        "XXII.": [{ORTH: "XXII."}],
        "(XXII.)": [{ORTH: "(XXII.)"}],
        "XXIII.": [{ORTH: "XXIII."}],
        "(XXIII.)": [{ORTH: "(XXIII.)"}],
        "XXIV.": [{ORTH: "XXIV."}],
        "(XXIV.)": [{ORTH: "(XXIV.)"}],
        "XXV.": [{ORTH: "XXV."}],
        "(XXV.)": [{ORTH: "(XXV.)"}],
        "XXVI.": [{ORTH: "XXVI."}],
        "(XXVI.)": [{ORTH: "(XXVI.)"}],
        "XXVII.": [{ORTH: "XXVII."}],
        "(XXVII.)": [{ORTH: "(XXVII.)"}],
        "XXVIII.": [{ORTH: "XXVIII."}],
        "XXIX.": [{ORTH: "XXIX."}],
        "(XXIX.)": [{ORTH: "(XXIX.)"}],
        "XXX.": [{ORTH: "XXX."}],
        "(XXX.)": [{ORTH: "(XXX.)"}],
        "d. Ä.": [{ORTH: "d. Ä."}],
        "d.Ä.": [{ORTH: "d.Ä."}],
        "(d.Ä.)": [{ORTH: "(d.Ä.)"}],
        "(d. Ä.)": [{ORTH: "(d. Ä.)"}],
        "d.J.": [{ORTH: "d.J."}],
        "d. J.": [{ORTH: "d. J."}],
        "(d.J.)": [{ORTH: "(d.J.)"}],
        "(d. J.)": [{ORTH: "(d. J.)"}],
    }
    return RomanNumbers