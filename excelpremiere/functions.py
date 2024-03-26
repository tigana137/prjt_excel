from rest_framework.response import Response
from rest_framework import status

from excel.serializers import excelsheetsSerializer
from excelpremiere.models import excelsheetsPremiere
from excelpremiere.serializers import excelsheetsSerializerPremiere
from x.models import AdminEcoledata









def create_excelsheetRowPremiere(request_data,dre_id):
    excelsheet_row = excelsheetsSerializerPremiere(data=request_data)

    if not excelsheet_row.is_valid():
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)

    excelsheet_row.validated_data['dre_id'] = dre_id  # ~ RAK7
    excelsheet_row.save()


def cancel_excelsheetRowPremiere(request_data,dre_id):
    try:
        excelsheetsrows = excelsheetsPremiere.objects.filter(uid=request_data['uid'],prev_ecole_id=request_data['prev_ecole_id'],next_ecole_id=request_data['next_ecole_id'],date_downloaded=None,dre_id=dre_id)
        if len(excelsheetsrows) == 1:
            excelsheetsrows.first().delete()
            return
        
        if len(excelsheetsrows) == 0:
            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
        
        excelsheetsrows.filter( nom=request_data['nom'],
                                prenom=request_data['prenom'],
                                date_naissance=request_data['date_naissance'],
                                prev_ecole=request_data['prev_ecole'],
                                Del1=request_data['Del1'],
                                next_ecole=request_data['next_ecole'],
                                reason=request_data['reason'],
                                decision=request_data['decision'],
                                comments=request_data['comments'],
                                ).first()
        
        if not excelsheetsrows :
            return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
        excelsheetsrows.delete()
        
    except:
        return Response({'success': False}, status=status.HTTP_400_BAD_REQUEST)
    