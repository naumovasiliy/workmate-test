import pytest
from pygments.style import ansicolors

from main import *

def test_create_where_cond():
    assert create_where_cond('fieldname<123') == ('fieldname', '<', '123')

@pytest.mark.xfail(raises=CSVReaderError)
def test_create_where_cond_fail():
    assert create_where_cond('fieldname<<123') == ('fieldname', '<', '123')

def test_check_row():
    test_row = ['Vasiliy', 'Naumov', '29', '173']
    test_where = (3, '>', 170)
    assert check_row(test_row, test_where)

@pytest.mark.xfail(raises=CSVReaderError)
def test_check_row_fail():
    test_row = ['Vasiliy', 'Naumov', '29', '173']
    test_where = (3, '=', 'Высокий')
    assert  check_row(test_row, test_where)

def test_aggregate_csv():
    table = create_test_table()
    fieldnames = create_test_fieldnames()
    assert aggregate_csv([fieldnames] + table, 'age=avg')

@pytest.mark.xfail(raises=CSVReaderError)
@pytest.mark.parametrize('x', ['age=median', 'name=avg', 'weight=min'])
def test_aggregate_csv_fail(x):
    table = create_test_table()
    fieldnames = create_test_fieldnames()
    assert aggregate_csv([fieldnames] + table, x)

@pytest.mark.parametrize('x', ['123', '1.2'])
def test_is_number_true(x):
    assert is_number(x)

@pytest.mark.parametrize('x', ['string', 'str123'])
def test_in_number_false(x):
    assert not is_number(x)

def test_avg():
    test_arr = [1, 2, 3, 4]
    assert avg(test_arr) == 2.5


def create_test_table():
    return [['Vasiliy', 'Naumov', '29', '173'],
             ['Vasiliy', 'Pupkin', '34', '182'],
             ['Egor', 'Moskvin', '17', '167'],
             ['Andrey', 'Golubev', '31', '192'],
             ['Grigoriy', 'Boroda', '48', '174']]

def create_test_fieldnames():
    return ['name', 'surname', 'age', 'height']