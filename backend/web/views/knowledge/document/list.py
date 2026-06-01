from django.utils.timezone import localtime
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from web.models.knowledge import KnowledgeDocument
from web.models.user import UserProfile


class ListDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            docs = KnowledgeDocument.objects.filter(user=user_profile).order_by('-create_time')

            data = [{
                'id': doc.id,
                'filename': doc.filename,
                'file_type': doc.file_type,
                'file_size': doc.file_size,
                'chunk_count': doc.chunk_count,
                'status': doc.status,
                'error_message': doc.error_message,
                'create_time': localtime(doc.create_time).strftime('%Y-%m-%d %H:%M:%S'),
            } for doc in docs]

            return Response({'result': 'success', 'documents': data})

        except Exception:
            return Response({'result': '系统异常，请稍后重试'})
