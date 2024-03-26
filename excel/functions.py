from rest_framework.response import Response
from rest_framework import status
from excel.models import excelsheets

from excel.serializers import excelsheetsSerializer
from x.models import AdminEcoledata, AdminElvs


def add_remove_elv(level, ecole, add,cancel):

    level_mapping = {
        1: ecole.premiere,
        2: ecole.deuxieme,
        3: ecole.troisieme,
        4: ecole.quatrieme,
        5: ecole.cinquieme,
        6: ecole.sixieme,
    }
    if add:
        if not cancel:
            level_mapping[level].add_elv()
        else:
            level_mapping[level].cancel_add_elv()
    else:
        if not cancel:
            level_mapping[level].reduce_elv()
        else:
            level_mapping[level].cancel_reduce_elv()


def adjust_levelstat(ecole_removed_from_id: int, ecole_added_to_id: int, level: int,dre_id,cancel:bool):

    ecole_removed_from = AdminEcoledata.objects.filter(dre_id=dre_id).filter(sid=ecole_removed_from_id).first()
    if ecole_removed_from:
        add_remove_elv(level, ecole_removed_from, add=False,cancel=cancel)

    ecole_added_to = AdminEcoledata.objects.filter(dre_id=dre_id).filter(sid=ecole_added_to_id).first()
    if ecole_added_to:
        add_remove_elv(level, ecole_added_to, add=True,cancel=cancel)


def create_excelsheetRow(request_data,dre_id):
    excelsheet_row = excelsheetsSerializer(data=request_data)

    if not excelsheet_row.is_valid():
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

    excelsheet_row.validated_data['dre_id'] = dre_id  # ~ RAK7
    excelsheet_row.save()


def cancel_excelsheetRow(request_data,dre_id):
    try:
        excelsheetsrows = excelsheets.objects.filter(uid=request_data['uid'],prev_ecole_id=request_data['prev_ecole_id'],next_ecole_id=request_data['next_ecole_id'],date_downloaded=None,dre_id=dre_id)
        if len(excelsheetsrows) == 1:
            excelsheetsrows.first().delete()
            print('loula')
            return
        
        if len(excelsheetsrows) == 0:
            print('2')
            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
        
        one_row = excelsheetsrows.filter(nom_prenom=request_data['nom_prenom'],
                                nom_pere=request_data['nom_pere'],
                                date_naissance=request_data['date_naissance'],
                                level=request_data['level'],
                                prev_ecole=request_data['prev_ecole'],
                                Del1=request_data['Del1'],
                                next_ecole=request_data['next_ecole'],
                                reason=request_data['reason'],
                                decision=request_data['decision'],
                                comments=request_data['comments'],
                                ).first()
        print('3')
        if not excelsheetsrows :
            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
        print('4')
        one_row.delete()
        
    except:
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
    
