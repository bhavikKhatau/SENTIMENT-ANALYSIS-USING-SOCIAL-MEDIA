from neattext import clean_text
from googletrans import Translator,LANGUAGES

translator = Translator()


def translato(tweets):
    lis = []
    for i in tweets:
        try:
            if translator.detect(i).lang != "en":
                print(LANGUAGES[translator.detect(i).lang])
                i = translator.translate(i)
                i = i.text
        except Exception as e:
            print(i)
            print(e)
        lis.append(i)
    return lis


def clean(tweets):
    lis = []
    for i in tweets:
        i = clean_text(i, urls=True)
        i = clean_text(i, puncts=True, stopwords=True, emails=True, numbers=True, emojis=True,
                       special_char=True, phone_num=True)
        i = i.strip()
        lis.append(i)
    return lis


def clean_own_text(own_text):
    try:
        if translator.detect(own_text).lang != "en":
            print(translator.detect(own_text).lang)
            own_text = translator.translate(own_text)
            own_text = own_text.text
    except Exception as e:
        print(own_text)
        print(e)
    own_text = clean_text(own_text, urls=True)
    own_text = clean_text(own_text, puncts=True, stopwords=True, emails=True, numbers=True, emojis=True,
                          special_char=True, phone_num=True)
    return own_text.strip()
