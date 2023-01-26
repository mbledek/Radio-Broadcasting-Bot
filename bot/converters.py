import re
import math


# Converts text boolean to actual boolean ("True" -> True)
def convert_to_boolean(user_input):
    if user_input == "True":
        return True
    elif user_input == "False":
        return False
    else:
        return


# A Polish "dictionary" converting numbers to text, so that Jarvis can read them
def num_to_text(user_input):
    output = " "
    user_input = str(user_input)
    length = len(user_input)
    if int(length) % 3 == 2:
        user_input = "0" + user_input
        length = length + 1
    elif int(length) % 3 == 1:
        user_input = "00" + user_input
        length = length + 2

    num_triples = length / 3
    num_triples = int(num_triples)
    for i in range(num_triples):
        triple = user_input[3 * i: 3 * i + 3]
        # Setki
        if int(triple[0]) == 1: output = output + " sto"
        elif int(triple[0]) == 2: output = output + " dwieście"
        elif int(triple[0]) == 3: output = output + " trzysta"
        elif int(triple[0]) == 4: output = output + " czterysta"
        elif int(triple[0]) == 5: output = output + " pięćset"
        elif int(triple[0]) == 6: output = output + " sześćset"
        elif int(triple[0]) == 7: output = output + " siedemset"
        elif int(triple[0]) == 8: output = output + " osiemset"
        elif int(triple[0]) == 9: output = output + " dziewięćset"

        # Dziesiątki
        for x in range(1):
            if int(triple[1]) == 1:
                if int(triple[2]) == 0: output = output + " dziesięć"
                elif int(triple[2]) == 1: output = output + " jedenaście"
                elif int(triple[2]) == 2: output = output + " dwanaście"
                elif int(triple[2]) == 3: output = output + " trzynaście"
                elif int(triple[2]) == 4: output = output + " czternaście"
                elif int(triple[2]) == 5: output = output + " piętnaście"
                elif int(triple[2]) == 6: output = output + " szesnaście"
                elif int(triple[2]) == 7: output = output + " siedemnaście"
                elif int(triple[2]) == 8: output = output + " osiemnaście"
                elif int(triple[2]) == 9: output = output + " dziewiętnaście"
                continue
            elif int(triple[1]) == 2: output = output + " dwadzieścia"
            elif int(triple[1]) == 3: output = output + " trzydzieści"
            elif int(triple[1]) == 4: output = output + " czterdzieści"
            elif int(triple[1]) == 5: output = output + " pięćdziesiąt"
            elif int(triple[1]) == 6: output = output + " sześćdziesiąt"
            elif int(triple[1]) == 7: output = output + " siedemdziesiąt"
            elif int(triple[1]) == 8: output = output + " osiemdziesiąt"
            elif int(triple[1]) == 9: output = output + " dziewięćdziesiąt"

            # Jedności
            if int(triple[2]) == 1: output = output + " jeden"
            elif int(triple[2]) == 2: output = output + " dwa"
            elif int(triple[2]) == 3: output = output + " trzy"
            elif int(triple[2]) == 4: output = output + " cztery"
            elif int(triple[2]) == 5: output = output + " pięć"
            elif int(triple[2]) == 6: output = output + " sześć"
            elif int(triple[2]) == 7: output = output + " siedem"
            elif int(triple[2]) == 8: output = output + " osiem"
            elif int(triple[2]) == 9: output = output + " dziewięć"

            if triple == "000": output = "zero"

        # Pozycyjny
        if (num_triples - i) > 6: output = output + " wiecej niz biliard"
        elif (num_triples - i) == 6:
            if int(triple[2]) == 1 and int(triple[1]) != 1 and int(triple[0]) == 0: output = output + " biliard"
            elif int(triple[2]) in (2, 3, 4) and triple[1] == 0: output = output + " biliardy"
            else: output = output + " biliardów"
        elif (num_triples - i) == 5:
            if int(triple[2]) == 1 and int(triple[1]) != 1 and int(triple[0]) == 0: output = output + " bilion"
            elif int(triple[2]) in (2, 3, 4) and triple[1] == 0: output = output + " biliony"
            else: output = output + " bilionów"
        elif (num_triples - i) == 4:
            if int(triple[2]) == 1 and int(triple[1]) != 1 and int(triple[0]) == 0: output = output + " miliard"
            elif int(triple[2]) in (2, 3, 4) and triple[1] == 0: output = output + " miliardy"
            else: output = output + " miliardów"
        elif (num_triples - i) == 3:
            if int(triple[2]) == 1 and int(triple[1]) != 1 and int(triple[0]) == 0: output = output + " milion"
            elif int(triple[2]) in (2, 3, 4) and triple[1] == 0: output = output + " miliony"
            else: output = output + " milinów"
        elif (num_triples - i) == 2:
            if int(triple[2]) == 1 and int(triple[1]) != 1 and int(triple[0]) == 0: output = output + " tysiąc"
            elif int(triple[2]) in (2, 3, 4) and triple[1] == 0: output = output + " tysiące"
            else: output = output + " tysięcy"

    return output


# Converts a text with numbers in it to a text with numbers spoken, using previously mentioned num_to_text()
def numbtext_to_texttext(user_input):
    list_of_num = re.findall(r"\d+", user_input)
    for item in list_of_num:
        user_input = user_input.replace(list_of_num[list_of_num.index(item)], num_to_text(list_of_num[list_of_num.index(item)]))
    return user_input


# Converts a text with ugly html formatting
def html_mail_clear(user_input):
    user_input = re.sub("""<div dir="ltr">""", "", user_input)
    user_input = re.sub(r"</div>\r\n", "", user_input)
    user_input = re.sub(r"""<div dir="auto">""", "", user_input)
    user_input = re.sub(r"""\xa0""", "", user_input)
    return user_input


# Converts a long string into a list of strings according to a limit of characters in each string (single_max)
def split_str(user_input, single_max):
    output = []
    iterations = math.ceil(len(str(user_input)) / int(single_max))
    user_input = user_input.split(" ")
    for i in range(0, int(int(iterations))):
        split_output = ""
        while len(split_output) < int(single_max) and len(user_input) > 0:
            split_output = str(split_output + user_input[0] + " ")
            user_input.pop(0)
        output.append(split_output)
    return output



