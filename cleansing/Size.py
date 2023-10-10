import re
from cmath import nan
def Size(txt):
    size = {"height": "", "width": "", "depth": ""}
    if re.search("高|長|口徑|底徑", txt):
        if re.findall("高\s*(\d+\.?\d*)\W*(\d+\.?\d*)\s*(×|X|x)\s*(\d+\.?\d*)", txt):
            temp = re.findall("高\s*(\d+\.?\d*)\W*(\d+\.?\d*)\s*(×|X|x)\s*(\d+\.?\d*)", txt)[0]
            print(re.findall("高\s*(\d+\.?\d*)\W*(\d+\.?\d*)\s*(×|X|x)\s*(\d+\.?\d*)", txt))
            size["depth"] = float(re.findall("\d+\.?\d*",txt)[0])
            size["height"] = float(re.findall("\d+\.?\d*",txt)[1])
            size["width"] = float(re.findall("\d+\.?\d*",txt)[2])
            return size, ""
        for i in re.findall("(高|長|口徑|底徑)+\s*(\d+\.?\d*)", txt):
            if size["height"] and size["width"] and size["depth"]:
                break
            if i[0] == "高":
                size["depth"] = i[1]
            elif i[0] == "底徑":
                size["width"] = i[1]
            elif i[0] in ["口徑", "長"]:
                size["height"] = i[1]    
        return size, ""
    
    etc = []
    unit = False
    if re.findall("mm|㎜", txt.lower()):
        temp = re.split("mm|㎜", txt.lower())
        if len(temp) > 1:
            etc = temp[1:]
        temp = temp[0]
        unit = True
    elif not re.findall("cm|츠|㎝|mm|㎜", txt.lower()):
        return size, ""
    
    if re.findall("(cm|츠|㎝),",txt):
        etc_ = " ".join(re.split("cm, |츠, |㎝, ",txt)[1:])
        if etc_.strip():
            etc.append(etc_)
        txt = re.split("cm, |츠, |㎝, ",txt)[0]+"cm"
    size_list = []

    if re.findall('x|×|☓', txt.lower()) and re.findall("(\d+)(\.\d+)?", txt):
        for i in re.split('x|×|☓', txt.lower()):
            if not re.findall("(\d+)(\.\d+)?", i) :
                size_list.append(nan)
                continue
            for d in re.findall("\(\s*\d{1,3}\s*\)|\d{1,3}\s*호", i):
                etc.append(re.findall("\d+", d)[0]+"호")
            i = re.sub("\(\s*\d{1,3}\s*\)|\d{1,3}\s*호", "",i)
            if re.findall("(\d+)(\.\d+)?", i):
                size_list.append("".join(re.findall("(\d+)(\.\d+)?", i)[-1]))
            else:
                print("----------->",txt)
    if size_list:
        if len(size_list) == 1:
            if re.findall("diameter|Ф|Φ", txt):
                size["height"] = float(size_list[0])
                size["width"] = float(size_list[0])
            elif re.findall("width|wide", txt):
                size["width"] = float(size_list[0])
            elif re.findall("depth|thickness|(d)|(h)|高", txt):
                size["depth"] = float(size_list[0])
            else:
                size["height"] = float(size_list[0])
        elif len(size_list) == 2:
            size["height"] = float(size_list[0])
            if re.findall("diameter|Ф|Φ", txt):
                size["width"] = float(size_list[0])
                size["depth"] = float(size_list[1])
            else:
                size["width"] = float(size_list[1])
        else:
            size["width"] = float(size_list[1])
            if re.findall("{0}\s*(depth|thickness|(d)|(h)|高)".format(size_list[0]), txt):
                size["height"] = float(size_list[0])
                size["depth"] = float(size_list[2])
            else:
                size["height"] = float(size_list[0])
                size["depth"] = float(size_list[2])
    if unit:
        if size["height"]:
            size["height"] = size["height"] / 10
        if size["depth"]:
            size["depth"] = size["depth"] / 10
        if size["width"]:
            size["width"] = size["width"] / 10
    etc = " / ".join(etc)
    for k,v in size.items():
        if size[k] == nan:
            size[k] == ""
    return size, etc