from http.client import responses

from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


class RefreshTokenView(APIView):
    def post(self,request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")
            if not refresh_token:
                return Response({
                    "result" : "refresh_token不存在"
                },status=401)   #必须加401
            refresh = RefreshToken(refresh_token)   #如果refresh_token过期了会报异常
            if settings.SIMPLE_JWT['ROTATE_REFRESH_TOKENS']:
                refresh.set_jti()
                responses = Response({
                    "result": "success",
                    "access": str(refresh.access_token),
                })
                responses.set_cookie(
                    key="refresh_token",
                    value=str(refresh),
                    httponly=True,
                    samesite="Lax",
                    secure=True,
                    max_age=86400 * 7,
                )
                return responses
            return Response({
                "result": "success",
                "access": str(refresh.access_token),
            })
        except:
            return Response({
                "result" : "refresh token过期了"
            },status=401)   #必须加401
