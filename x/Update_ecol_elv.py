<<<<<<< HEAD
<<<<<<< HEAD
import re
import time
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
from bidict import bidict

from django.db import IntegrityError, transaction
from requests.exceptions import ChunkedEncodingError
from rest_framework.response import Response
from x.functions import check_if_sid_need_to_be_replaced, get_clean_name, get_clean_name_for_school_name, get_dre_id_from_select_element, get_url_return_soup, post_url_return_soup


from x.models import AdminEcoledata, AdminElvs, Del1,  Dre, Elvsprep
from pprint import pprint

# [l ids l yelzmhom ytbadlou] : actual id fil db
sids_to_replace = bidict({"842911": "842811",
                          "842913": "842813",
                          "842922": "842822",
                          "842923": "842823",
                          "842924": "842824",
                          "842912": "842812",
                          "842914": "842814"
                          })




# bulkcreate l data t3 mders f admin ecole data prive w etatik
def create_AdminEcole_data(request2: requests.Session):

    ############# etatiq #############

    soup = get_url_return_soup(
        url="https://suivisms.cnte.tn/ministere/index.php?op=inscprim&act=find_etab", request=request2,decode=True)

    dre = get_dre_id_from_select_element(soup)

    existing_sids_in_db = set(AdminEcoledata.objects.filter(
        dre_id=dre).values_list('sid', flat=True))

    soup = get_url_return_soup(
        url="https://suivisms.cnte.tn/ministere/inscprim/getetab_choix.php?id="+dre, request=request2,decode=True)

    options = soup.find_all('option')

    admin_ecoles_array = []
    new_ecoles_to_add_their_Levelstat = []

    for option in options:
        sid = option['value']
        sid = check_if_sid_need_to_be_replaced(sid, etatiq=True)

        school_name = option.get_text()
        school_name = get_clean_name_for_school_name(
            school_name, etatique=True)

        ecole = AdminEcoledata(
            sid=sid,
            school_name=school_name,
            dre_id=dre,
            del1_id=sid[:4],
        )

        if int(sid) not in existing_sids_in_db:  # create Levelstat instances for the levels
            print('New ecole !! :  ' + school_name + sid)
            new_ecoles_to_add_their_Levelstat.append(ecole)

        admin_ecoles_array.append(ecole)

    ############# privee #############

    soup = get_url_return_soup(
        url="https://suivisms.cnte.tn/ministere/prive/getetab_prive_prim.php?id="+dre, request=request2,decode=True)

    options = soup.find_all('option')

    for option in options:

        sid = option['value']
        sid = check_if_sid_need_to_be_replaced(sid, prive=True)

        school_name = option.get_text()
        school_name = get_clean_name_for_school_name(school_name, prive=True)

        ecole = AdminEcoledata(
            sid=sid,
            school_name=school_name,
            dre_id=dre,
            del1_id=sid[:4],
        )
        admin_ecoles_array.append(ecole)

    with transaction.atomic():
        AdminEcoledata.objects.bulk_create(
            admin_ecoles_array, batch_size=100, ignore_conflicts=False, update_conflicts=True, update_fields=["school_name"])
        for ecole in new_ecoles_to_add_their_Levelstat:
            ecole.create_levelstats()
        print("updating AdminEcoledata done succesfully")

    return Response(True)


# ~ zid comparision bin l sids l 5dhithom welli 3ndk famch zeyed walla ne9s
# ~ les preivees in all dre 3ndhom **98 del ?
# bulkcreate lil AdminElvs2 l request 5dheha mil Verify capatcha 5atr lezmn bypass heki bch tod5al donc torbtha m3aha in case of ist3mel
def create_AdminElvs(request2: requests.Session):

    def is_valid_date_string(date_string):
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    # privee
    sids = AdminEcoledata.objects.filter(
        del1_id=8498).values_list('sid', flat=True)

    for sid in sids:
        elvs_array = []
        url = "https://suivisms.cnte.tn/ministere/index.php?op=prive&act=list_eleve_prive_prim"
        payload = {
            "code_dre": "84",
            "code_etab": sid,
            "btenv": "بحث"
        }
        response = request2.post(url=url, data=payload)

        soup = bs(response.content.decode(
            encoding='utf-8', errors='ignore'), 'html.parser')

        rows = soup.find_all('tr', {'height': '30', 'bgcolor': '#B9FFB9'})

        # print(rows[0].find_all('td', {'align': 'center'}))

        for tr in rows:
            data = tr.findAll('font')
          #  temp_uid = data[1].text.strip()
            uid = data[2].text.strip()
            if uid == "" or uid == "0" or not uid.isdigit():
                print('fama uid egal 0 wall "" :', end='')
                print(uid)
                continue
            nom_prenom = data[3].text.strip()
            nom_pere = data[4].text.strip()
            date_naissance = data[5].text.strip()
            elv = AdminElvs(
                uid=uid,
                nom_prenom=get_clean_name(nom_prenom),
                nom_pere=get_clean_name(nom_pere),
                date_naissance=date_naissance if is_valid_date_string(
                    date_naissance) else None,
                ecole_id=sid,
                #   temp_uid=temp_uid
            )
            elvs_array.append(elv)

        try:
            AdminElvs.objects.bulk_create(elvs_array, batch_size=100, ignore_conflicts=False, update_conflicts=True, update_fields=[
                                          "nom_prenom", "nom_pere", "date_naissance", "ecole_id"])
            print(str(sid)+' : good ' + str(len(elvs_array)) + ' elvs')

        except IntegrityError as e:
            print("------------")
            print("errerur with this : " + str(sid))
            print(f"IntegrityError: {e}")
            print("------------")

    # etatik

    response = request2.get(
        "https://suivisms.cnte.tn/ministere/index.php?op=inscprim&act=find_etab")
    soup = bs(response.content.decode(
        encoding='utf-8', errors='ignore'), 'html.parser')
    dre_select_elm = soup.find('select', {'name': 'code_dre'})

    options = dre_select_elm.findAll('option')
    dre = '84'  # ~
    existing_sids = set(AdminEcoledata.objects.filter(
        dre_id=dre).values_list('sid', flat=True))
    if len(options) == 2:  # ~ lezmhm nrmlmnt l kol zouz loula kil ---- w b3d l weileya chouf ken le nik errur or somethn
        dre = options[1]['value']
    response = request2.get(
        "https://suivisms.cnte.tn/ministere/inscprim/getetab_choix.php?id="+dre)
    select_element = response.content.decode(encoding='utf-8', errors='ignore')
    pattern = r'value="(\d+)"'
    sids = re.findall(pattern, select_element)

    for sid in sids:
        print("currently traiment of : " + str(sid))
        elvs_array = []
        url = "https://suivisms.cnte.tn/ministere/index.php?op=inscprim&act=list_eleve"
        payload = {
            "code_dre": "84",
            "code_etab": sid,
            "btenv": "بحث"
        }

        response = request2.post(url=url, data=payload)

        soup = bs(response.content.decode(
            encoding='utf-8', errors='ignore'), 'html.parser')

        rows = soup.find_all('tr', {'height': '30', 'bgcolor': '#a9edca'})

        for tr in rows:
            data = tr.findAll('font')

            uid = data[1].text.strip()
            if uid == "" or uid == "0" or not uid.isdigit():
                continue
            nom_prenom = data[2].text.strip()
            nom_pere = data[3].text.strip()
            date_naissance = data[4].text.strip()
            elv = AdminElvs(
                uid=uid,
                nom_prenom=get_clean_name(nom_prenom),
                nom_pere=get_clean_name(nom_pere),
                date_naissance=date_naissance if is_valid_date_string(
                    date_naissance) else None,
                ecole_id=int(sid) if str(
                    sid) not in sids_to_replace.keys() else sids_to_replace[sid]
            )
            elvs_array.append(elv)

        try:
            AdminElvs.objects.bulk_create(elvs_array, batch_size=100, ignore_conflicts=False, update_conflicts=True, update_fields=[
                                          "nom_prenom", "nom_pere", "date_naissance", "ecole_id"])
            print(str(sid)+' : good ' + str(len(elvs_array)) + ' elvs')

        except Exception as e:
            print("------------")
            print("erreur with this : " + str(sid))
            print(f"Exception : {e}")
            print("------------")

    return Response(True)


