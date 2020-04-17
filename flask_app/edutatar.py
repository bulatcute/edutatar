import requests
from bs4 import BeautifulSoup as bs4


def login_edu(session, login, password):
    payload = {'main_login': login, 'main_password': password}
    url = 'https://edu.tatar.ru/logon'
    headers = {'Referer': url}
    session.post(url, data=payload, headers=headers)


def check_login(session):
    page = session.get('https://edu.tatar.ru')
    return 'Войти' not in page.text


def subjects_list(session):
    print('find facultatives')
    url = 'https://edu.tatar.ru'
    facs = session.get('https://edu.tatar.ru/student')

    facs_soup = bs4(facs.text, features="html.parser")

    ford = {}

    for li in facs_soup.find('ul', {'class': 'edu-list horizontal'}).find_all('li'):
        ford[li.find('a').text] =\
            url + li.find('a').get('href') + '/facultatives'
        print(li.find('a').text)
        print(url + li.find('a').get('href') + '/facultatives')
    print('found facultatives')


def find_facultative(session, pattern, subject_url):
    count = 1

    while True:
        print(count)

        page = session.get(f'{subject_url}/?page={count}')

        if 'Список пуст' in page.text:
            break

        for ul in bs4(page.text, features="html.parser").find_all('ul', {'class': 'blogs'}):
            for li in ul.find_all('li'):
                if pattern in li.find('span').text.lower():
                    print(li.find('a').text)
                    print(li.find('a').get('href'))
                    # Обучение детей с ОВЗ
                    # https://edu.tatar.ru/student/page379377.htm/facultatives
                    print()

        count += 1


def get_home_params(session):
    page = session.get('https://edu.tatar.ru')
    soup = bs4(page.text, features='html.parser')
    name = soup.find('table', {'class': 'tableEx'}).find(
        'tr').find_all('td')[1].find('strong').text
    img = soup.find('div', {'class': 'user-photo'}).find('img')
    if img:
        img = 'https://edu.tatar.ru' + img.get('href')
    else:
        img = None
    return {'name': name, 'avatar': img, }


def my_facultatives(session):
    url = 'https://edu.tatar.ru/user/subscriptions/facultatives'
    page = session.get(url)

    facultatives = {}

    soup = bs4(page.text, features="html.parser")
    content_panel = soup.find('div', {'class': 'content panel panel-default'})
    ul = content_panel.find('ul')

    for li in ul.find_all('li'):
        a = li.find('a')
        text = a.text
        text = text.replace('№', '')
        text = text.replace(' - ', ' ')
        text = text.replace('-', ' ')
        text = ' '.join([i.lower()
                         for i in text.split() if i.lower() != 'казань'])
        href = a.get('href')
        href = href.split('/')[-1]
        facultatives[href] = text.capitalize()

    return facultatives


def my_stars(session, term=''):
    if term:
        payload = {'term': f'{term}'}
        url = 'https://edu.tatar.ru/user/diary/term'
        headers = {'Referer': url}
        page = session.post(url, data=payload, headers=headers)
    else:
        page = session.get('https://edu.tatar.ru/user/diary/term')

    soup = bs4(page.text, features='html.parser')

    if not term:
        term = soup.find('select', {'id': 'term'}).find(
            'option', {'selected': 'selected'}).text[0]

    table = soup.find('table', {'class': 'table term-marks'})
    out = {}
    for tr in table.find('tbody').find_all('tr')[:-1]:
        tds = tr.find_all('td')
        subj = tds[0].text
        if 'ОБЖ' in subj:
            subj = 'ОБЖ'
        elif 'Музыка' in subj:
            subj = 'Музыка'
        elif 'Информатика' in subj:
            subj = 'Информатика'
        stars = [star.text for star in tds[1: len(tds) - 5] if star.text != '']
        if not stars:
            continue
        average = tds[len(tds) - 5].text
        total = tds[-1].text
        if total:
            total = total[-1]

        out[subj] = {'stars': stars, 'average': average, 'total': total}
    return [out, term]


