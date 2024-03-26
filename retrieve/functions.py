from x.models import AdminElvs
from thefuzz import fuzz



####################    search by date   #####################

def search_elv_by_date(date):
    matching_objects = AdminElvs.objects.filter(date_naissance=date).values_list(
        "uid", "nom_prenom", "nom_pere", "date_naissance", 'ecole__school_name')
    return matching_objects



################### custom sql search ######################


hamza_options = ["ا", "أ", "إ", "آ", "ٱ", "ء", "ئ", "ؤ"]
lte2_options = ["ة", "ت", "ه"]
edha2 = ["ظ", "ض"]
essa2 = ["س", "ص"]
all_letter_options = hamza_options + lte2_options + edha2 + essa2


def change_character_at_index(string, index, new_character):
    if index < 0 or index >= len(string):
        print('out of range ???')
        return string  # Return original string if index is out of range
    return string[:index] + new_character + string[index + 1:]


def set_multiple_names(name, index=-1):

    results = []
    condition = True

    if index == -1:
        alt_name = ""
        index = 0
        name = name.replace(' ','')
    else:
        alt_name = name[:index]
    # if i+1 == len(name): return name ????
    for i in range(index, len(name)):
        if name[i] == " ":
            continue

        if name[i] in hamza_options:
            condition = False
            for letter_option in hamza_options:
                new_name_option = change_character_at_index(
                    string=name, index=i, new_character=letter_option)
                results.extend(set_multiple_names(new_name_option, index=i+1))
            break

        if name[i] in lte2_options:
            condition = False
            for letter_option in lte2_options:
                new_name_option = change_character_at_index(
                    string=name, index=i, new_character=letter_option)
                results.extend(set_multiple_names(new_name_option, index=i+1))
            break

        if name[i] in edha2:
            condition = False
            for letter_option in edha2:
                new_name_option = change_character_at_index(
                    string=name, index=i, new_character=letter_option)
                results.extend(set_multiple_names(new_name_option, index=i+1))
            break

        if name[i] in essa2:
            condition = False
            for letter_option in essa2:
                new_name_option = change_character_at_index(
                    string=name, index=i, new_character=letter_option)
                results.extend(set_multiple_names(new_name_option, index=i+1))
            break

        alt_name += name[i]

    alt_name = "%" + ("%".join(alt_name))+"%"
    if condition:
        results.append(alt_name)

    return results


def search_elv_custom_sql_query(possible_names):
    from django.db import connection
    sql = """SELECT uid,nom_prenom,nom_pere,date_naissance,x_adminecoledata.ministre_school_name AS nom_ecole
                FROM x_adminelvs
                JOIN x_adminecoledata ON x_adminelvs.ecole_id = x_adminecoledata.sid
                where  nom_prenom LIKE %s """
    params = []
    params.append(possible_names[0])
    if len(possible_names) > 0:
        for i in range(1, len(possible_names)):
            sql += f" OR nom_prenom LIKE %s "
            params.append(possible_names[i])

    sql += ' ;'
    print(params)
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return rows




###################  the fuzzy method ######################

def search_by_fuzzy_algo(model, searched_name, threshold=80):
    matches = []
    for eleve in model:
        similarity_score = fuzz.ratio(searched_name, eleve[1])
        if similarity_score >= threshold:
            matches.append((eleve, similarity_score))
            # matches.append(obj_name)
    # Sort matches by similarity score
    matches.sort(key=lambda x: x[1], reverse=True)
    eleves = [match[0] for match in matches]
    return eleves


####################    mergin  the custom and fuzzy and get uniq result without any repetition #####################



def merge_arrays(array1, array2):
    merged_array = []
   
    # Add unique items from array1
    for obj in array1:
        if not any(item[0] == obj[0] for item in merged_array):
            merged_array.append(obj)

    # Add unique items from array2
    for obj in array2:
        if not any(item[0] == obj[0] for item in merged_array):
            merged_array.append(obj)

    return merged_array

    # seen_uids = set()  # Create a set to store seen "uid" values
    # unique_objects = []
    # for obj in array1:
    #     if obj["uid"] not in seen_uids:
    #         seen_uids.add(obj["uid"])
    #         unique_objects.append(obj)
    # for obj in array2:
    #     if obj["uid"] not in seen_uids:
    #         seen_uids.add(obj["uid"])
    #         unique_objects.append(obj)

    # return unique_objects
