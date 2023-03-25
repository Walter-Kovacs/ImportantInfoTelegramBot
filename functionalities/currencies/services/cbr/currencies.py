import csv

codes_by_phrase = dict()
codes_by_roditelny_padezh = dict()
imenitelny_padezh_by_code = dict()


def _init_currencies_dicts():
    global codes_by_phrase
    global codes_by_roditelny_padezh
    global imenitelny_padezh_by_code

    with open('functionalities/currencies/services/cbr/currencies.csv') as csvfile:
        for row in csv.reader(csvfile):
            code = row[0]
            for i in range(1, len(row)):
                codes_by_phrase[row[i]] = code
            codes_by_roditelny_padezh[row[2]] = code
            imenitelny_padezh_by_code[code] = row[1]


_init_currencies_dicts()
