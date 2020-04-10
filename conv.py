# Импортируем необходимые библиотеки
import requests
from bs4 import BeautifulSoup as bs
import json
from lxml import etree
from telegram import ParseMode
from telegram.ext import CallbackContext
from telegram import Update
from telegram.ext import Updater
from telegram.ext import MessageHandler
from telegram.ext import Filters




'''Описание переменных программы
headers и proxy: значения которые необходимо передать сайту
'''
headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
           'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 YaBrowser/20.2.0.1043 Yowser/2.5 Safari/537.36'}
proxy = {'htpp': 'htpp://95.141.193.14:80', 'htpp://46.235.53.26:3128'
         'htpps':'htpp://95.141.193.14:80'}

'''
функция check_url() служит для проверки ссылки
-------------------------------------
Описание переменных для функции
-------------------------------------
формальный парматер функции
link: введённая пользователем ссылка
-------------------------------------
Результат функции
NewID: ID товара (str)
T: Переменная указывает на валидность сссылки (bool)
soup: HTML код страницы (bs)
session: сессия
-------------------------------------
Локальные переменные функции
i: счётчик(int)
'''
def check_url(link):
    link = str(link)
    link = link.strip()
    if ('https://' or 'http://') not in link:
        link = ''.join(['https://', link])
    session = requests.Session() #создаём сессию
    if ('asos' in link):
        request = session.get(link, headers=headers) # отправим GET()-запрос на сайт и сохраним полученное в переменную 'request'
        if (request.status_code == 200): # Проверяем состояние запроса
            soup = bs(request.content, 'lxml') #  Создаем сам объект , передаем в него наш код страницы (html)

            id = soup.find('link', attrs={'rel': 'alternate'})['href'] # Получаем ссылку со старницы
            if 'prd' in id: # Проверяем ссылку
                T = True
                i = len(id) - 1
                newID = ''
                while '/' not in newID: # Запускаем цикл для извлечения ID товара из ссылки
                    newID += id[i]
                    i -= 1
                newID = newID[len(newID) - 2::-1] # Получаем ID товара
            else:
                newID = ''
                T = False
        else:
            soup = 'None'
            T = False
    else:
        T = False
        newID = 'None'
        soup = 'None'

    return newID, T, soup, session
'''
функция get_all_urls() служит для получения всех ссылок на товар
-------------------------------------
Описание переменных для функции
-------------------------------------
формальный парматер функции
id: ID товара (str)
-------------------------------------
Результат функции
all_urls: ссылки на товары (list)
-------------------------------------
Локальные переменные функции
asos: переменная для конструкции ссылки (str)
valeut: список валют (list)
'''
def get_all_urls(id):
    asos = 'asos.su/'
    all_urls = []
    valuet = ['RUB', 'GBP', 'AUD', 'TWD', 'HKD', 'ILS', 'CNY', 'TRR', 'EUR', 'SEK', 'CHF', 'EEG']
    for i in range(len(valuet)):
        url = ''.join([asos, valuet[i], id])
        all_urls.append(url)
    return all_urls
'''
функция get_urlsJS() служит для проверки ссылки
-------------------------------------
Описание переменных для функции
-------------------------------------
формальный парматер функции
id: ID товара (str)
-------------------------------------
Результат функции
likJs: список ссылок, необходимых для парсинга стоимости (list)
valuet: список валют (list)
-------------------------------------
Локальные переменные функции
regions: список стран (list)
'''
def get_urlsJs(id):
    regions = ['RU', 'COM', 'AU', 'ROW', 'ROW', 'ROW', 'ROW', 'ROW', 'DE', 'SE', 'FR', 'ROE']
    valuet = ['RUB', 'GBP', 'AUD', 'TWD', 'HKD', 'ILS', 'CNY', 'RUB', 'EUR', 'SEK', 'CHF', 'GBP']
    linksJs = []
    for i in range(len(regions)):
        NewLinks = ''.join(['https://www.asos.com/api/product/catalogue/v3/stockprice?productIds=', id, '&store=',  regions[i], '&currency=',  valuet[i], '&keyStoreDataversion=ekbycqu-23'])
        linksJs.append(NewLinks)
    return linksJs, valuet
