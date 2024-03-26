

from Tunis.models import DreTunis
from x.functions import CustomError


def Verify_len_dres_same(dres_count_in_soup):
    db_dres_count = DreTunis.objects.all().count()
    if db_dres_count != dres_count_in_soup:
        message= "l len t3 dres f links wel db count is not the same \n"
        message+= "len db_dre = "+str(db_dres_count)+"  "
        message+= "len soup_dre = "+str(dres_count_in_soup)
        raise CustomError(message)


def Verify_Dre_exits(dre_name):
    dre = DreTunis.objects.filter(name=dre_name).first()
    if not dre:
        raise CustomError(
            dre_name, " ismou mefamech fil db not exactly at least")

    return dre.dre_id_in_cnte


def Verify_both_cnte_ids_same(db_cnte_id, soup_cnte_id):
    if db_cnte_id != soup_cnte_id:
        dre_in_question = DreTunis.objects.filter(
            dre_id_in_cnte=db_cnte_id).first()
        message = dre_in_question.name+" l id te3ou fil cnte tbaddl \n"
        message+= 'db_id = ' + str(db_cnte_id) +"   "
        message+= 'w lo5ra :'+str(soup_cnte_id)
        raise CustomError(message)



def Verify_number_of_classes_matches(nbr_classes_instances, nbr_class):
    r""" ythabet ken 3dad l claset kifkif milli 5dhithom 
        w 3dadhom fil mo3tayet l 3amma
    """

    if nbr_class != nbr_classes_instances:
        msg= "!!!!!!!!!!"
        msg+= '\n3dad l classet l 5dhithom vs l 3dad fil mo3tayet l 3amma unequal \n'
        msg+= 'nbr f classes_instances = '+str(nbr_classes_instances)
        msg+= '\nw fil mo3tayet l 3ama = '+str(nbr_class)
        raise CustomError(msg)
    print('\n✓ ✓ number of classes extracted matches whats in mo3tayet 3amma ')
    


def Verify_number_of_elvs_matches(nbr_eleves_instances, nbr_eleves):
    r""" ythabet ken 3dad l claset kifkif milli 5dhithom 
        w 3dadhom fil mo3tayet l 3amma
    """
    
    if nbr_eleves != nbr_eleves_instances:
        msg= "!!!!!!!!!!"
        msg+= '3dad l eleves l 5dhithom vs l 3dad fil mo3tayet l 3amma unequal \n'
        msg+= 'nbr t3 l eleves = '+str(nbr_eleves_instances)
        msg+= '\nw fil mo3tayet l 3ama = '+str(nbr_eleves)
        print(msg)
        response= input('if you wanna quit type break   :   ')
        if response=="break":
            raise CustomError("")
        
    print('\n✓ len of elvs extracted matches the number in cnte')