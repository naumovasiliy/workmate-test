import argparse
import csv
import re
from tabulate import tabulate

from CSVReaderError import CSVReaderError

def create_parser():
    # Создание парсера аргументов командной строки

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', required=True)
    parser.add_argument('-w', '--where')
    parser.add_argument('-a', '--aggregate')

    return parser

def create_where_cond(where: str) -> tuple:
    # Парсинг условия where
    where_tuple = ()
    if not where:
        return where_tuple
    match = re.findall(r'(\w+)\s*([><=])\s*([\s\w]+)', where)
    if match:
        if len(match) > 1:
            raise CSVReaderError('На данный момент поддерживается одно условие фильтрации')
        where_tuple = match[0]

    else:
        # Поднять ошибку и обработать на выходе из main
        raise CSVReaderError(f'Не получилось обработать следующее условие: {where}')

    return where_tuple

def check_row(row: list, where_cond: tuple) -> bool:
    # Проверка условий фильтрации для строки
    # Структура where_cond: (field_index, operator, value)
    flag = True
    if not where_cond:
        return flag

    field_number_flag = is_number(row[where_cond[0]])
    value_number_flag = is_number(where_cond[2])
    if field_number_flag and not value_number_flag:
        raise CSVReaderError(f'В файле в столбце хранятся числа, в условии сравнение со строкой')

    match where_cond[1]:
        case '<':
            if field_number_flag:
                flag = float(row[where_cond[0]]) < float(where_cond[2])
            else:
                flag = row[where_cond[0]] < where_cond[2]
        case '=':
            if field_number_flag:
                flag = float(row[where_cond[0]]) == float(where_cond[2])
            else:
                flag = row[where_cond[0]] == where_cond[2]
        case '>':
            if field_number_flag:
                flag = float(row[where_cond[0]]) > float(where_cond[2])
            else:
                flag = row[where_cond[0]] > where_cond[2]

    return flag



def aggregate_csv(table: list, aggregate: str) -> tuple:
    # Агрегация

    # Получаем поле агрегации и функцию, по которой обобщать
    agg_cond = aggregate.split('=')
    if len(agg_cond) != 2:
        raise CSVReaderError(f'В агрегатном условии указано что-то не то: {agg_cond[0]}')
    if agg_cond[0] not in table[0]:
        raise CSVReaderError(f'В файле нет столбца {agg_cond[0]}')
    else:
        agg_index = table[0].index(agg_cond[0])
        if not is_number(table[1][agg_index]):
            raise CSVReaderError(f'В столбце {agg_cond[0]}, указанном в агрегатном условии, хранятся не числа')

    match agg_cond[1]:
        case 'min':
            return [min([float(x[agg_index]) for x in table[1:]])], agg_cond[1]
        case 'max':
            return [max([float(x[agg_index]) for x in table[1:]])], agg_cond[1]
        case 'avg':
            return [avg([float(x[agg_index]) for x in table[1:]])], agg_cond[1]
        case _:
            raise CSVReaderError(f'Для агрегации поддерживаются: avg, min, max, введенная функция: {agg_cond[1]}')

def is_number(test_str: str) -> bool:
    try:
        float(test_str)
        return True
    except ValueError:
        return False

def avg(nums: list) -> float:
    return sum(nums) / len(nums)

if __name__ == '__main__':

    parser = create_parser()
    args = parser.parse_args()

    try:
        with open(args.file, 'r') as file:
            reader = csv.reader(file)
            fieldnames = reader.__next__()
            result = []
            where_condition = create_where_cond(args.where)

            if where_condition:
                if where_condition[0] not in fieldnames:
                    raise CSVReaderError(f'В файле нет столбца {where_condition[0]}')
                else:
                    where_condition = (fieldnames.index(where_condition[0]), *where_condition[1:])
            for row in reader:
                if check_row(row, where_condition):
                    result.append(row)

            if args.aggregate and len(result):
                func, res = aggregate_csv([fieldnames] + result, args.aggregate)
                print(tabulate([func], [res], tablefmt='psql'))
            else:
                print(tabulate(result, fieldnames, tablefmt='psql'))

    except FileNotFoundError as exc:
        print(f'Нет такого файла или доступ к нему ограничен: {exc.filename}')
    except CSVReaderError as exc:
        print(exc.message)