def create_Elvsprep(request2: requests.Session):
    # request2.get(
    #     "https://suivisms.cnte.tn/ministere/index.php?op=preparatoire&act=inscrit_find")
    # response = request2.get(
    #     "https://suivisms.cnte.tn/ministere/preparatoire/getetabprint.php?id=84")
    soup = get_url_return_soup(
        url="https://suivisms.cnte.tn/ministere/index.php?op=preparatoire&act=inscrit_find", request=request2,decode=True)

    dre = get_dre_id_from_select_element(soup)

    select_element =str( get_url_return_soup(
        url="https://suivisms.cnte.tn/ministere/preparatoire/getetabprint.php?id="+dre, request=request2,decode=True))

    pattern = r'value="(\d+)"'
    sids = re.findall(pattern, select_element)
    if sids[0] == '0':
        del sids[0]

    for sid in sids:
        elvs_array = []
        url = "https://suivisms.cnte.tn/ministere/preparatoire/liste_inscrit.php"
        payload = {
            "code_dre": "84",
            "code_etab": sid,
            "btenv": "طباعة"
        }
        
        soup = post_url_return_soup(url=url,payload=payload,request=request2,decode=True)

        table = soup.find('table', {'id': 'datatables', }).tbody
        tr_s = [i for i in table.children if i != '\n']

        for tr in tr_s:
            tds = [i for i in tr.children if i != '\n']
            uid = tds[1].text.strip()

            nom = tds[2].text.strip()
            nom = get_clean_name(nom)

            prenom = tds[3].text.strip()
            prenom= get_clean_name(prenom)

            date_naissance = tds[4].text.strip()

            sid = check_if_sid_need_to_be_replaced(sid, etatiq=True)

            eleve = Elvsprep(
                uid=uid,
                nom=nom,
                prenom=prenom,
                date_naissance=date_naissance,
                ecole_id=sid ,
            )
            elvs_array.append(eleve)

        with transaction.atomic():
            Elvsprep.objects.bulk_create(elvs_array, ignore_conflicts=False, update_conflicts=True, update_fields=[
                                         "nom", "prenom", "date_naissance", "ecole_id"])
            print(str(sid)+' : good ' + str(len(elvs_array)) + ' elvs')


    return Response(True)


def create_Elvpremiere(request2: requests.Session):
    request2.get(
        "https://suivisms.cnte.tn/ministere/index.php?op=primaire&act=inscrit_find")
    response = request2.get(
        "https://suivisms.cnte.tn/ministere/primaire/getetabprint1.php?id=84")

    select_element = response.content.decode(encoding='utf-8', errors='ignore')
    pattern = r'value="(\d+)"'
    sids = re.findall(pattern, select_element)
    if sids[0] == '0':
        del sids[0]
    for sid in sids:
        elvs_array = []
        url = "https://suivisms.cnte.tn/ministere/primaire/liste_inscrit.php"
        payload = {
            "code_dre": "84",
            "code_etab": sid,
            "btenv": "طباعة"
        }

        response = request2.post(url=url, data=payload)

        soup = bs(response.content.decode(
            encoding='utf-8', errors='ignore'), 'html.parser')

        table = soup.find('table', {'id': 'datatables', }).tbody

        tr_s = [i for i in table.children if i != '\n']

        for tr in tr_s:
            tds = [i for i in tr.children if i != '\n']
            uid = tds[1].text.strip()
            nom_prenom = tds[2].text.strip() + " " + tds[3].text.strip()
            date_naissance = tds[4].text.strip()
            eleve = AdminElvs(
                uid=uid,
                nom_prenom=get_clean_name(nom_prenom),
                date_naissance=date_naissance,
                ecole_id=sid if str(sid) not in sids_to_replace.keys(
                ) else sids_to_replace[str(sid)],
            )
            elvs_array.append(eleve)

        try:
            AdminElvs.objects.bulk_create(elvs_array, batch_size=100, ignore_conflicts=False, update_conflicts=True, update_fields=[
                                          "nom_prenom", "date_naissance", "ecole_id"])
            print(str(sid)+' : good ' + str(len(elvs_array)) + ' elvs')

        except IntegrityError as e:
            print("------------")
            print("errerur with this : " + str(sid))
            print(f"IntegrityError: {e}")
            print("------------")

    return Response(True)
=======
import re
import time
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
from bidict import bidict

from django.db import IntegrityError, transaction
from requests.exceptions import ChunkedEncodingError
from rest_framework.response import Response


from x.models import AdminEcoledata2 , AdminElvs , Del1,  Dre
from pprint import pprint


sids_to_replace= bidict({"842911":"842811",
                 "842913":"842813",
                 "842922":"842822",
                 "842923":"842823",
                 "842924":"842824",
                 "842912":"842812",
                 "842914":"842814" 
                 })