def get_diary(session, url='https://edu.tatar.ru/user/diary/week'):
    r = session.get(url)
    day_code = {
        'mo': 'Понедельник',
        'tu': 'Вторник',
        'we': 'Среда',
        'th': 'Четверг',
        'fr': 'Пятница',
        'sa': 'Суббота'
    }
    soup = bs4(r.text, features='html.parser')
    days = soup.find_all('td', {'class': 'tt-days'})[1:]
    subjs = soup.find_all('td', {'class': 'tt-subj'})[1:]
    tasks = soup.find_all('td', {'class': 'tt-task'})[1:]
    marks = soup.find_all('td', {'class': 'tt-mark'})[1:]
    out = {}
    trs = soup.find_all('tr')

    for i in range(3):
        daydiv = days[i].find('div')
        day = day_code[daydiv.get('class')[0][-2:]] + \
            ' ' + daydiv.find('span').text
        value = []
        for j in range(6):
            subj = subjs[8*i + j].find('div').text
            value.append((subj, [task for task in tasks[8*i + j].find(
                'div').text.split('\n') if task], marks[8*i + j].find('div').text))
        out[day] = value

    wsc = soup.find('div', {'class': 'week-selector-controls'}).find_all('a')
    next_page = [ctrl.get('href')[42:]
                 for ctrl in wsc if ctrl.text == 'Следующая →']
    prev_page = [ctrl.get('href')[42:]
                 for ctrl in wsc if ctrl.text == '← Предыдущая']
    return [out, next_page, prev_page]


def facultative_info(session, index):
    to_delete = [
        'гимназия',
        'лицей',
        'школа',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        '№',
        'г.',
        'казань',
        '-',
        'классы',
        'класс'
    ]
    url = f'https://edu.tatar.ru/facultative/index/{index}'
    r = session.get(url)
    soup = bs4(r.text, features='html.parser')
    left = soup.find('div', {'class': 'left'})

    name = left.find('div', {'class': 'community_title'}).find(
        'div').find('p').find('strong').text[13:-1].lower()
    for i in to_delete:
        name = name.replace(i, '')
    name = ' '.join(name.split()).capitalize()

    teacher_a = soup.find('div', {'class': 'right'}).find('p').find('a')
    teacher = {f'https://edu.tatar.ru{teacher_a.get("href")}': teacher_a.text}

    description = []
    for p in left.findChildren(recursive=False)[1:]:
        if p.name == 'hr' or 'Прикрепленные файлы:' in p.text:
            break
        description.append(p.text.strip())


    try:
        attached_files = {f'https://edu.tatar.ru{a.get("href")}': a.text for a in left.find(
            'div', {'class': 'attached_files'}).find('ul').find_all('a')}
    except:
        attached_files = None

    com_div = left.find('div', {'class': 'comments'})
    comments = [mess for mess in com_div.find_all(
        'div', {'class': 'mess'})] if com_div else None

    if comments:
        for i in range(len(comments)):
            mess = comments[i]
            author = mess.find('div', {'class': 'user'}).find('a').find('strong').text
            date = mess.find('div', {'class': 'user'}).find('span').text
            paragraphs = mess.find(
                'div', {'class': 'mtext'}).find('div').text
            files_list = [li.find('a') for li in mess.find('div', {'class': 'mtext'}).find(
                'div', {'class': 'attached_files'}).find('ul').find_all('li')] if mess.find(
                    'div', {'class': 'mtext'}).find('div', {'class': 'attached_files'}) else None
            files = {
                f'https://edu.tatar.ru{a.get("href")}': a.text for a in files_list
            } if files_list else None
            comments[i] = {'author': author, 'date': date, 'text': paragraphs, 'files': files}

    return {
        'name': name,
        'teacher': teacher,
        'description': description,
        'files': attached_files,
        'comments': comments,
    }
