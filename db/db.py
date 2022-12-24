from pymongo import MongoClient
import pymongo
import json
import CambridgeDictionaryAPI as cDict
import config

CONNECTION_STRING = config.DATABASE_URL
client = MongoClient(CONNECTION_STRING)


def add_word(word, userid):
    try:
        dbname = client['users']
        collection_name = dbname[str(userid)]
        collection_name.insert_many([word])
    except:
        pass


def read_words(userid):
    try:
        dbname = client['users']
        collection_name = dbname[str(userid)]
        words = collection_name.find()
        # print(words)
        # for data in words:
        #    print(data.get(list(data.keys())[1])[0].get("word"))
        return words
    except:
        pass
