import re
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from defines.material import material_kind


def Material(txt_eng, text_kor, desc):
    txt = "{0},{1}".format(txt_eng, text_kor)
    if re.findall(
        "unlimited edition|open edition|unnumbered limited edition|edition of unknown size|edition unknown",
        " {0},{1} ".format(txt, desc).lower(),
    ) and (not re.findall("unique", " {0},{1} ".format(txt, desc).lower())):
        result = "Decorative Art"
    elif re.findall(
        "ed.\s*\d|edition|editions|artist's proofs|hors commerce|trial proofs|printer's proofs|limited editioned. of|ed. of|\Wa\.?p\.?\W|\Wp\.?p\.?\W|\Wh\.?c\.?\W|\(\d+\/\d+\)",
        " {0},{1} ".format(txt, desc).lower(),
    ) and (not re.findall("unique", " {0},{1} ".format(txt, desc).lower())):
        result = "Edition"
    elif re.findall(
        "(on)\s*({0})".format("|".join(material_kind["eng"]["Painting"])), txt.lower()
    ):
        result = "Painting"
    elif re.findall(
        "({0})(에|위에|위)".format("|".join(material_kind["kor"]["Painting"])),
        "  " + re.sub(" ", "", txt.lower()),
    ):
        result = "Painting"
    elif re.findall(
        "({0})".format("|".join(material_kind["eng"]["Edition"])), txt.lower()
    ):
        result = "Edition"
    elif re.findall(
        "({0})".format("|".join(material_kind["kor"]["Edition"])),
        "  " + re.sub(" ", "", txt.lower()),
    ):
        result = "Edition"
    elif re.findall(
        "(on)\s*({0})".format("|".join(material_kind["eng"]["Works on Paper"])),
        txt.lower(),
    ):
        result = "Works on Paper"
    elif re.findall(
        "({0})(에|위에|위)".format("|".join(material_kind["kor"]["Works on Paper"])),
        "  " + re.sub(" ", "", txt.lower()),
    ):
        result = "Works on Paper"
    elif re.findall("|".join(material_kind["eng"]["Multi-media"]), txt.lower()):
        result = "Multi-media"
    elif re.findall(
        "|".join(material_kind["kor"]["Multi-media"]),
        "  " + re.sub(" ", "", txt.lower()),
    ):
        result = "Multi-media"
    elif re.findall("|".join(material_kind["eng"]["Sculpture"]), txt.lower()):
        result = "Sculpture"
    elif re.findall(
        "|".join(material_kind["kor"]["Sculpture"]), "  " + re.sub(" ", "", txt.lower())
    ):
        result = "Sculpture"
    elif re.findall("|".join(material_kind["eng"]["Painting"]), txt.lower()):
        result = "Painting"
    elif re.findall(
        re.sub(" ", "", "|".join(material_kind["kor"]["Painting"])),
        re.sub(" ", "", txt.lower()),
    ):
        result = "Painting"
    elif re.findall("|".join(material_kind["eng"]["Works on Paper"]), txt.lower()):
        result = "Works on Paper"
    elif re.findall(
        re.sub(" ", "", "|".join(material_kind["kor"]["Works on Paper"])),
        re.sub(" ", "", txt.lower()),
    ):
        result = "Works on Paper"
    else:
        result = "Others"
    return result
