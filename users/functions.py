from rest_framework import status
import datetime
from rest_framework.response import Response
import jwt


def create_jwtResponse(dre_id):
    jwt_payload = {
        'dre_id': dre_id,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow()+datetime.timedelta(minutes=600),
    }

    token = jwt.encode(jwt_payload, 'secret', algorithm='HS256')

    respone = Response()
    respone.set_cookie(key='jwt', value=token, httponly=True)
    respone.data = {'success': True, }

    return respone


def verify_jwt(request):
    token = request.COOKIES.get('jwt')
    if not token:
        return Response(status=status.HTTP_403_FORBIDDEN)

    try:
        jwt_payload = jwt.decode(token, 'secret', algorithms='HS256')
    except jwt.ExpiredSignatureError:
        # hedhi chouf l noumrou t3 http t3ha wel msg l tb3thou w ki t expiry kifh t3awd jwt o5ra
        return Response({"auth": "Not auth."}, status=status.HTTP_401_UNAUTHORIZED)

    return jwt_payload