def create_AdminEcole_data():   # bulkcreate l data t3 mders f admin ecole data prive w etatik
    select_el = '''<select name="code_etab" size="1" style="font-family: Sakkal Majalla,Verdana; font-size: 16pt; font-weight: bold;"><option value="842401">م.إ.  الباب الشمالي  سوسة المدينة</option><option value="842405">م.إ.  العمارات الجنوبية  سوسة المدينة</option><option value="842407">م.إ.   الخزامة الشرقيــة  سوسة المدينة</option><option value="842412">م.إ. التريكية  سوسة المدينة</option><option value="842414">م.إ.   ابن خلدون  سوسة المدينة</option><option value="842416">م.إ.  العمارات الشمالية  سوسة المدينة</option><option value="842601">م.إ.  نهج المنصف باي  سوسة الجوهرة</option><option value="842602">م.إ.  نهج الحكيم قرول  سوسة الجوهرة</option><option value="842603">م.إ.  الصفايا  سوسة الجوهرة</option><option value="842604">م.إ. بوحسينة  2 سوسة الجوهرة</option><option value="842606">م.إ.  بوحسينة سوسة الجوهرة</option><option value="842607">م.إ.  نهج الغزالي  سوسة الجوهرة</option><option value="842610">م.إ.  حي التعمير  سوسة الجوهرة</option><option value="842613">م.إ.  خزامة الغربية سوسة الجوهرة</option><option value="842616">م.إ.  وادي غنيم  سوسة الجوهرة</option><option value="842617">م.إ.  الوفاء سهلول 2 سوسة الجوهرة</option><option value="842618">م.إ.  الامتياز- سهلول 1 سوسة الجوهرة</option><option value="842619">م.إ. الطموح سهلول 3 سوسة الجوهرة</option><option value="842620">م.إ. بوخيزر سوسة الجوهرة</option><option value="842705">م.إ.  خير الدين باشا  سيدي عبد الحميد</option><option value="842708">م.إ.  اسد بن الفرات  سيدي عبد الحميد</option><option value="842709">م.إ.  كدية مالك  سيدي عبد الحميد</option><option value="842711">م.إ.  قصيبة الشط  سيدي عبد الحميد</option><option value="842712">م.إ.  حي العوينة  سيدي عبد الحميد</option><option value="842714">م.إ.  ابن سينا  سيدي عبد الحميد</option><option value="842715">م.إ. حي الشباب  سيدي عبد الحميد</option><option value="842717">م.إ.  2 مارس 34 قصيبة الشط  سيدي عبد الحميد</option><option value="842718">م.إ.  سيدي عبد الحميد  سيدي عبد الحميد</option><option value="842719">م.إ. الكفيف سيدي عبد الحميد</option><option value="842911">م.إ.  الجمهورية  الزاوية القصيبة الثريات</option><option value="842912">م.إ.  علي البلهوان  الزاوية القصيبة الثريات</option><option value="842913">م.إ.  العفة  الزاوية القصيبة الثريات</option><option value="842914">م.إ. الثريات السالم الزاوية القصيبة الثريات</option><option value="842915">م.إ.  بورقيبة حي الزهور سوسة الرياض</option><option value="842916">م.إ. الشابي- الرياض الخامس سوسة الرياض</option><option value="842917">م.إ.  الفتح حي الرياض سوسة الرياض</option><option value="842918">م.إ.  المستقبل حي الزهور سوسة الرياض</option><option value="842920">م.إ.  الأمل حي الرياض سوسة الرياض</option><option value="842921">م.إ.  الهداية حي الزهور سوسة الرياض</option><option value="842922">م.إ. جمال الدين قصيبة سوسة الزاوية القصيبة الثريات</option><option value="842923">م.إ.  العهد الجديد زاوية سوسة الزاوية القصيبة الثريات</option><option value="842924">م.إ. الإمتياز الزاوية القصيبة الثريات</option><option value="842925">م.إ.  ابن شرف حي الرياض سوسة الرياض</option><option value="842926">م.إ.  طارق ابن زياد حي الرياض سوسة الرياض</option><option value="842927">م.إ.  السعادة حي الزهور سوسة الرياض</option><option value="842928">م.إ.  النجاح حي الرياض سوسة الرياض</option><option value="842929">م.إ.  السلام حي الرياض سوسة الرياض</option><option value="842930">م.إ المعرفة حي الرياض سوسة الرياض</option><option value="843001">م.إ.  الأخلاق حمام سوسة</option><option value="843002">م.إ.  25 جويلية حمام سوسة</option><option value="843003">م.إ.  طريق تونس حمام سوسة</option><option value="843004">م.إ.  سهلول حمام سوسة</option><option value="843005">م.إ. الشيخ محمد البحري حمام سوسة</option><option value="843006">م.إ.  طريق الشاطئ حمام سوسة</option><option value="843007">م.إ.  سيدي القنطاوي حمام سوسة</option><option value="843008">م.إ. أبو القاسم الشابي حمام سوسة</option><option value="843101">م.إ.  الحبيب الكامل- هرقلة</option><option value="843102">م.إ.  السويح هرقلة</option><option value="843103">م.إ.  العريبات هرقلة</option><option value="843201">م.إ.  بورقيبة أكودة</option><option value="843202">م.إ.  الراجحية أكودة أكودة</option><option value="843203">م.إ.  حشاد أكودة</option><option value="843204">م.إ.  شط مريم أكودة</option><option value="843205">م.إ.  الفقاعية أكودة</option><option value="843206">م.إ.  "علي الحطاب أكودة" أكودة</option><option value="843207">م.إ.  حاتم أكودة</option><option value="843208">م.إ.  طنطانة أكودة</option><option value="843209">م.إ.  وادي العروق أكودة</option><option value="843401">م.إ.  ابن خلدون القلعة الكبيرة</option><option value="843402">م.إ.  الحي الجديد القلعة الكبيرة</option><option value="843403">م.إ.  غرة جوان القلعة الكبيرة</option><option value="843404">م.إ.  9 أفريل القلعة الكبرى القلعة الكبيرة</option><option value="843405">م.إ.  الحي الشرقي القلعة الكبيرة</option><option value="843406">م.إ.  حي النزهة القلعة الكبيرة</option><option value="843410">م.إ.  سد الشياب القلعة الكبيرة</option><option value="843411">م.إ.  ابن عيسى القلعة الكبيرة</option><option value="843412">م.إ.  البورة ا القلعة الكبيرة</option><option value="843413">م.إ.  القبو القلعة الكبيرة</option><option value="843414">م.إ.  الكرارية القلعة الكبيرة</option><option value="843415">م.إ. حشاد القلعة الكبيرة</option><option value="843417">م.إ.  "2 مارس " القلعة الكبيرة</option><option value="843418">م.إ.  الزيتونة القلعة الكبيرة</option><option value="843421">م.إ. المنصورة القلعة الكبيرة</option><option value="843422">م.إ. أهل جميع القلعة الكبيرة</option><option value="843423">م.إأولاد الصلعاني القلعة الكبيرة</option><option value="843424">م.إ الغويرقة القلعة الكبيرة</option><option value="843901">م.إ.  ابن خلدون  سيدي بوعلي</option><option value="843902">م.إ.  منزل المحطة  سيدي بوعلي</option><option value="843903">م.إ.  سدّ أولاد علي  سيدي بوعلي</option><option value="843904">م.إ.  سلمون  سيدي بوعلي</option><option value="843905">م.إ.  السد الشمالي  سيدي بوعلي</option><option value="843906">م.إ.  الكنانة  سيدي بوعلي</option><option value="843907">م.إ.  وريمة  سيدي بوعلي</option><option value="843908">م.إ.  الشويشة  سيدي بوعلي</option><option value="843909">م.إ.  "الأنصاري"  سيدي بوعلي</option><option value="844301">م.إ.  بورقيبة  القلعة الصغيرة</option><option value="844302">م.إ.  البشرى  القلعة الصغيرة</option><option value="844303">م.إ. النقر  القلعة الصغيرة</option><option value="844304">م.إ.  ابن خلدون  القلعة الصغيرة</option><option value="844305">م.إ.   الحبيب  القلعة الصغيرة</option><option value="844306">م.إ.  غرة جوان القلعة الصغيرة</option><option value="844307">م.إ.  وادي لاية  القلعة الصغيرة</option><option value="844308">م.إ.  حي المنازه 1 القلعة الصغيرة</option><option value="844309">م.إ.  حي المنازه2  القلعة الصغيرة</option><option value="844310">م.إبت. النور(الصباغين) القلعة الصغيرة</option><option value="844901">م.إ.  حشاد  بوفيشة</option><option value="844902">م.إ.  عين الرحمة  بوفيشة</option><option value="844903">م.إ.  سيدي سعيد  بوفيشة</option><option value="844904">م.إ.  سيدي خليفة  بوفيشة</option><option value="844905">م.إ.  سيدي مطير بوفيشة</option><option value="844906">م.إ.  ابن الجزار - السلوم بوفيشة</option><option value="844907">م.إ.  الصفحة بوفيشة</option><option value="844908">م.إ.  وادي الخروب  بوفيشة</option><option value="844909">م.إ.  "2 مارس"  بوفيشة</option><option value="844910">م.إ.  الشابي كلم / 70  بوفيشة</option><option value="844911">م.إ.  المثاليث  بوفيشة</option><option value="844912">م.إ. لندرية  بوفيشة</option><option value="844913">المدسة الإبتدائية حي الرياض بوفيشة</option><option value="845401">م.إ.  بطحاء السوق  مساكن</option><option value="845402">م.إ.  نهج البريد  مساكن</option><option value="845403">م.إ.  نهج المحطة  مساكن</option><option value="845404">م.إ.  الحي الشمالي- مساكن</option><option value="845405">م.إ.  الحي الجديد  مساكن</option><option value="845406">م.إ. 2 مارس مساكن</option><option value="845407">م.إ.  حي التحرير  مساكن</option><option value="845408">م.إ.  بني كلثوم  مساكن</option><option value="845409">م.إ.  المور الدين  مساكن</option><option value="845410">م.إ.  إبن الهيثم المسعدين  مساكن</option><option value="845411">م.إ.  بني ربيعة  مساكن</option><option value="845412">م.إ.  البرجين  مساكن</option><option value="845413">م.إ. الكنائس مساكن</option><option value="845414">م.إ. الفرادة  مساكن</option><option value="845415">م.إ.  الفرادة الجديدة  مساكن</option><option value="845416">م.إ.  الكعيبي  مساكن</option><option value="845418">م.إ.  النهوض   مساكن</option><option value="845419">م.إ. النجاح مساكن مساكن</option><option value="845424">م.إ. النور  مساكن</option><option value="845426">م.إ.  الإمام الشافعي  مساكن</option><option value="845427">م.إ.  سيدي عبار  مساكن</option><option value="845428">م.إ.  وادي لاية  مساكن</option><option value="845430">م.إ.  المسعدين 2 مساكن</option><option value="845431">م.إ.  الحرية مساكن</option><option value="845501">م.إ. غبغوب  سيدي الهاني</option><option value="845502">م.إ.  كروسية  سيدي الهاني</option><option value="845503">م.إ. سيدي الهاني  سيدي الهاني</option><option value="845504">م.إ.  أولاد علي بلهاني  سيدي الهاني</option><option value="845505">م.إ.  أولاد الخشين  سيدي الهاني</option><option value="845506">م.إ.  أولاد بوبكر سيدي الهاني</option><option value="845507">م.إ.  الشراشير  سيدي الهاني</option><option value="845508">م.إ.  كروسية الشرقية  سيدي الهاني</option><option value="845509">م.إ.  المويسات سيدي الهاني</option><option value="845510">م.إ. أولاد الصغير  سيدي الهاني</option><option value="845511">م.إ. العزيب سيدي الهاني</option><option value="845601">م.إ.  الهادي شاكر النفيضة</option><option value="845602">م.إ.  الشقارنية  النفيضة</option><option value="845604">م.إ.  أولاد عبد الله  النفيضة</option><option value="845605">م.إ. منزل دار بلواعر  النفيضة</option><option value="845607">م.إ. فرحات حشاد النفيضة النفيضة</option><option value="845608">م.إ.  الفرادي  النفيضة</option><option value="845610">م.إ.  عين قارصي النفيضة</option><option value="845611">م.إ.  عين مذاكر  النفيضة</option><option value="845612">م.إ.  هيشر  النفيضة</option><option value="845614">م.إ.  منزل فاتح  النفيضة</option><option value="845616">م.إ.  تكرونة  النفيضة</option><option value="845619">م.إ.  الغويلات النفيضة</option><option value="845620">م.إ. مرابط حشاد  النفيضة</option><option value="845621">م.إ.  الغواليف  النفيضة</option><option value="845625">م.إ.  قريميت الشرقية  النفيضة</option><option value="845626">م.إ.  أولاد تليل  النفيضة</option><option value="845627">م.إ.  قريميت الغربية  النفيضة</option><option value="845628">م.إ.  سيدي سعيدان  النفيضة</option><option value="845629">م.إ.  المدافعي  النفيضة</option><option value="845630">م.إ.  الصمايدية أولاد بالليل النفيضة</option><option value="845631">م.إ. العيايشة النفيضة</option><option value="845632">م.إبت. الارتقاء (اولاد محمد) النفيضة</option><option value="845902">م.إ.  كندار كندار</option><option value="845903">م.إ.  أولاد عامر كندار</option><option value="845904">م.إ. البشاشمة  كندار</option><option value="845905">م.إ. البلالمة  كندار</option><option value="845906">م.إ. القماطة  كندار</option><option value="845907">م.إ.  بئر الجديد كندار</option><option value="845909">م.إ.  أولاد العابد  كندار</option><option value="845910">م.إبت. الرقي كندار</option></select>'''
    pattern = r'value="(\d+)"'
    sids = re.findall(pattern, select_el)
   
    pattern = r'<option value="[^"]+">([^<]+)</option>'
    ecole_names = re.findall(pattern, select_el)

    admin_ecoles_array = []
    for sid,name in zip(sids,ecole_names):
        sid = sid if sid not in sids_to_replace.keys() else sids_to_replace[sid]
        school_name = name.replace('م.إ.  ','').replace('م.إبت. ','').replace('م.إ. ','')
        ecole = AdminEcoledata2(
            sid=sid,
            school_name=school_name,
            dre_id=sid[:2],
            del1_id=sid[:4],
        )
        admin_ecoles_array.append(ecole)


    select_el_ecole_privee = '''<select name="code_etab" size="1" style="font-family: Sakkal Majalla,Verdana; font-size: 16pt; font-weight: bold;"><option value="849801">المدرسة الابتدائية الخاصة  صلاح الدين الأيوبي سوسة</option><option value="849802">المدرسة الابتدائية الخاصة  الأخوات  جوزفين</option><option value="849803">المدرسة الابتدائية الخاصة  الأمير الصغير سوسة</option><option value="849804">المدرسة الابتدائية الخاصة  ابن خلدون سوسة</option><option value="849806">المدرسة الابتدائية الخاصة  المعرفة مساكن</option><option value="849807">المدرسة الابتدائية الخاصة  فرنسواز دلتو</option><option value="849808">المدرسة الابتدائية الخاصة  العلماء</option><option value="849810">المدرسة الابتدائية الخاصة  جزيرة الأحلام</option><option value="849813">المدرسة الابتدائية الخاصة  الصديق بسوسة</option><option value="849814">المدرسة الابتدائية الخاصة  فاطمة الزهراء</option><option value="849815">المدرسة الابتدائية الخاصة  القدس</option><option value="849817">المدرسة الابتدائية الخاصة  القادة</option><option value="849818">المدرسة الابتدائية الخاصة دي لافونتان"De la Fontaine" بحمام سوسة</option><option value="849819">المدرسة الابتدائية الخاصة "الشابي" بحمام سوسة</option><option value="849820">المدرسة الابتدائية الخاصة "فولتير" بسوسة</option><option value="849821">المدرسة الابتدائية الخاصة "الرحمة" بسوسة الرياض</option><option value="849822">المدرسة الابتدائية الخاصة "الصغار العظماء" بسوسة الرياض</option><option value="849823">المدرسة الابتدائية الخاصة "ابن رشد" بالقلعة الكبرى</option><option value="849824">المدرسة الابتدائية الخاصة الآفاق الجديدة بأكودة</option><option value="849825">المدرسة الابتدائية الخاصة الامتياز بسوسة جوهرة</option><option value="849826">المدرسة الابتدائية الخاصة الخلدونية بالنفيضة</option><option value="849827">المدرسة الابتدائية الخاصة  "هابي شايلد" بسهلول1</option><option value="849828">المدرسة الابتدائية الخاصة الأنس بالقنطاوي</option><option value="849829">المدرسة الابتدائية الخاصة بيتاغور بخزامة الشرقية</option><option value="849830">المدرسة الابتدائية الخاصة "الصديق 2" بسوسة</option><option value="849831"> المدرسة الابتدائية الخاصة باسكال سكول بالقلعة الكبرى</option><option value="849832">المدرسة الابتدائية الخاصة جنتي</option><option value="849833">المدرسة الابتدائية الخاصة طريق الامتياز بالنفيضة</option><option value="849834">المدرسة الابتدائية الخاصة جون دوي بسوسة الجوهرة</option><option value="849835">المدرسة الابتدائية الخاصة العلم</option><option value="849836">المدرسة الابتدائية الخاصة المتفوقون بسوسة الجوهرة</option><option value="849837">المدرسة الابتدائية الخاصة البديل بمساكن</option><option value="849838">المدرسة الابتدائية الخاصة فكتور هيقو بزاوية سوسة</option><option value="849839">المدرسة الابتدائية الخاصة الرحمة 2</option><option value="849841">المدرسة الابتدائية الخاصة "النجوم" بمساكن</option><option value="849842">المدرسة الابتدائية الخاصة "Ma récré school" بسوسة جوهرة</option><option value="849844">المدرسة الابتدائية الخاصة "الأمد" بسهلول</option><option value="849845">المدرسة الابتدائية الخاصة قادة الغد "Leaders private school" بسوسة الرياض</option><option value="849846">المدرسة الابتدائية الخاصة "Decroly school" بخزامة الشرقية</option><option value="849847">المدرسة الابتدائية الخاصة "I school" ببوحسينة</option><option value="849848">المدرسة الابتدائية الخاصة "النجاح" بسهلول3</option><option value="849849">المدرسة الابتدائية الخاصة ألفونس دودي (برنامج فرنسي) ببوحسينة</option><option value="849850">المدرسة الابتدائية الخاصة زهرة الحياة بمساكن</option><option value="849851">المدرسة الابتدائية الخاصة الأهرام بسوسة</option><option value="849852">المدرسة الابتدائية الخاصة الياسمين بالزاوية</option><option value="849853">المدرسة الابتدائية الخاصة "المدرسة الابتدائية الدولية EPI"</option><option value="849854">المدرسة الابتدائية الخاصة "L'acadie" بأكودة</option><option value="849856">المدرسة الابتدائية الخاصة "دافنشي" بمساكن</option><option value="849857">المدرسة الابتدائية الخاصة "أميلكار" بالمسعدين</option><option value="849858">المدرسة الابتدائية الخاصة "القلعة La Tour" بالقلعة الكبرى</option><option value="849859">المدرسة الابتدائية الخاصة "المعهد الدولي الفرنسي محمد ادريس" بسوسة</option><option value="849860">المدرسة الابتدائية الخاصة "لاروس" بسوسة الرياض</option><option value="849861">المدرسة الابتدائية الخاصة "مؤسسة بن عبد الكريم للتعليم الخاص" بمساكن</option><option value="849862">المدرسة الابتدائية الخاصة أكاديمية النور بسوسة</option><option value="849863">المدرسة الابتدائية الخاصة"المدرسة الدولية بسوسة"</option><option value="849864">المدرسة الابتدائية الخاصة "هافارد" بالنفيضة</option><option value="849865">المدرسة الابتدائية الخاصة "عائشة" بشط مريم</option><option value="849866">المدرسة الابتدائية الخاصة "Inter Futur School" بسهلول</option><option value="849867">المدرسة الابتدائية الخاصة  "دروس موليار" بمساكن</option><option value="849868">المدرسة الابتدائية الخاصة "إينوف سكول" بالقلعة الصغرى</option></select>'''

    pattern = r'value="(\d+)"'
    sids = re.findall(pattern, select_el_ecole_privee)
   
    pattern = r'<option value="[^"]+">([^<]+)</option>'
    ecole_names = re.findall(pattern, select_el_ecole_privee)

    for sid,name in zip(sids,ecole_names):
        school_name = name.replace('المدرسة الابتدائية الخاصة  ','').replace('المدرسة الابتدائية الخاصة ','')
        ecole = AdminEcoledata2(
            sid=sid,
            school_name=school_name,
            dre_id=84,
            del1_id=sid[:4],
        )
        admin_ecoles_array.append(ecole)

    with transaction.atomic():
        AdminEcoledata2.objects.bulk_create(admin_ecoles_array,batch_size=100,ignore_conflicts=False,update_conflicts=True,update_fields=["school_name"])




