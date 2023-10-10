import re


def MfgDate(txt):
    if type(txt) != str or not txt:
        return None
    if re.match("\d\d\d\d", txt):
        return txt
    mfg_date = []
    if re.findall("\d\d세기", txt):
        temp = re.findall("\d\d세기", txt)
        for i in temp:
            mfg_date.append(str(int(i[:-2])-1) + "00")
    if re.findall("\d\d\d\d", txt):
        temp = re.findall("\d\d\d\d", txt)
        for i in temp:
            mfg_date.append(i)
    mfg_date = list(set(mfg_date))
    if len(mfg_date) == 0:
        return None
    elif len(mfg_date) == 1:
        mfg_date = mfg_date[0]
    else:
        mfg_date = mfg_date[0] + "/" + mfg_date[1]
    return mfg_date
