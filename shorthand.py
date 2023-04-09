import argparse
import os
import re

FILE_PATH = "file_path"

CHECK_COMMENT = "\t% TODO: Check shorthand. Propose: "
EMPTY_SHORTHAND_PREFIX = "\tshorthand    = {"

ID_PART = "id"
TITLE_PART = "title"
AUTHOR_PART = "author"
SHORTHAND_PART = "shorthand"
YEAR_PART = "year"
TIMESTAMP_PART = "timestamp"

CITE_PARTS = [TITLE_PART, AUTHOR_PART, SHORTHAND_PART, YEAR_PART, TIMESTAMP_PART]

UNIMPORTANT_WORDS = [
    "the", "a", "on", "in", "at", "and", "of", "on", "about", "an",
    "under", "above", "between", "into", "to", "from", "by", "for",
    "в", "для", "до", "за", "из", "к", "на", "о", "при", "по", "c",
    "до", "и", "если", "то", "об"
]

def extract_author(cite):
    result = ""
    raw = cite[AUTHOR_PART]
    if raw:
        surname = ""
        first_initial = ""
        second_initial = ""
        words = re.split('\.|\s|,', raw)
        for word in words:
            if len(word) == 0:
                continue

            if len(word) > 1:
                if not surname:
                    surname = word
                    if first_initial:
                        break
                    else:
                        continue

            if not first_initial:
                first_initial = word[0] + "."
            elif not second_initial:
                second_initial = word[0] + "."

            if surname and first_initial and second_initial:
                break
        result = surname + " " + first_initial + second_initial
        if len(word) > 5:
            result += "."

    return result

def extract_title(cite):
    result = ""
    raw = cite[TITLE_PART].replace('(', '').replace(')','')
    if raw:
        words = re.split('\.|\s|,', raw)
        main_word = False
        i = 0
        while i < len(words):
            if words[i]:
                if words[i] in UNIMPORTANT_WORDS:
                    result += words[i].lower()[0]
                elif not main_word:
                    main_word = True
                    result += words[i].upper()[0]
                    j = 1
                    while j < min(5, len(words[i])):
                        result += words[i][j]
                        j+=1
                    if i + 1 != len(words) and words[i+1] in UNIMPORTANT_WORDS:
                        result += " "
                else:
                    result += words[i].upper()[0]
            i += 1

    return result

def extract_year(cite):
    year = cite[YEAR_PART]
    if not year:
        timestamp_words = cite[TIMESTAMP_PART].split('.')
        if len(timestamp_words) > 0:
            year = timestamp_words[0]
        else:
            year = "XXXX"
    return year

def extract_type(cite):
    return "art" if re.search("[a-zA-Z]", cite[TITLE_PART]) else "ст"

def generate_shorthand(cite):
    author = extract_author(cite)
    title = extract_title(cite)
    year = extract_year(cite)
    type = extract_type(cite)

    return author + title + "-" + year + type

def get_part_content(line):
    start = line.find('=') + 1
    finish = line.rfind(',')
    return line[start:finish].strip().replace('{', '').replace('}', '')

def main(args):
    # for key, value in args.items():
    #     args[key] = os.path.abspath(value)  # Convert to absolute path

    # file_path = args[FILE_PATH]
    file_path = "../monography2022/biblio.bib"
    bibliography_path = "../monography2022/bibliography.tex"
    print(f"\nGenerate for {file_path}")

    with open(file_path, 'r', encoding="utf-8") as file,\
            open("./output.bib", 'w', encoding="utf-8") as output_file, \
            open(bibliography_path, 'r', encoding="utf-8") as bibliography_file:

        lines = file.readlines()
        bibliography = bibliography_file.read()
        cite_started, shorthand_exist = False, False
        i = 0
        while i < len(lines):
            if lines[i][0] == '@':
                id = lines[i][lines[i].find("{") + 1:len(lines[i])-2]
                if id in bibliography:
                    cite_started = True
                    shorthand_exist = False
                    cite = {ID_PART: id}
                    [cite.update({part: ""}) for part in CITE_PARTS]

            if cite_started:
                words = re.split("\t|\s|=", lines[i])
                for part_key in CITE_PARTS:
                    if part_key in words:
                        cite[part_key] = get_part_content(lines[i])
                        if part_key == SHORTHAND_PART:
                            shorthand_exist = True

                if lines[i][0] == '}':
                    shorthand = generate_shorthand(cite)
                    if not shorthand_exist:
                        output_file.write(EMPTY_SHORTHAND_PREFIX + shorthand +"}\n")

                    output_file.write(CHECK_COMMENT + shorthand + "\n")
                    cite_started = False
                    shorthand_exist = False

            output_file.write(lines[i])
            i+=1


if __name__ == "__main__":

    # parser = argparse.ArgumentParser()
    # parser.add_argument(dest=FILE_PATH, type=str,
    #                     help="Bib file to generate shorthands")
    #
    # PARSED_ARGS = parser.parse_args()

    # main(vars(PARSED_ARGS))
    main([])