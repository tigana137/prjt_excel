from bs4 import BeautifulSoup as bs
from bidict import bidict


class CustomError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


# [l ids l yelzmhom ytbadlou] : actual id fil db
sids_to_replace = bidict({"842911": "842811",
                          "842913": "842813",
                          "842922": "842822",
                          "842923": "842823",
                          "842924": "842824",
                          "842912": "842812",
                          "842914": "842814"
                          })


# tna7i l repetition t3 l chadda w tfas5 l soukoun, fat7a, kasra, tajwid,dhama, kasrtin, fat7tin, dhamtin
def get_clean_name(name: str):
    soukoun = 'ْ'
    fat7a = 'َ'
    fat7tin = 'ً'
    kasra = 'ِ'
    kasrtin = 'ٍ'
    tajwid = 'ـ'
    dhama = 'ُ'
    dhamtin = 'ٌ'

    bullshit = [soukoun, fat7a, kasra, tajwid,
                dhama, kasrtin, fat7tin, dhamtin]

    clean_name = ''
    for i in range(len(name)):
        if name[i] == "ّ" and clean_name == "":  # e.g if awil 7rouf ybdew chadda bark
            continue
        if name[i] == "ّ" and name[i-1] == "ّ" and i > 0:
            continue

        if name[i] not in bullshit:
            clean_name += name[i]

    return clean_name



def get_url_return_soup(url:str,request,decode:bool=True):
    response = request.get(url)
    
    soup = bs(response.content.decode(
        encoding='utf-8', errors='ignore'), 'html.parser')
    
    return soup



def post_url_return_soup(url:str,payload,request,decode:bool=True):
    response = request.post(url=url, data=payload)

    soup = bs(response.content.decode(
            encoding='utf-8', errors='ignore'), 'html.parser')
    
    return soup


def get_dre_id_from_select_element(soup:bs):
    dre_select_elm = soup.find('select', {'name': 'code_dre'})
    options = dre_select_elm.findAll('option')

    if len(options) != 2:  # ~ lezmhm nrmlmnt l kol zouz loula kil ---- w b3d l weileya chouf ken le nik errur or somethn
        raise CustomError("erreur 5atr l select nrmlmnt feha zouz loula kil ---- w b3d l weileya l kahaw ")


    
    dre = options[1]['value']
    return dre



def check_if_sid_need_to_be_replaced(sid:str,etatiq=False,prive=False):
    if sid=="" or sid =="0":
        raise CustomError("famma sid equal espace or 0 ezebi f select t3 قائمة التلاميذ (من الثانية إلى السادسة)" + ("etatiq" if etatiq else "privee") )

    if sid in sids_to_replace.keys():
        return sids_to_replace[sid]
    
    return sid 








def get_clean_name_for_school_name(school_name,etatique=False,prive=False):
    if school_name=='':
        raise CustomError("school_name je fera8 k jit te5ou fih mil options winti t updati f schools_data defq ")
    
    if etatique:
        return school_name.replace('م.إ.  ', '').replace('م.إبت. ', '').replace('م.إ. ', '').replace('المدرسة الابتدائية ', '')
    
    
    if prive:
        return school_name.replace('المدرسة الابتدائية الخاصة  ', '').replace('المدرسة الابتدائية الخاصة ', '')













