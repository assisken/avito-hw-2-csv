from collections import Counter
from dataclasses import dataclass, astuple, fields
from functools import partial
from statistics import mean
from typing import List, Set, Iterable, Callable, Dict

import csv


@dataclass
class Employee:
    fio: str
    position: str
    unit: str
    review_result: int
    salary: int

    @classmethod
    def from_csv(cls, record: List[str]):
        return cls(
            fio=record[0],
            position=record[1],
            unit=record[2],
            review_result=int(record[3]),
            salary=int(record[4]),
        )


@dataclass
class ReportRecord:
    unit: str
    quantity: int
    min_salary: int
    max_salary: int
    avg_salary: float


def units(employees: Iterable[Employee]) -> Set[str]:
    return {e.unit for e in employees}


def count_employers_in_units(employees: Employee) -> Dict[str, int]:
    counter = Counter()
    for e in employees:
        counter[e.unit] += 1
    return dict(counter)


def aggregate_salary_from(
    unit: str, *, aggregator: Callable, employees: Iterable[Employee]
) -> int:
    return aggregator(e.salary for e in employees if e.unit == unit)


min_salary = partial(aggregate_salary_from, aggregator=min)
max_salary = partial(aggregate_salary_from, aggregator=max)
avg_salary = partial(aggregate_salary_from, aggregator=mean)


def generate_report(employees: Iterable[Employee]) -> List[ReportRecord]:
    employees_count_by_unit = count_employers_in_units(employees)

    return [
        ReportRecord(
            unit=unit,
            quantity=employees_count_by_unit[unit],
            max_salary=max_salary(unit, employees=employees),
            min_salary=min_salary(unit, employees=employees),
            avg_salary=avg_salary(unit, employees=employees),
        )
        for unit in units(employees)
    ]


def print_report(report: List[ReportRecord]):
    header = tuple(f.name.upper() for f in fields(report[0]))
    format = "{:>20}" * len(header)

    print(format.format(*header))
    for r in report:
        print(format.format(*astuple(r)))


def save_report_to_file(report: List[ReportRecord], *, filename="report.csv"):
    with open(filename, "w") as file:
        writer = csv.writer(file)
        for r in report:
            writer.writerow(astuple(r))
    print("Сохранено в report.csv")


selects: Dict[str, Callable[[Iterable[Employee]], None]] = {
    "1": lambda emp: print("Все отделы: ", ", ".join(units(emp))),
    "2": lambda emp: print_report(generate_report(emp)),
    "3": lambda emp: save_report_to_file(generate_report(emp)),
    "q": lambda _: None,
}

with open("employees.csv", "r") as file:
    employees_reader = csv.reader(file)
    employees = [Employee.from_csv(e) for e in employees_reader]

selected = "_"
while selected != "q":
    print(
        """Введите команду, перечисленную ниже:
        1. Вывести все отделы
        2. Вывести сводный отчёт по отделам
        3. Сохранить отчёт в виде файла (report.csv)
        q. Выход"""
    )
    selected = input("> ")

    while selected not in selects:
        allowed_selects = ", ".join(selects)
        print("Вы ошиблись. Введите один из:", allowed_selects)
        selected = input("> ")

    selects[selected](employees)
    print()
