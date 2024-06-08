import argparse
import os
from itertools import count

import dotenv
import requests
from terminaltables import AsciiTable


def get_hh_vacancy_data(url, payload, header):
    salaries = []
    vacancies_found = 0
    for page in count():
        payload["page"] = page
        page_response = requests.get(url, params=payload, headers=header)
        page_response.raise_for_status()
        page_payload = page_response.json()

        salaries += get_salaries(page_payload["items"], predict_rub_salary_hh)

        if page >= page_payload["pages"] - 1:
            vacancies_found = page_payload["found"]
            break
    return salaries, vacancies_found


def get_sj_vacancy_data(url, payload, header):
    salaries = []
    vacancies_found = 0
    for page in count():
        payload["page"] = page
        page_response = requests.get(url, params=payload, headers=header)
        page_response.raise_for_status()
        page_payload = page_response.json()

        salaries += get_salaries(
            page_payload["objects"], predict_rub_salary_sj
        )

        vacancies_found += page_payload["total"]
        if not page_payload["more"]:
            break
    return salaries, vacancies_found


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return round((salary_from + salary_to) / 2, 0)
    elif not salary_to:
        return round(salary_from * 1.2, 0)
    else:
        return round(salary_to * 0.8, 0)


def predict_rub_salary_hh(vacancy):
    salary = vacancy["salary"]
    if not salary or salary["currency"] != "RUR":
        return None
    return predict_salary(salary["from"], salary["to"])


def predict_rub_salary_sj(vacancy):
    if (
        not vacancy["payment_from"]
        and not vacancy["payment_to"]
        or vacancy["currency"] != "rub"
    ):
        return None
    return predict_salary(vacancy["payment_from"], vacancy["payment_to"])


def get_salaries(vacancies, function):
    salaries = []
    for vacancy in vacancies:
        if function(vacancy):
            salaries.append(function(vacancy))
    return salaries


def process_vacancies(it_langs, platform_data):
    it_lang_vacancies = {}
    payload = platform_data["payload"]
    for lang in it_langs:
        match platform_data["search_key"]:
            case "keyword":
                payload["keyword"] = f"{lang}"
            case "text":
                payload["text"] = f"NAME:{lang}"
        vacancy_data = platform_data["collector"](
            platform_data["url"], payload, platform_data["header"]
        )
        vacancies_processed = len(vacancy_data[0])
        if vacancies_processed:
            average_salary = int(sum(vacancy_data[0]) / vacancies_processed)
        else:
            average_salary = 0
        it_lang_vacancies[lang] = {
            "vacancies_found": vacancy_data[1],
            "vacancies_processed": vacancies_processed,
            "average_salary": average_salary,
        }
    return it_lang_vacancies


def print_table(title, it_lang_stat):
    table_data = [
        [
            "Язык программирования",
            "Вакансий найдено",
            "Вакансий обработано",
            "Средняя зарплата",
        ],
    ]

    for lang, stat in it_lang_stat.items():
        lang_stat = [
            lang,
            stat["vacancies_found"],
            stat["vacancies_processed"],
            stat["average_salary"],
        ]
        table_data.append(lang_stat)

    table = AsciiTable(table_data, title)
    print(table.table)


def main():
    dotenv.load_dotenv()
    sjob_key = os.environ["SJOB_KEY"]
    parser = argparse.ArgumentParser(
                prog = "dev_job_stat",
                description = """Utility for fetching salary statistics for
                  JavaScript, Java, Python, Ruby, PHP, C++, C#, Go, Scala,
                  Swift, TypeScript programming languages from HeadHunter
                  and SuperJob platforms. Uses vacancies published in last
                  30 days."""
        )
    parser.parse_args()

    popular_it_langs = [
        "JavaScript",
        "Java",
        "Python",
        "Ruby",
        "PHP",
        "C++",
        "C#",
        "Go",
        "Scala",
        "Swift",
        "TypeScript",
    ]

    payload_hh = {
        "professional_role": "96",
        "area": 1,
        "period": 30,
        "per_page": 100,
    }
    hh_data = {
        "url": "https://api.hh.ru/vacancies",
        "payload": payload_hh,
        "search_key": "text",
        "header": {},
        "collector": get_hh_vacancy_data,
    }
    print_table(
        "HeadHunter Moscow", process_vacancies(popular_it_langs, hh_data)
    )

    payload_sj = {"catalogues": 48, "t": 4, "period": 30, "count": 100}
    sj_data = {
        "url": "https://api.superjob.ru/2.0/vacancies/",
        "payload": payload_sj,
        "search_key": "keyword",
        "header": {"X-Api-App-Id": sjob_key},
        "collector": get_sj_vacancy_data,
    }
    print_table(
        "SuperJob Moscow", process_vacancies(popular_it_langs, sj_data)
    )


if __name__ == "__main__":
    main()