def create_AdminElvs2(request2): # bulkcreate lil AdminElvs2 l request 5dheha mil Verify capatcha 5atr lezmn bypass heki bch tod5al donc torbtha m3aha in case of ist3mel

    def is_valid_date_string(date_string):
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False
        

    sids = AdminEcoledata2.objects.filter(del1_id=8498).values_list('sid',flat=True)

    for sid in sids:
        elvs_array=[]
        url = "http://admin.inscription.education.tn/ministere/index.php?op=prive&act=list_eleve_prive_prim"
        payload = {
            "code_dre": "84",
            "code_etab": sid if str(sid) not in sids_to_replace.items() else sids_to_replace.inverse(sid) ,
            "btenv": "بحث"
        }
        try:            
            response = request2.post(url=url, data=payload)
        except ChunkedEncodingError as e:
            print(f"Chunked Encoding Error: {e}")
            print('t7che f sid : ',end='')
            print(sid)
        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {e}")
            print('t7che f sid : ',end='')
            print(sid)
        print("sleep began")
        time.sleep(5)
        print("sleep finito")
        soup = bs(response.content.decode(
            encoding='utf-8', errors='ignore'), 'html.parser')
        table = soup.find('table', {'dir': 'rtl', 'border': '1'})
        tr_s = [i for i in table.children if i != '\n']

        for tr in tr_s[1:len(tr_s)-1]:
            data = tr.findAll('font')
          #  temp_uid = data[1].text.strip()
            uid = data[2].text.strip()
            if uid=="" or uid=="0" or not uid.isdigit():
                print('uid 5rajj :',end='')
                print(uid)
                continue
            nom_prenom = data[3].text.strip()
            nom_pere = data[4].text.strip()
            date_naissance = data[5].text.strip()
            elv = AdminElvs(
                uid=uid,
                nom_prenom=nom_prenom,
                nom_pere=nom_pere,
                date_naissance=date_naissance if is_valid_date_string(
                date_naissance) else None,
                ecole_id=sid,
             #   temp_uid=temp_uid
            )
            elvs_array.append(elv)
        
        try:
            AdminElvs.objects.bulk_create(elvs_array,batch_size=100,ignore_conflicts=False,update_conflicts=True,update_fields=["nom_prenom","nom_pere","date_naissance","ecole_id"])
            print(str(sid)+' : good '+ str(len(elvs_array))+ ' elvs')
            
            
        except IntegrityError as e:
            print("------------")
            print("errerur with this : " + str(sid))
            print(f"IntegrityError: {e}")
            print("------------")
        

    sids = AdminEcoledata2.objects.exclude(del1_id=8498).values_list('sid',flat=True)

    for sid in sids:
        print("currently traiment of : "+ str(sid))
        elvs_array=[]
        url = "http://admin.inscription.education.tn/ministere/index.php?op=inscprim&act=list_identifiant"
        payload = {
            "code_dre": "84",
              "code_etab": sid if str(sid) not in sids_to_replace.items() else sids_to_replace.inverse(sid) ,
            "btenv": "بحث"
        }

        try:
            response = request2.post(url=url, data=payload)
        except ChunkedEncodingError as e:
            print(f"Chunked Encoding Error: {e}")
            print('t7che f sid : ',end='')
            print(sid)
            
        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {e}")
            print('t7che f sid : ',end='')
            print(sid)
        soup = bs(response.content.decode(
            encoding='utf-8', errors='ignore'), 'html.parser')
        table = soup.find('table', {'dir': 'rtl', 'border': '1'})
        tr_s = [i for i in table.children if i != '\n']
        tr_s = [i for i in tr_s[0].children if i != '\n']
        for tr in tr_s[5:]:
            data = tr.findAll('font')
            uid = data[1].text.strip()
            if uid=="" or uid=="0" or not uid.isdigit():
                continue
            nom_prenom = data[2].text.strip()
            nom_pere = data[3].text.strip()
            date_naissance = data[4].text.strip()
            elv = AdminElvs(
                uid=uid,
                nom_prenom=nom_prenom,
                nom_pere=nom_pere,
                date_naissance=date_naissance if is_valid_date_string(
                date_naissance) else None,
                ecole_id=int(sid)
            )
            elvs_array.append(elv)
        try:
            AdminElvs.objects.bulk_create(elvs_array,batch_size=100,ignore_conflicts=False,update_conflicts=True,update_fields=["nom_prenom","nom_pere","date_naissance","ecole_id"])
            print(str(sid)+' : good '+ str(len(elvs_array))+ ' elvs')
            
            
        except Exception  as e:
            print("------------")
            print("errerur with this : " + str(sid))
            print(f"Exception : {e}")
            print("------------")

    return Response(True)





    ecoles = Ecole_data.objects.filter(sid__startswith='84')
    for ecole in ecoles:
       payload = {
           'ecole_url': ecole.url+'/',
           "saisieprenom": ecole.pr_nom,
           "saisienom": ecole.pr_prenom,
           "saisiepasswd": '1234',
           "saisie_membre": "administrateur",
       }
       if verify_cnte(payload):
           print('wowow  :'+str(ecole.sid))
       else:
           print('sid : '+str(ecole.sid) + ' non')
       pass
