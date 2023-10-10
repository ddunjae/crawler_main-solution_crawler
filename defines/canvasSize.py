# size : size of canvas
# std_l : standard large length value
# max_l : max large length value
# min_s : min small length value
# max_s : max small length value
# max_area : max area value
def call_size():
    temp = [
        {
            "size": 0,
            "std_l": 18.0,
            "max_s": 14.0,
            "min_s": 0,
        },
        {
            "size": 1,
            "std_l": 22.7,
            "max_s": 15.8,
            "min_s": 12.0,
        },
        {
            "size": 2,
            "std_l": 25.8,
            "max_s": 17.9,
            "min_s": 14.0,
        },
        {
            "size": 3,
            "std_l": 27.3,
            "max_s": 22.0,
            "min_s": 16.0,
        },
        {
            "size": 4,
            "std_l": 33.4,
            "max_s": 24.2,
            "min_s": 19.0,
        },
        {
            "size": 5,
            "std_l": 34.8,
            "max_s": 27.3,
            "min_s": 21.2,
        },
        {
            "size": 6,
            "std_l": 40.9,
            "max_s": 31.8,
            "min_s": 24.2,
        },
        {
            "size": 8,
            "std_l": 45.5,
            "max_s": 37.9,
            "min_s": 27.3,
        },
        {
            "size": 10,
            "std_l": 53.0,
            "max_s": 45.5,
            "min_s": 33.4,
        },
        {
            "size": 12,
            "std_l": 60.6,
            "max_s": 50.0,
            "min_s": 40.9,
        },
        {
            "size": 15,
            "std_l": 65.1,
            "max_s": 53.0,
            "min_s": 45.5,
        },
        {
            "size": 20,
            "std_l": 72.7,
            "max_s": 60.6,
            "min_s": 50.0,
        },
        {
            "size": 25,
            "std_l": 80.3,
            "max_s": 65.1,
            "min_s": 53.0,
        },
        {
            "size": 30,
            "std_l": 90.9,
            "max_s": 72.7,
            "min_s": 60.6,
        },
        {
            "size": 40,
            "std_l": 100.0,
            "max_s": 80.3,
            "min_s": 65.1,
        },
        {
            "size": 50,
            "std_l": 116.8,
            "max_s": 91.0,
            "min_s": 72.7,
        },
        {
            "size": 60,
            "std_l": 130.3,
            "max_s": 97.0,
            "min_s": 80.3,
        },
        {
            "size": 80,
            "std_l": 145.5,
            "max_s": 112.1,
            "min_s": 89.4,
        },
        {
            "size": 100,
            "std_l": 162.2,
            "max_s": 130.3,
            "min_s": 97.0,
        },
        {
            "size": 120,
            "std_l": 193.9,
            "max_s": 130.3,
            "min_s": 97.0,
        },
        {
            "size": 150,
            "std_l": 227.3,
            "max_s": 181.8,
            "min_s": 145.5,
        },
        {
            "size": 200,
            "std_l": 259.1,
            "max_s": 193.9,
            "min_s": 162.1,
        },
        {
            "size": 300,
            "std_l": 290.9,
            "max_s": 218.2,
            "min_s": 181.8,
        },
        {
            "size": 500,
            "std_l": 333.3,
            "max_s": 248.5,
            "min_s": 197.0,
        },
    ]

    index = 0
    while index < len(temp) - 1:
        temp[index]["max_l"] = (temp[index]["std_l"] + temp[index + 1]["std_l"]) / 2
        temp[index]["max_area"] = temp[index]["max_l"] * temp[index]["max_s"]
        index += 1
    return temp


size_canvas = call_size()


