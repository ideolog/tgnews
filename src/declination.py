#this is temporary file to generate declinations for RU words in our dictionaries
import json, requests, time


url = "https://ws3.morpher.ru/russian/declension"

lang = 'ru'
category = 'todo_society'

dictionary_file = open("./src/{0}_{1}.txt".format(category, lang))
words = {}

for word in dictionary_file.read().split("\n"):
    word = word.lower()
    params = dict(
        s=word,
        format="json",
        # token= #Не обязателен. Подробнее: http://morpher.ru/ws3/#authentication
    )

    response = requests.get(url=url, params=params)
    data = json.loads(response.text)

    print(data.get('И'))
    print(data.get('Р'))
    print(data.get('Д'))
    print(data.get('В'))
    print(data.get('Т'))
    print(data.get('П'))
    print(data.get('множественное').get('И'))
    print(data.get('множественное').get('Р'))
    print(data.get('множественное').get('Д'))
    print(data.get('множественное').get('В'))
    print(data.get('множественное').get('Т'))
    print(data.get('множественное').get('П'))
    time.sleep(0.3)

dictionary_file.close()

