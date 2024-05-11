# gitcheck - Скрипт для сверки задач в релизе Jira и коммитов в git

## Настройка окружения

1. Убедиться что в системе установлен python 3.11 и выше

2. Клонировать репозиторий проекта 

```bash
git clone git@github.com:akoval77/gitcheck.git
```

3. Перейти в рабочую папку проекта :
```bash
cd gitcheck
```

4. Создать виртуальное окружение Python:
[Официальная документация Python](https://docs.python.org/3/tutorial/venv.html) для настройки виртуального окружения.


```bash
python3 -m venv venv
```

При использовании IDE PyCharm нет необходимости выполнять этот и последующий шаги, так как при первом открытии проекта PyCharm предложит создать виртуальное окружение автоматически 

5. Активировать виртуальное окружение:
   - Для Windows:
   ```
   .\venv\Scripts\activate
   ```
   - Для macOS и Linux:
   ```
   source venv/bin/activate
   ```
6. Установить требуемые пакеты Python из файла `requirements.txt`:

```
pip install -r requirements.txt
```

## Запуск скрипта

Для получения информации о параметрах командной строки выполнить команду:

```bash
python main.py -h
```
в терминале будет отображена подсказка по каждому параметру
```bash
usage: main.py [-h] path first last project release

positional arguments:
  path        Gitlab project URL 
  first       First tag or branch name
  last        Last tag branch name
  project     Jira project name
  release     Jira release name
```
   - path - url проекта в gitlab http://147.45.104.169/rnd/gitcheck   
   - first - тег или ветка предыдущего релиза - 0.0.0  
   - last - тег или ветка текущего релиза - 1.0.0
   - project - наименование проекта в Jira - "Git Check"
   - release - наименование релиза в Jira - "1.0.0" 

Пример запуска скрипта 

```bash
python main.py http://147.45.104.169/rnd/gitcheck 0.0.0 1.0.0 "Git Check" "1.0.0" 
```
Вывод скрипта
```bash
--------------------------------------- In release ---------------------------------------
JG-8 1c33c136   Готово               https://quick-order.atlassian.net/browse/JG-8
JG-7 --------   К выполнению         https://quick-order.atlassian.net/browse/JG-7
JG-6 73b9b6f2   Готово               https://quick-order.atlassian.net/browse/JG-6
JG-5 5ef4b1b4   Готово               https://quick-order.atlassian.net/browse/JG-5
JG-4 cb827516   Готово               https://quick-order.atlassian.net/browse/JG-4
JG-3 cb827516   Готово               https://quick-order.atlassian.net/browse/JG-3
JG-2 cb827516   Готово               https://quick-order.atlassian.net/browse/JG-2
JG-1 cb827516   Готово               https://quick-order.atlassian.net/browse/JG-1
------------------------------------- Out of release -------------------------------------
------------------------------------------------------------------------------------------
Tasks in Jira: 8
Tasks in git: 7
Tasks without commit: 1
Tasks out of release: 0
````
Если в журнале измений git-репозитория для задачи найден соответсвтующий коммит, напротив задачи отображается хэш коммита, если коммит не найден - прочерк <code>--------</code>

Дополнительно для каждой задачи выводится ее статус и линк для быстрого перехода к задаче.

Также может быть отображена отдельная группа задач, для которых найдены коммиты в git, но эти задачи отсутствуют в релизе Jira 

Пример
```bash
python main.py http://147.45.104.169/rnd/gitcheck 1.0.0 1.1.0 "Git Check" "1.1.0" 
```
Вывод скрипта (см. задачу в секции Out of Release)
```bash
--------------------------------------- In release ---------------------------------------
JG-12 df121a44   Готово               https://quick-order.atlassian.net/browse/JG-12
JG-11 3c55fd04   Готово               https://quick-order.atlassian.net/browse/JG-11
JG-10 3c55fd04   Готово               https://quick-order.atlassian.net/browse/JG-10
JG-9  d3a43276   Готово               https://quick-order.atlassian.net/browse/JG-9
------------------------------------- Out of release -------------------------------------
JG-13 58a536e9   Готово               https://quick-order.atlassian.net/browse/JG-13
------------------------------------------------------------------------------------------
Tasks in Jira: 4
Tasks in git: 5
Tasks without commit: 0
Tasks out of release: 1
```

## Особенности запуска скрипта под Windows из bat файлов

Bat-файл должен быть в кодировке utf-8 и в первой строке должна быть команда изменения кодировки

Пример bat-файла

```bash
chcp 65001 > nul
D:\work\python\PycharmProjects\gitcheck\venv\Scripts\python.exe d:\work\python\PycharmProjects\gitcheck\main.py http://147.45.104.169/rnd/gitcheck 0.0.0 1.0.0 "Git Check" "1.0.0" 
```
