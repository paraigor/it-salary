import os
from itertools import count

import dotenv
import requests
from terminaltables import AsciiTable


def get_hh_vacancies(url, payload, header):
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


def get_sj_vacancies(url, payload, header):
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
    payment_from = vacancy["payment_from"]
    payment_to = vacancy["payment_to"]
    currency = vacancy["currency"]
    if not payment_from and not payment_to or currency != "rub":
        return None
    return predict_salary(payment_from, payment_to)


def get_salaries(vacancies, predict_rub_salary):
    salaries = []
    for vacancy in vacancies:
        salary = predict_rub_salary(vacancy)
        if salary:
            salaries.append(salary)
    return salaries


def process_vacancies(it_langs, vacancies_params):
    it_lang_vacancies = {}
    collector = vacancies_params["collector"]
    url = vacancies_params["url"]
    payload = vacancies_params["payload"]
    header = vacancies_params["header"]
    for lang in it_langs:
        match vacancies_params["search_key"]:
            case "keyword":
                payload["keyword"] = f"{lang}"
            case "text":
                payload["text"] = f"NAME:{lang}"
        salaries, vacancies_found = collector(url, payload, header)
        vacancies_processed = len(salaries)
        if vacancies_processed:
            average_salary = int(sum(salaries) / vacancies_processed)
        else:
            average_salary = 0
        it_lang_vacancies[lang] = {
            "vacancies_found": vacancies_found,
            "vacancies_processed": vacancies_processed,
            "average_salary": average_salary,
        }
    return it_lang_vacancies


def print_table(title, it_lang_stat):
    table_content = [
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
        table_content.append(lang_stat)

    table = AsciiTable(table_content, title)
    print(table.table)


def main():
    dotenv.load_dotenv()
    sjob_key = os.environ["SJOB_KEY"]
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
    hh_prof_category_id = 96
    sj_prof_category_id = 48
    hh_moscow_id = 1
    sj_moscow_id = 4
    vacancy_publish_period = 30
    vacancies_per_page = 100

    payload_hh = {
        "professional_role": hh_prof_category_id,
        "area": hh_moscow_id,
        "period": vacancy_publish_period,
        "per_page": vacancies_per_page,
    }
    hh_vacancies_params = {
        "url": "https://api.hh.ru/vacancies",
        "payload": payload_hh,
        "search_key": "text",
        "header": {},
        "collector": get_hh_vacancies,
    }
    print_table(
        "HeadHunter Moscow",
        process_vacancies(popular_it_langs, hh_vacancies_params),
    )

    payload_sj = {
        "catalogues": sj_prof_category_id,
        "t": sj_moscow_id,
        "period": vacancy_publish_period,
        "count": vacancies_per_page,
    }
    sj_vacancies_params = {
        "url": "https://api.superjob.ru/2.0/vacancies/",
        "payload": payload_sj,
        "search_key": "keyword",
        "header": {"X-Api-App-Id": sjob_key},
        "collector": get_sj_vacancies,
    }
    print_table(
        "SuperJob Moscow",
        process_vacancies(popular_it_langs, sj_vacancies_params),
    )


if __name__ == "__main__":
    main()
