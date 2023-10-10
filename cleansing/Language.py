import re


def Language(lang, text):
    if lang == "kor" and not re.findall("[ㄱ-ㅣ가-힣]", text):
        return ""
    elif lang == "eng" and re.findall("[ㄱ-ㅣ가-힣]", text):
        return ""
    return text.strip()