>>>>>>> 05b98efc67f75b0e94f2311b07801f92443b2d3a
=======
import re
import time
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
from bidict import bidict

from django.db import IntegrityError, transaction
from requests.exceptions import ChunkedEncodingError
from rest_framework.response import Response


from x.models import AdminEcoledata2 , AdminElvs , Del1,  Dre
from pprint import pprint


sids_to_replace= bidict({"842911":"842811",
                 "842913":"842813",
                 "842922":"842822",
                 "842923":"842823",
                 "842924":"842824",
                 "842912":"842812",
                 "842914":"842814" 
                 })

def create_AdminEcole_data():   # bulkcreate l data t3 mders f admin ecole data prive w etatik
    select_el = '''<select name="code_etab" size="1" style="font-family: Sakkal Majalla,Verdana; font-size: 16pt; font-weight: bold;"><option value="842401">م.إ.  الباب الشمالي  سوسة المدينة</option><option value="842405">م.إ.  العمارات الجنوبية  سوسة المدينة</option><option value="842407">م.إ.   الخزامة الشرقيــة  سوسة المدينة</option><option value="842412">م.إ. التريكية  سوسة المدينة</option><option value="842414">م.إ.   ابن خلدون  سوسة المدينة</option><option value="842416">م.إ.  العمارات الشمالية  سوسة المدينة</option><option value="842601">م.إ.  نهج المنصف باي  سوسة الجوهرة</option><option value="842602">م.إ.  نهج الحكيم قرول  سوسة الجوهرة</option><option value="842603">م.إ.  الصفايا  سوسة الجوهرة</option><option value="842604">م.إ. بوحسينة  2 سوسة الجوهرة</option><option value="842606">م.إ.  بوحسينة سوسة الجوهرة</option><option value="842607">م.إ.  نهج الغزالي  سوسة الجوهرة</option><option value="842610">م.إ.  حي التعمير  سوسة الجوهرة</option><option value="842613">م.إ.  خزامة الغربية سوسة الجوهرة</option><option value="842616">م.إ.  وادي غنيم  سوسة الجوهرة</option><option value="842617">م.إ.  الوفاء سهلول 2 سوسة الجوهرة</option><option value="842618">م.إ.  الامتياز- سهلول 1 سوسة الجوهرة</option><option value="842619">م.إ. الطموح سهلول 3 سوسة الجوهرة</option><option value="842620">م.إ. بوخيزر سوسة الجوهرة</option><option value="842705">م.إ.  خير الدين باشا  سيدي عبد الحميد</option><option value="842708">م.إ.  اسد بن الفرات  سيدي عبد الحميد</option><option value="842709">م.إ.  كدية مالك  سيدي عبد الحميد</option><option value="842711">م.إ.  قصيبة الشط  سيدي عبد الحميد</option><option value="842712">م.إ.  حي العوينة  سيدي عبد الحميد</option><option value="842714">م.إ.  ابن سينا  سيدي عبد الحميد</option><option value="842715">م.إ. حي الشباب  سيدي عبد الحميد</option><option value="842717">م.إ.  2 مارس 34 قصيبة الشط  سيدي عبد الحميد</option><option value="842718">م.إ.  سيدي عبد الحميد  سيدي عبد الحميد</option><option value="842719">م.إ. الكفيف سيدي عبد الحميد</option><option value="842911">م.إ.  الجمهورية  الزاوية القصيبة الثريات</option><option value="842912">م.إ.  علي البلهوان  الزاوية القصيبة الثريات</option><option value="842913">م.إ.  العفة  الزاوية القصيبة الثريات</option><option value="842914">م.إ. الثريات السالم الزاوية القصيبة الثريات</option><option value="842915">م.إ.  بورقيبة حي الزهور سوسة الرياض</option><option value="842916">م.إ. الشابي- الرياض الخامس سوسة الرياض</option><option value="842917">م.إ.  الفتح حي الرياض سوسة الرياض</option><option value="842918">م.إ.  المستقبل حي الزهور سوسة الرياض</option><option value="842920">م.إ.  الأمل حي الرياض سوسة الرياض</option><option value="842921">م.إ.  الهداية حي الزهور سوسة الرياض</option><option value="842922">م.إ. جمال الدين قصيبة سوسة الزاوية القصيبة الثريات</option><option value="842923">م.إ.  العهد الجديد زاوية سوسة الزاوية القصيبة الثريات</option><option value="842924">م.إ. الإمتياز الزاوية القصيبة الثريات</option><option value="842925">م.إ.  ابن شرف حي الرياض سوسة الرياض</option><option value="842926">م.إ.  طارق ابن زياد حي الرياض سوسة الرياض</option><option value="842927">م.إ.  السعادة حي الزهور سوسة الرياض</option><option value="842928">م.إ.  النجاح حي الرياض سوسة الرياض</option><option value="842929">م.إ.  السلام حي الرياض سوسة الرياض</option><option value="842930">م.إ المعرفة حي الرياض سوسة الرياض</option><option value="843001">م.إ.  الأخلاق حمام سوسة</option><option value="843002">م.إ.  25 جويلية حمام سوسة</option><option value="843003">م.إ.  طريق تونس حمام سوسة</option><option value="843004">م.إ.  سهلول حمام سوسة</option><option value="843005">م.إ. الشيخ محمد البحري حمام سوسة</option><option value="843006">م.إ.  طريق الشاطئ حمام سوسة</option><option value="843007">م.إ.  سيدي القنطاوي حمام سوسة</option><option value="843008">م.إ. أبو القاسم الشابي حمام سوسة</option><option value="843101">م.إ.  الحبيب الكامل- هرقلة</option><option value="843102">م.إ.  السويح هرقلة</option><option value="843103">م.إ.  العريبات هرقلة</option><option value="843201">م.إ.  بورقيبة أكودة</option><option value="843202">م.إ.  الراجحية أكودة أكودة</option><option value="843203">م.إ.  حشاد أكودة</option><option value="843204">م.إ.  شط مريم أكودة</option><option value="843205">م.إ.  الفقاعية أكودة</option><option value="843206">م.إ.  "علي الحطاب أكودة" أكودة</option><option value="843207">م.إ.  حاتم أكودة</option><option value="843208">م.إ.  طنطانة أكودة</option><option value="843209">م.إ.  وادي العروق أكودة</option><option value="843401">م.إ.  ابن خلدون القلعة الكبيرة</option><option value="843402">م.إ.  الحي الجديد القلعة الكبيرة</option><option value="843403">م.إ.  غرة جوان القلعة الكبيرة</option><option value="843404">م.إ.  9 أفريل القلعة الكبرى القلعة الكبيرة</option><option value="843405">م.إ.  الحي الشرقي القلعة الكبيرة</option><option value="843406">م.إ.  حي النزهة القلعة الكبيرة</option><option value="843410">م.إ.  سد الشياب القلعة الكبيرة</option><option value="843411">م.إ.  ابن عيسى القلعة الكبيرة</option><option value="843412">م.إ.  البورة ا القلعة الكبيرة</option><option value="843413">م.إ.  القبو القلعة الكبيرة</option><option value="843414">م.إ.  الكرارية القلعة الكبيرة</option><option value="843415">م.إ. حشاد القلعة الكبيرة</option><option value="843417">م.إ.  "2 مارس " القلعة الكبيرة</option><option value="843418">م.إ.  الزيتونة القلعة الكبيرة</option><option value="843421">م.إ. المنصورة القلعة الكبيرة</option><option value="843422">م.إ. أهل جميع القلعة الكبيرة</option><option value="843423">م.إأولاد الصلعاني القلعة الكبيرة</option><option value="843424">م.إ الغويرقة القلعة الكبيرة</option><option value="843901">م.إ.  ابن خلدون  سيدي بوعلي</option><option value="843902">م.إ.  منزل المحطة  سيدي بوعلي</option><option value="843903">م.إ.  سدّ أولاد علي  سيدي بوعلي</option><option value="843904">م.إ.  سلمون  سيدي بوعلي</option><option value="843905">م.إ.  السد الشمالي  سيدي بوعلي</option><option value="843906">م.إ.  الكنانة  سيدي بوعلي</option><option value="843907">م.إ.  وريمة  سيدي بوعلي</option><option value="843908">م.إ.  الشويشة  سيدي بوعلي</option><option value="843909">م.إ.  "الأنصاري"  سيدي بوعلي</option><option value="844301">م.إ.  بورقيبة  القلعة الصغيرة</option><option value="844302">م.إ.  البشرى  القلعة الصغيرة</option><option value="844303">م.إ. النقر  القلعة الصغيرة</option><option value="844304">م.إ.  ابن خلدون  القلعة الصغيرة</option><option value="844305">م.إ.   الحبيب  القلعة الصغيرة</option><option value="844306">م.إ.  غرة جوان القلعة الصغيرة</option><option value="844307">م.إ.  وادي لاية  القلعة الصغيرة</option><option value="844308">م.إ.  حي المنازه 1 القلعة الصغيرة</option><option value="844309">م.إ.  حي المنازه2  القلعة الصغيرة</option><option value="844310">م.إبت. النور(الصباغين) القلعة الصغيرة</option><option value="844901">م.إ.  حشاد  بوفيشة</option><option value="844902">م.إ.  عين الرحمة  بوفيشة</option><option value="844903">م.إ.  سيدي سعيد  بوفيشة</option><option value="844904">م.إ.  سيدي خليفة  بوفيشة</option><option value="844905">م.إ.  سيدي مطير بوفيشة</option><option value="844906">م.إ.  ابن الجزار - السلوم بوفيشة</option><option value="844907">م.إ.  الصفحة بوفيشة</option><option value="844908">م.إ.  وادي الخروب  بوفيشة</option><option value="844909">م.إ.  "2 مارس"  بوفيشة</option><option value="844910">م.إ.  الشابي كلم / 70  بوفيشة</option><option value="844911">م.إ.  المثاليث  بوفيشة</option><option value="844912">م.إ. لندرية  بوفيشة</option><option value="844913">المدسة الإبتدائية حي الرياض بوفيشة</option><option value="845401">م.إ.  بطحاء السوق  مساكن</option><option value="845402">م.إ.  نهج البريد  مساكن</option><option value="845403">م.إ.  نهج المحطة  مساكن</option><option value="845404">م.إ.  الحي الشمالي- مساكن</option><option value="845405">م.إ.  الحي الجديد  مساكن</option><option value="845406">م.إ. 2 مارس مساكن</option><option value="845407">م.إ.  حي التحرير  مساكن</option><option value="845408">م.إ.  بني كلثوم  مساكن</option><option value="845409">م.إ.  المور الدين  مساكن</option><option value="845410">م.إ.  إبن الهيثم المسعدين  مساكن</option><option value="845411">م.إ.  بني ربيعة  مساكن</option><option value="845412">م.إ.  البرجين  مساكن</option><option value="845413">م.إ. الكنائس مساكن</option><option value="845414">م.إ. الفرادة  مساكن</option><option value="845415">م.إ.  الفرادة الجديدة  مساكن</option><option value="845416">م.إ.  الكعيبي  مساكن</option><option value="845418">م.إ.  النهوض   مساكن</option><option value="845419">م.إ. النجاح مساكن مساكن</option><option value="845424">م.إ. النور  مساكن</option><option value="845426">م.إ.  الإمام الشافعي  مساكن</option><option value="845427">م.إ.  سيدي عبار  مساكن</option><option value="845428">م.إ.  وادي لاية  مساكن</option><option value="845430">م.إ.  المسعدين 2 مساكن</option><option value="845431">م.إ.  الحرية مساكن</option><option value="845501">م.إ. غبغوب  سيدي الهاني</option><option value="845502">م.إ.  كروسية  سيدي الهاني</option><option value="845503">م.إ. سيدي الهاني  سيدي الهاني</option><option value="845504">م.إ.  أولاد علي بلهاني  سيدي الهاني</option><option value="845505">م.إ.  أولاد الخشين  سيدي الهاني</option><option value="845506">م.إ.  أولاد بوبكر سيدي الهاني</option><option value="845507">م.إ.  الشراشير  سيدي الهاني</option><option value="845508">م.إ.  كروسية الشرقية  سيدي الهاني</option><option value="845509">م.إ.  المويسات سيدي الهاني</option><option value="845510">م.إ. أولاد الصغير  سيدي الهاني</option><option value="845511">م.إ. العزيب سيدي الهاني</option><option value="845601">م.إ.  الهادي شاكر النفيضة</option><option value="845602">م.إ.  الشقارنية  النفيضة</option><option value="845604">م.إ.  أولاد عبد الله  النفيضة</option><option value="845605">م.إ. منزل دار بلواعر  النفيضة</option><option value="845607">م.إ. فرحات حشاد النفيضة النفيضة</option><option value="845608">م.إ.  الفرادي  النفيضة</option><option value="845610">م.إ.  عين قارصي النفيضة</option><option value="845611">م.إ.  عين مذاكر  النفيضة</option><option value="845612">م.إ.  هيشر  النفيضة</option><option value="845614">م.إ.  منزل فاتح  النفيضة</option><option value="845616">م.إ.  تكرونة  النفيضة</option><option value="845619">م.إ.  الغويلات النفيضة</option><option value="845620">م.إ. مرابط حشاد  النفيضة</option><option value="845621">م.إ.  الغواليف  النفيضة</option><option value="845625">م.إ.  قريميت الشرقية  النفيضة</option><option value="845626">م.إ.  أولاد تليل  النفيضة</option><option value="845627">م.إ.  قريميت الغربية  النفيضة</option><option value="845628">م.إ.  سيدي سعيدان  النفيضة</option><option value="845629">م.إ.  المدافعي  النفيضة</option><option value="845630">م.إ.  الصمايدية أولاد بالليل النفيضة</option><option value="845631">م.إ. العيايشة النفيضة</option><option value="845632">م.إبت. الارتقاء (اولاد محمد) النفيضة</option><option value="845902">م.إ.  كندار كندار</option><option value="845903">م.إ.  أولاد عامر كندار</option><option value="845904">م.إ. البشاشمة  كندار</option><option value="845905">م.إ. البلالمة  كندار</option><option value="845906">م.إ. القماطة  كندار</option><option value="845907">م.إ.  بئر الجديد كندار</option><option value="845909">م.إ.  أولاد العابد  كندار</option><option value="845910">م.إبت. الرقي كندار</option></select>'''
    pattern = r'value="(\d+)"'
    sids = re.findall(pattern, select_el)
   
    pattern = r'<option value="[^"]+">([^<]+)</option>'
    ecole_names = re.findall(pattern, select_el)

    admin_ecoles_array = []
    for sid,name in zip(sids,ecole_names):
        sid = sid if sid not in sids_to_replace.keys() else sids_to_replace[sid]
        school_name = name.replace('م.إ.  ','').replace('م.إبت. ','').replace('م.إ. ','')
        ecole = AdminEcoledata2(
            sid=sid,
            school_name=school_name,
            dre_id=sid[:2],
            del1_id=sid[:4],
        )
        admin_ecoles_array.append(ecole)


    select_el_ecole_privee = '''<select name="code_etab" size="1" style="font-family: Sakkal Majalla,Verdana; font-size: 16pt; font-weight: bold;"><option value="849801">المدرسة الابتدائية الخاصة  صلاح الدين الأيوبي سوسة</option><option value="849802">المدرسة الابتدائية الخاصة  الأخوات  جوزفين</option><option value="849803">المدرسة الابتدائية الخاصة  الأمير الصغير سوسة</option><option value="849804">المدرسة الابتدائية الخاصة  ابن خلدون سوسة</option><option value="849806">المدرسة الابتدائية الخاصة  المعرفة مساكن</option><option value="849807">المدرسة الابتدائية الخاصة  فرنسواز دلتو</option><option value="849808">المدرسة الابتدائية الخاصة  العلماء</option><option value="849810">المدرسة الابتدائية الخاصة  جزيرة الأحلام</option><option value="849813">المدرسة الابتدائية الخاصة  الصديق بسوسة</option><option value="849814">المدرسة الابتدائية الخاصة  فاطمة الزهراء</option><option value="849815">المدرسة الابتدائية الخاصة  القدس</option><option value="849817">المدرسة الابتدائية الخاصة  القادة</option><option value="849818">المدرسة الابتدائية الخاصة دي لافونتان"De la Fontaine" بحمام سوسة</option><option value="849819">المدرسة الابتدائية الخاصة "الشابي" بحمام سوسة</option><option value="849820">المدرسة الابتدائية الخاصة "فولتير" بسوسة</option><option value="849821">المدرسة الابتدائية الخاصة "الرحمة" بسوسة الرياض</option><option value="849822">المدرسة الابتدائية الخاصة "الصغار العظماء" بسوسة الرياض</option><option value="849823">المدرسة الابتدائية الخاصة "ابن رشد" بالقلعة الكبرى</option><option value="849824">المدرسة الابتدائية الخاصة الآفاق الجديدة بأكودة</option><option value="849825">المدرسة الابتدائية الخاصة الامتياز بسوسة جوهرة</option><option value="849826">المدرسة الابتدائية الخاصة الخلدونية بالنفيضة</option><option value="849827">المدرسة الابتدائية الخاصة  "هابي شايلد" بسهلول1</option><option value="849828">المدرسة الابتدائية الخاصة الأنس بالقنطاوي</option><option value="849829">المدرسة الابتدائية الخاصة بيتاغور بخزامة الشرقية</option><option value="849830">المدرسة الابتدائية الخاصة "الصديق 2" بسوسة</option><option value="849831"> المدرسة الابتدائية الخاصة باسكال سكول بالقلعة الكبرى</option><option value="849832">المدرسة الابتدائية الخاصة جنتي</option><option value="849833">المدرسة الابتدائية الخاصة طريق الامتياز بالنفيضة</option><option value="849834">المدرسة الابتدائية الخاصة جون دوي بسوسة الجوهرة</option><option value="849835">المدرسة الابتدائية الخاصة العلم</option><option value="849836">المدرسة الابتدائية الخاصة المتفوقون بسوسة الجوهرة</option><option value="849837">المدرسة الابتدائية الخاصة البديل بمساكن</option><option value="849838">المدرسة الابتدائية الخاصة فكتور هيقو بزاوية سوسة</option><option value="849839">المدرسة الابتدائية الخاصة الرحمة 2</option><option value="849841">المدرسة الابتدائية الخاصة "النجوم" بمساكن</option><option value="849842">المدرسة الابتدائية الخاصة "Ma récré school" بسوسة جوهرة</option><option value="849844">المدرسة الابتدائية الخاصة "الأمد" بسهلول</option><option value="849845">المدرسة الابتدائية الخاصة قادة الغد "Leaders private school" بسوسة الرياض</option><option value="849846">المدرسة الابتدائية الخاصة "Decroly school" بخزامة الشرقية</option><option value="849847">المدرسة الابتدائية الخاصة "I school" ببوحسينة</option><option value="849848">المدرسة الابتدائية الخاصة "النجاح" بسهلول3</option><option value="849849">المدرسة الابتدائية الخاصة ألفونس دودي (برنامج فرنسي) ببوحسينة</option><option value="849850">المدرسة الابتدائية الخاصة زهرة الحياة بمساكن</option><option value="849851">المدرسة الابتدائية الخاصة الأهرام بسوسة</option><option value="849852">المدرسة الابتدائية الخاصة الياسمين بالزاوية</option><option value="849853">المدرسة الابتدائية الخاصة "المدرسة الابتدائية الدولية EPI"</option><option value="849854">المدرسة الابتدائية الخاصة "L'acadie" بأكودة</option><option value="849856">المدرسة الابتدائية الخاصة "دافنشي" بمساكن</option><option value="849857">المدرسة الابتدائية الخاصة "أميلكار" بالمسعدين</option><option value="849858">المدرسة الابتدائية الخاصة "القلعة La Tour" بالقلعة الكبرى</option><option value="849859">المدرسة الابتدائية الخاصة "المعهد الدولي الفرنسي محمد ادريس" بسوسة</option><option value="849860">المدرسة الابتدائية الخاصة "لاروس" بسوسة الرياض</option><option value="849861">المدرسة الابتدائية الخاصة "مؤسسة بن عبد الكريم للتعليم الخاص" بمساكن</option><option value="849862">المدرسة الابتدائية الخاصة أكاديمية النور بسوسة</option><option value="849863">المدرسة الابتدائية الخاصة"المدرسة الدولية بسوسة"</option><option value="849864">المدرسة الابتدائية الخاصة "هافارد" بالنفيضة</option><option value="849865">المدرسة الابتدائية الخاصة "عائشة" بشط مريم</option><option value="849866">المدرسة الابتدائية الخاصة "Inter Futur School" بسهلول</option><option value="849867">المدرسة الابتدائية الخاصة  "دروس موليار" بمساكن</option><option value="849868">المدرسة الابتدائية الخاصة "إينوف سكول" بالقلعة الصغرى</option></select>'''

    pattern = r'value="(\d+)"'
    sids = re.findall(pattern, select_el_ecole_privee)
   
    pattern = r'<option value="[^"]+">([^<]+)</option>'
    ecole_names = re.findall(pattern, select_el_ecole_privee)

    for sid,name in zip(sids,ecole_names):
        school_name = name.replace('المدرسة الابتدائية الخاصة  ','').replace('المدرسة الابتدائية الخاصة ','')
        ecole = AdminEcoledata2(
            sid=sid,
            school_name=school_name,
            dre_id=84,
            del1_id=sid[:4],
        )
        admin_ecoles_array.append(ecole)

    with transaction.atomic():
        AdminEcoledata2.objects.bulk_create(admin_ecoles_array,batch_size=100,ignore_conflicts=False,update_conflicts=True,update_fields=["school_name"])




