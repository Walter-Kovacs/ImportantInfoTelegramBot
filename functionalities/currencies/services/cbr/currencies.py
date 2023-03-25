import csv

codes_by_phrase = dict()
codes_by_roditelny_padezh = dict()
codes_by_imenitelny_padezh = dict()


def _init_currencies_dicts():
    global codes_by_phrase
    global codes_by_roditelny_padezh
    global codes_by_imenitelny_padezh

    with open('functionalities/currencies/services/cbr/currencies.csv') as csvfile:
        for row in csv.reader(csvfile):
            code = row[0]
            for i in range(1, len(row)):
                codes_by_phrase[row[i]] = code
            codes_by_roditelny_padezh[row[2]] = code
            codes_by_imenitelny_padezh[row[1]] = code


_init_currencies_dicts()
