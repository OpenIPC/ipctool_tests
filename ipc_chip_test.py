#!/usr/bin/env python3

import pytest
from subprocess import Popen, PIPE
import os
import yaml
import telnet


def pytest_generate_tests(metafunc):
    def generate_id(input_data, level):
        level += 1

        # Выбираем как это будет выглядеть
        INDENTS = {
            # level: (levelmark, addition_indent)
            1: ("_", ["", ""]),
            2: ("-", ["[", "]"]),
        }
        COMMON_INDENT = ("-", ["[", "]"])

        levelmark, additional_indent = INDENTS.get(level, COMMON_INDENT)

        # Если глубже второго уровня - идентификатором становится тип данных
        if level > 3:
            return (
                additional_indent[0] + type(input_data).__name__ + additional_indent[1]
            )

        # Возвращаем простые данные
        elif isinstance(input_data, (str, bool, float, int)):
            return str(input_data)

        # Разбираем список
        elif isinstance(input_data, (list, set, tuple)):
            # Погружаемся в список, чтобы проверить те данные, что внутри
            list_repr = levelmark.join(
                [generate_id(input_value, level=level) for input_value in input_data]
            )
            return additional_indent[0] + list_repr + additional_indent[1]

        # Ключи словаря переводим в строку
        elif isinstance(input_data, dict):
            return "{" + levelmark.join(input_data.keys()) + "}"

        # Или ничего для ничего
        else:
            return None

    if "test_case" not in metafunc.fixturenames:
        return

    dir_path = os.path.dirname(os.path.abspath(metafunc.module.__file__))

    file_path = os.path.join(dir_path, metafunc.function.__name__ + ".yaml")
    with open(file_path) as f:
        raw_test_cases = yaml.full_load(f)

    if not raw_test_cases:
        raise ValueError("Test cases not loaded")

    test_cases = []

    # Проходим по нашим сырым данным
    for case_id, test_case in enumerate(raw_test_cases):
        # Ищем список маркеров
        marks = [getattr(pytest.mark, name) for name in test_case.get("marks", [])]

        # Берем идентификатор из данных, либо сгенерируем
        case_id = test_case.get("id", generate_id(test_case["hostname"], level=0))

        # Добавляем в наш список сгенерированный из тестовых данных pytest.param
        test_cases.append(pytest.param(test_case, marks=marks, id=case_id,))

    return metafunc.parametrize("test_case", test_cases)


def do_test(test_case):
    host = test_case["hostname"]
    expected = test_case["output"]

    hash = os.environ["SHA"]

    run_cmd = "cd /tmp; rm -f ipc_chip_info; wget openipc.s3-eu-west-1.amazonaws.com/ipc_chip_info-{0}; chmod +x ipc_chip_info-{0}; ./ipc_chip_info-{0}; rm ipc_chip_info-{0}".format(
        hash
    )
    with Popen(["ssh", "root@{}".format(host), run_cmd], stdout=PIPE) as proc:
        output = [i.decode("utf-8") for i in proc.stdout.read().splitlines()]
        assert output == expected


def test_zftlab(test_case):
    do_test(**locals())