def create_AdminElvs2(request2): # bulkcreate lil AdminElvs2 l request 5dheha mil Verify capatcha 5atr lezmn bypass heki bch tod5al donc torbtha m3aha in case of ist3mel

    def is_valid_date_string(date_string):
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False
        

    sids = AdminEcoledata2.objects.filter(del1_id=8498).values_list('sid',flat=True)

    for sid in sids:
        elvs_array=[]
        url = "http://admin.inscription.education.tn/ministere/index.php?op=prive&act=list_eleve_prive_prim"
        payload = {
            "code_dre": "84",
            "code_etab": sid if str(sid) not in sids_to_replace.items() else sids_to_replace.inverse(sid) ,
            "btenv": "بحث"
        }
        try:            
            response = request2.post(url=url, data=payload)
        except ChunkedEncodingError as e:
            print(f"Chunked Encoding Error: {e}")
            print('t7che f sid : ',end='')
            print(sid)
        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {e}")
            print('t7che f sid : ',end='')
            print(sid)
        print("sleep began")
        time.sleep(5)
        print("sleep finito")
        soup = bs(response.content.decode(
            encoding='utf-8', errors='ignore'), 'html.parser')
        table = soup.find('table', {'dir': 'rtl', 'border': '1'})
        tr_s = [i for i in table.children if i != '\n']

        for tr in tr_s[1:len(tr_s)-1]:
            data = tr.findAll('font')
          #  temp_uid = data[1].text.strip()
            uid = data[2].text.strip()
            if uid=="" or uid=="0" or not uid.isdigit():
                print('uid 5rajj :',end='')
                print(uid)
                continue
            nom_prenom = data[3].text.strip()
            nom_pere = data[4].text.strip()
            date_naissance = data[5].text.strip()
            elv = AdminElvs(
                uid=uid,
                nom_prenom=nom_prenom,
                nom_pere=nom_pere,
                date_naissance=date_naissance if is_valid_date_string(
                date_naissance) else None,
                ecole_id=sid,
             #   temp_uid=temp_uid
            )
            elvs_array.append(elv)
        
        try:
            AdminElvs.objects.bulk_create(elvs_array,batch_size=100,ignore_conflicts=False,update_conflicts=True,update_fields=["nom_prenom","nom_pere","date_naissance","ecole_id"])
            print(str(sid)+' : good '+ str(len(elvs_array))+ ' elvs')
            
            
        except IntegrityError as e:
            print("------------")
            print("errerur with this : " + str(sid))
            print(f"IntegrityError: {e}")
            print("------------")
        

    sids = AdminEcoledata2.objects.exclude(del1_id=8498).values_list('sid',flat=True)

    for sid in sids:
        print("currently traiment of : "+ str(sid))
        elvs_array=[]
        url = "http://admin.inscription.education.tn/ministere/index.php?op=inscprim&act=list_identifiant"
        payload = {
            "code_dre": "84",
              "code_etab": sid if str(sid) not in sids_to_replace.items() else sids_to_replace.inverse(sid) ,
            "btenv": "بحث"
        }

        try:
            response = request2.post(url=url, data=payload)
        except ChunkedEncodingError as e:
            print(f"Chunked Encoding Error: {e}")
            print('t7che f sid : ',end='')
            print(sid)
            
        except requests.exceptions.RequestException as e:
            print(f"Request Exception: {e}")
            print('t7che f sid : ',end='')
            print(sid)
        soup = bs(response.content.decode(
            encoding='utf-8', errors='ignore'), 'html.parser')
        table = soup.find('table', {'dir': 'rtl', 'border': '1'})
        tr_s = [i for i in table.children if i != '\n']
        tr_s = [i for i in tr_s[0].children if i != '\n']
        for tr in tr_s[5:]:
            data = tr.findAll('font')
            uid = data[1].text.strip()
            if uid=="" or uid=="0" or not uid.isdigit():
                continue
            nom_prenom = data[2].text.strip()
            nom_pere = data[3].text.strip()
            date_naissance = data[4].text.strip()
            elv = AdminElvs(
                uid=uid,
                nom_prenom=nom_prenom,
                nom_pere=nom_pere,
                date_naissance=date_naissance if is_valid_date_string(
                date_naissance) else None,
                ecole_id=int(sid)
            )
            elvs_array.append(elv)
        try:
            AdminElvs.objects.bulk_create(elvs_array,batch_size=100,ignore_conflicts=False,update_conflicts=True,update_fields=["nom_prenom","nom_pere","date_naissance","ecole_id"])
            print(str(sid)+' : good '+ str(len(elvs_array))+ ' elvs')
            
            
        except Exception  as e:
            print("------------")
            print("errerur with this : " + str(sid))
            print(f"Exception : {e}")
            print("------------")

    return Response(True)





    ecoles = Ecole_data.objects.filter(sid__startswith='84')
    for ecole in ecoles:
       payload = {
           'ecole_url': ecole.url+'/',
           "saisieprenom": ecole.pr_nom,
           "saisienom": ecole.pr_prenom,
           "saisiepasswd": '1234',
           "saisie_membre": "administrateur",
       }
       if verify_cnte(payload):
           print('wowow  :'+str(ecole.sid))
       else:
           print('sid : '+str(ecole.sid) + ' non')
       pass
>>>>>>> 05b98efc67f75b0e94f2311b07801f92443b2d3a
