import json
import re
import requests
from lxml import html

import config

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) Gecko/20100101 Firefox/45.0'
}

DICTIONARY_URL = config.DICTIONARY_URL


def word_finder(word):
    """
    :param word:
    :return:

    id_word - cambridge id's word
    id_level - meanings of word
    map_id_level - just converted id_level
    help_code - cambridge codes
    speech_type - type of speech
    map_id_level -

    refactor this code bruh
    """

    url = f'{DICTIONARY_URL}{word}'
    r = requests.get(url, headers=headers)
    tree = html.fromstring(r.content)

    id_word = re.findall('data-wl-senseid="(.*?)"', r.text)
    id_level = re.findall('class="cid" id="cldru-(.*?)"', r.text)
    # phrase-title dphrase-title
    raw_words = tree.xpath('//*[@class="hw dhw"]/text()')
    raw_words_add = tree.xpath('//*[@class="phrase-title dphrase-title"]//text()')
    wwwords = tree.xpath('//*[@class="dsense_h"]//text()')
    speech_type = tree.xpath('//*[@class="pos dpos"]/text()')
    help_code = tree.xpath('//*[@class="gram dgram"]//*[@class="gc dgc"]//text()')
    ex_word = tree.xpath('//*[@class="examp dexamp"]//*[@class="eg deg"]//text()')
    example_word_raw = re.findall('<span class="eg deg">(.*?)</span>',
                                  r.text)  # //*[@data-wl-senseid="%s"]//*[@class="examp dexamp"]
    example_word = []
    for ex in example_word_raw:
        example_word.append(re.sub('<.*?>', '', ex))

    # print(''.join(tree.xpath('//*[@data-wl-senseid="%s"]//*[@class="examp dexamp"]//text()' % id_word[0])))

    level = []
    for i in id_word:
        level.append((tree.xpath('//*[@data-wl-senseid="%s"]//*[@class="def-info ddef-info"]//text()' % i))[0])
    id_level = list(filter(lambda x: len(x) == 3, id_level))
    map_id_level = []
    for i in id_level:
        map_id_level.append((int(re.sub('-', '', i))) % 10)

    norm_word = []
    count = 0
    if(len(raw_words_add) + len(raw_words) != len(map_id_level)):
        for i in range(len(map_id_level)):
            norm_word.append(raw_words[0])
    else:
        for i in range(len(id_level)):  # Combine words
            if map_id_level[i] == 1:
                norm_word.append(raw_words[count])
                count += 1
            else:
                if len(raw_words_add) == 0:
                    norm_word.append(raw_words[0])
                else:
                    print(map_id_level[i])
                    norm_word.append(raw_words_add[map_id_level[i] - 2])
    data = {'_id': id_word[0][:-3][3:]}
    for speech_ind in range(len(speech_type)):  # generate dict
        speech = speech_type[speech_ind]
        data[speech] = []
        x = len(id_word)
        for i in range(x):
            if int(id_level[i][0]) == speech_ind + 1:
                data[speech].append({
                    'id': id_level[i],
                    'level': level[i],
                    'word': norm_word[i],
                    'meaning': ''.join(tree.xpath('//*[@data-wl-senseid="%s"]//*[@class="def ddef_d db"]//text()'
                                                  % id_word[i])),
                    'russian': tree.xpath('//*[@data-wl-senseid="%s"]//*[@class="trans dtrans dtrans-se "]/text()'
                                          % id_word[i])[0][:-1],
                    'example': ''.join(tree.xpath('//*[@data-wl-senseid="%s"]//*[@class="examp dexamp"]//text()'
                                                  % id_word[i]))
                })
    # data["examples"] = []
    # with open("cache/words-tests.json", 'w', encoding='utf-8') as outfile:
    #    json.dump(data, outfile, indent=4, ensure_ascii=False)

    return data


def word_checker(word):
    url = config.SEARCH_URL + word
    r = requests.get(url, headers=headers)
    tree = html.fromstring(r.content)

    word_list = tree.xpath('//*[@class="hul-u"]//li//text()')
    word_link = tree.xpath('//*[@class="hul-u"]//@href')
    word_list = [x for x in word_list if x.find("\n") != 0]
    if ' in English–Russian\n                                    ' in word_list:
        return True
    else:
        wls = len(word_link)
        word_link = list(filter(lambda x: x.find('https://') != -1, word_link))
        wls -= len(word_link)
        del word_list[0:wls * 2]
        return [word_list, word_link]