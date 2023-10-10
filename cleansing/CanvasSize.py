import os
import sys
import re

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from defines.canvasSize import size_canvas


def calculateCanvasSize(area, large, small):
    for size, index in zip(size_canvas[:-1], range(len(size_canvas) -1)):
        if size["max_l"] > large and size["max_area"] >= area:
            size = size["size"]
            break
    else:
        index = len(size_canvas)-1
        size = size_canvas[-1]["size"]
    if large/small <= 2:
        return size
    if large/small <= 3:
        if (index - 1) < 0:
            return size
        else:
            return size_canvas[index - 1]["size"]
    if large/small <= 4:
        if (index - 2) < 0:
            return size
        else:
            return size_canvas[index - 2]["size"]
    if (index - 3) < 0:
        return size
    else:
        return size_canvas[index - 3]["size"]





#1
def CanvasSize(material_kind, height, width, desc):
    if re.findall("\(\s*\d+호?\s*\)", str(desc)):
        return int(re.sub("[^0-9]","",re.findall("\(\s*\d+호?\s*\)", str(desc))[0]))
        
    if (str(height).lower().strip() in ["none", "nan", ""] or str(width).lower().strip() in ["none", "nan", ""]):
        return None
    if material_kind not in ["Painting", "Edition", "Works on Paper"]:
        return ""
    area = float(height) * float(width)
    if area > 72726:
        return 500
    large = max(float(height), float(width))
    small = min(float(height), float(width))
    
    if small == 0.0:
        return ""
    result = calculateCanvasSize(area, large, small)
    return result


def Canvas_size_not_depend_on_material_kind(height, width):
    area = float(height) * float(width)
    if area > 72726:
        return 500 #size 500
    
    large = max(float(height), float(width))
    small = min(float(height), float(width))

    if small == 0.0:
        return ""
    result = calculateCanvasSize(area, large, small)
    return result
