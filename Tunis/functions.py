
import re
from Tunis.models import EcolesTunis
from x.functions import CustomError
from bs4 import BeautifulSoup as bs


def extract_cnte_id(input_string):
    pattern = r'\((\d+)\)'
    match = re.search(pattern, input_string)
    if match:
        return int(match.group(1))

    raise CustomError('famma cnte_id mefiyouch number fil link te3ou ????')




def extract_ecoles_of_dre_info(soup:bs,dre:dict): # extract all ecoles info of a single dre : schhol_name,principal,slug
    table_element = soup.find('table', {'id': 'datatables'}).tbody
    tr_s = [tr for tr in table_element.children if tr != '\n']
    ecoles = []
    for tr in tr_s:
        tds = [td for td in tr.children if td != '\n']
        sid = tds[0].text.strip()
        ecole_name = tds[1].text.strip()
        slug = tds[1].a['href']
        principal_name = tds[2].text.strip()
        ecole = EcolesTunis(
            sid=sid,
            school_name=ecole_name,
            principal=principal_name,
            dre_id=dre['id'],
            slug=slug
        )
        ecoles.append(ecole)
    
    return ecoles
