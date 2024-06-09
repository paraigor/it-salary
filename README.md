# Dev job informer

`dev_job_stat` is a utility providing salary statistics for some popular programming languages. Particularly: JavaScript, Java, Python, Ruby, PHP, C++, C#, Go, Scala, Swift, TypeScript.

Data fetched from HeadHunter and SuperJob platforms.

Utility calculates average salary for available vacancies of paticular language, published in last 30 days and print a summary table to console.

### Installation

Python3 should already be installed. 
Use `pip` (or `pip3`, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```

SuperJob API secret key is required to use this utility. Key is generated after [creating application](https://api.superjob.ru/register) on the SuperJob platform and looks like: `v3.r.123456789.1abc1234def4567gh89i01k23lm456n789o01234.567e8d9b012c34fc56df7890ccdb1a234b5a67d8`.

Security sensitive information recommended storing in the project using `.env` files.

Key name to store secret value is `SJOB_KEY`.

SuperJob API version 2.0 is used for requests.

### Usage

Easy to use utility. No arguments needed:
```
$ python dev_job_stat.py
```
Output example:
```
+HeadHunter Moscow------+------------------+---------------------+------------------+
| Язык программирования | Вакансий найдено | Вакансий обработано | Средняя зарплата |
+-----------------------+------------------+---------------------+------------------+
| JavaScript            | 342              | 111                 | 210228           |
| Java                  | 952              | 114                 | 252448           |
...
```

### Project Goals

This code was written for educational purposes as part of an online course for web developers at [dvmn.org](https://dvmn.org/).
 