'''
функция asos_parser_bot() служит для получения необходимой информации о товаре
-------------------------------------
Описание переменных для функции
-------------------------------------
формальный парматер функции
likJs: список ссылок, необходимых для парсинга стоимости (list)
all_urls: ссылки на товары (list)
valuet: список валют (list)
session: сессия
soup: HTML код страницы пользователя
-------------------------------------
Результат функции
goods: список словарей с данными о товаре в разных странах
-------------------------------------
Локальные переменные функции
conuntryList: список стран (list)
soupJS: HTML код страницы со стоимостью товара (bs)
name: Название товара (str)
root: переменная для нахождения стомости
price: стоимость товара (float)
country: страна сайта (str)
'''
def asos_parser_bot(linksJs, all_urls, valuet, session, soup):
    goods = []
    conuntryList = ['RU', 'GB', 'AU', 'TW', 'HK', 'IL', 'CN', 'TR', 'DE', 'SE', 'FR', 'EE']
    for i in range(len(all_urls)):

        country = conuntryList[i]

        requestPrice = session.get(linksJs[i], headers=headers) # отправим GET()-запрос на сайт и сохраним полученное в переменную 'requestPrice'
        soupJs = bs(requestPrice.content, 'lxml') # HTML код страницы
        soupJs = str(soupJs) # преобразуем bs в str
        root = etree.fromstring(soupJs)
        price = json.loads(root.xpath('.//p')[0].text)
        price = price[0]['productPrice']['current']['value'] # находим значение стоимости

        if i == 1: # создадим условие для добавления названия товара в список с индексом 1.
            name = soup.find('h1').text  # находим название в HTML коде
            goods.append({'name': name})

        goods.append({
            'country': country,
            'price': float(price),
            'valuet': valuet[i],
            'url': all_urls[i]
            })

    return goods
'''
функция get_cours() служит для получения курса валют
-------------------------------------
Описание переменных для функции
-------------------------------------
формальный парматер функции
headers: заголовки авторизации
session: сессия
Результат функции
cours: список с курсом валют (list)
-------------------------------------
Локальные переменные функции
url: ссылка на сайт, с которого берётся курс валют (str)
request: запрос на сайт с курсом
valuet: список валют (list)
i: счтётчик цикла (int)
a: курс (float)
'''
def get_cours(headers, session):
    url = 'https://pokur.su/gbp/'
    request = session.get(url, headers=headers) # отправляем запрос
    soup = bs(request.content, 'lxml') # получаем HTML код
    cours = []
    valuet = ['rub', 'aud', 'twd', 'hkd', 'ils', 'cny', 'eur', 'sek', 'chf']
    for i in range(len(valuet)):
        link = ''.join(['/gbp/', valuet[i], '/1/']) # конструируем ссылку
        a = soup.find('a', attrs={'href': link}).text # находим курс текущей валюты
        if ',' in a:
            a = float(a.replace(',', '.')) # редактируем и переобразуем значение курса
        cours.append({
            valuet[i].upper(): a
        })
    return cours
'''
функция result() служит для конвертирования валют в рубли
-------------------------------------
Описание переменных для функции
-------------------------------------
формальный парматер функции
goods: список с данными о товаре (list)
cours: список с курсом валют (list)
Результат функции
goods: обновлённый список с данными о товаре (list)
-------------------------------------
Локальные переменные функции
val: значение курса текущей валюты (float)
pr: значение стоимости товара в валюте (float)
rub: курс рубля к фунту стерлингов (float)
i: счтётчик цикла (int)
j: счётчик цикла (int)
res: конвертация валюты в рубли
'''
def result(cours, goods):
    for i in range(2, len(goods)):
        val = goods[i].get('valuet')
        pr = goods[i].get('price')
        rub = cours[0].get('RUB')
        if val == 'GBP':
            res = float('{:.2f}'.format(pr * rub)) # конвертируем
        else:
            for j in range(len(cours)):
                cr = cours[j].get(val)
                if cr != None:
                    a = cr
                    res = float('{:.2f}'.format(pr / a * rub))
        goods[i]['rub'] = res
    goods[0]['rub'] = goods[0].get('price')
    return goods
'''
функция result() служит для сортировки информации о товаре в порядке убывания цены
-------------------------------------
Описание переменных для функции
-------------------------------------
формальный парматер функции
goods: список с данными о товаре (list)
Результат функции
goods: отсортированный список с данными о товаре (list)
name: навазние товара (str)
-------------------------------------
Локальные переменные функции
i: счтётчик цикла (int)
j: счётчик цикла (int)
'''
def sort(goods):
    name = str(goods[1].get('name'))
    goods.pop(1) # удаляем ключ с названием товара
    for i in range(len(goods)):
        for j in range(len(goods)-i-1):
            if goods[j].get('rub') < goods[j+1].get('rub'):
                goods[j], goods[j+1] = goods[j+1], goods[j]
    return goods, name

