import os

import lancedb
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from web.models.knowledge import KnowledgeDocument
from web.models.user import UserProfile


class RemoveDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            doc_id = request.data.get('document_id')

            if not doc_id:
                return Response({'result': '缺少 document_id'})

            doc = KnowledgeDocument.objects.filter(id=doc_id, user=user_profile).first()
            if not doc:
                return Response({'result': '文档不存在'})

            # 从 LanceDB 删除向量
            try:
                lancedb_path = os.path.join(settings.BASE_DIR, 'web', 'documents', 'lancedb_storage')
                db = lancedb.connect(lancedb_path)
                if 'my_knowledge_base' in db.table_names():
                    table = db.open_table('my_knowledge_base')
                    table.delete(f"document_id = {doc.id}")
            except Exception:
                pass

            # 删除磁盘文件
            if doc.file and os.path.isfile(doc.file.path):
                os.remove(doc.file.path)

            # 级联删除 chunks 和 document
            doc.delete()

            return Response({'result': 'success'})

        except Exception:
            return Response({'result': '系统异常，请稍后重试'})
