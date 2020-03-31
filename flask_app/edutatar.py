from bs4 import BeautifulSoup as bs4


def login_edu(session, login, password):
    payload = {'main_login': login, 'main_password': password}
    url = 'https://edu.tatar.ru/logon'
    headers = {'Referer': url}
    session.post(url,
                 data=payload,
                 headers=headers)
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
    soup = bs4(page.text)
    name = soup.find('table', {'class': 'tableEx'}).find('tr').find_all('td')[1].find('strong').text
    img = soup.find('div', {'class': 'user-photo'}).find('img')
    if img:
        img = 'https://edu.tatar.ru' + img.get('href')
    else:
        img = None
    return {'name': name, 'avatar': img,}


def my_facultatives(session):
    url = 'https://edu.tatar.ru/user/subscriptions/facultatives'
    page = session.get(url)

    facultatives = {}

    soup = bs4(page.text, features="html.parser")
    content_panel = soup.find('div', {'class': 'content panel panel-default'})
    ul = content_panel.find('ul')

    for li in ul.find_all('li'):
        a = li.find('a')
        facultatives[a.get('href')] = a.text

    return facultatives