'''
функция prinT() служит для конструирования сообщения с результатом для пользователя
-------------------------------------
Описание переменных для функции
-------------------------------------
формальный парматер функции
goods: список с данными о товаре (list)
Результат функции
s: результат, который будет отправлять пользователю (str)
-------------------------------------
Локальные переменные функции
i: счтётчик цикла (int)
k: счётчик для нахождения предложения с минимальной ценой (int)
'''
def prinT(goods,name):
    s = '*'+name+'*'+'\n'
    bl = ' '*24
    for i in range(len(goods)):
        s += ''.join([f'\n {goods[i].get("country")} \t\t {goods[i].get("rub")} \t\t ✔️{goods[i].get("price"):}  ({goods[i].get("valuet")}): \n {bl} {goods[i].get("url")}'])
    s += '👈🏻'
    res = goods[0].get('rub')
    k = 0
    for i in range(len(goods)-1):
        if res > goods[i+1].get('rub'):
            res = goods[i+1].get('rub')
            k = i + 1
    content = ['',
               '',
               f'☝🏻Лучшее предложение в {goods[k].get("country")} - {res} руб, оплата в {goods[k].get("valuet")}.',
               '(Все цены в сравнении сконвертированы в RUB).🤟🏻',
                'Экономь ещё больше с официальными промокодами ASOS👍🏻',
               '',
               '🔹Обратная связь: [telegram](http://tgram.su/xexeel)']

    s += '\n'.join(content)
    return s

'''
функция get_url() служит для получения ссылки на товар от пользователя, обработки команд и оправки сообщений пользователю
-------------------------------------
Описание переменных для функции
-------------------------------------
формальный парматер функции
update: действия, которые совершил бот или пользователь
context: 
-------------------------------------
Локальные переменные функции
text: сообщение, которое нужно отправить пользователю (list)
'''
def get_url(update: Update, context: CallbackContext):
    link = update.effective_message.text # получаем сообещние от пользователя
    if link == '/start': # обработка команды '/start'
        text = ['Привет!',
                '',
                'Я был создан для помощи в покупках на ASOS.COM.',
                'Знаешь ли ты, что один и тот же товар',
                'имеет разные цены на сайтах ASOS, относящихся к разным странам',
                'Я сканирую цены на всех ASOS-сайтах',
                'и сравниваю их в выбраной валюте.',
                'Узнай, где продукт имеет самую низкую цену, и в какой валюте',
                'выгоднее всего совершить покупку!',
                '',
                'Отправь мне ссылки на товары, цены на которые хочешь сравнить!',
                '',
                'Читай инструкцию [👉🏻здесь👈🏻](https://teletype.in/@edima/R5BateM_H)',
                '',
                'Контакты:',
                '[telegram](http://tgram.su/xexeel)',
                '[vk](https://vk.com/e_dima)',
                '',
                '']
        # отравляем сообщение пользователю
        update.message.reply_text(
            text='\n'.join(text),
            parse_mode=ParseMode.MARKDOWN, # выделяем текст жирным шрифтом
        )
    elif link == '/help': # обработка команды '/help'
        text = ['В случаии возникновении проблем читайте FAQ ',
                '[👉🏻здесь👈🏻](https://teletype.in/@edima/R5BateM_H)',
                '',
                'Если вы не смогли решить свою пробелму, свяжитесь со мной',
                '',
                'Контакты:',
                '🔹 [telegram](http://tgram.su/xexeel)',
                '🔹 [vk](https://vk.com/e_dima)',
                '',
                '']
        # отправляем сообщение пользоавтелю
        update.message.reply_text(
            text='\n'.join(text),
            parse_mode=ParseMode.MARKDOWN, # выделяем жирным шрифтом текст
        )
    else:
        id, T, soup, session = check_url(link,) # проверяем сссылку и получаем необходимые параметры
        if T: # проверяем валидность ссылки
            update.message.reply_text(
                text='Найдена 1 позиция. Подождите, идет поиск цен...'
            )
            all_urls = get_all_urls(id) # получаем список всех ссылок на товар
            linksJs, valuet = get_urlsJs(id) # получаем список цен на товар и список валют
            goods = asos_parser_bot(linksJs, all_urls,valuet, session, soup) # получаем необходимыю информацию о товаре
            cours = get_cours(headers, session) # получаем курс
            result(cours, goods) # конвертируем вcё в рубли
            goods, name = sort(goods) # сортируем в порядке убывания цены
            end = prinT(goods,name) # конструируем сообщение для пользователя
            # отправляем конечный результат пользователю
            update.message.reply_text(
                text=end,
                parse_mode=ParseMode.MARKDOWN, # выделяем жирным шрифтом название товара
               )
        else:
            # отправляем сообщение об ошибки
            update.message.reply_text(
                text='Ошибка. Не могу определить эту ссылку.'
            )
'''
функция main() служит для запуска телеграм бота
-------------------------------------
Описание переменных для функции
------------------------------------
TG_TOKEN: токен телеграм бота
'''
def main():
    TG_TOKEN = '1148579186:AAHnPRrZ8INOQVZkDErcdGlm5OLGXxQ9Q-E' # Токен бота
    updater = Updater(
        token=str(TG_TOKEN),
        use_context=True,
    )
    updater.dispatcher.add_handler(MessageHandler(Filters.text, callback=get_url)) # запускаем функцию get_url
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main() # запускаем код
