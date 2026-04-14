from http.client import responses

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]      #强制必须登录才能访问
    def post(self,request):
        responses = Response({
            "result": "success"
        })
        responses.delete_cookie("refresh_token")
        return responses


