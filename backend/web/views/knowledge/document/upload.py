import os

import lancedb
from django.conf import settings
from langchain_community.vectorstores import LanceDB
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from web.documents.utils.custom_embeddings import CustomEmbeddings
from web.documents.utils.document_loader import load_document
from web.models.knowledge import KnowledgeDocument, KnowledgeChunk
from web.models.user import UserProfile

ALLOWED_TYPES = {'pdf', 'docx', 'txt', 'md', 'csv'}


class UploadDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            user_profile = UserProfile.objects.get(user=user)
            file = request.FILES.get('file')

            if not file:
                return Response({'result': '请选择文件'})

            ext = file.name.split('.')[-1].lower()
            if ext not in ALLOWED_TYPES:
                return Response({'result': f'不支持的文件类型: .{ext}'})

            doc = KnowledgeDocument.objects.create(
                user=user_profile,
                filename=file.name,
                file_type=ext,
                file=file,
                file_size=file.size,
                status='processing'
            )

            try:
                file_path = doc.file.path
                documents = load_document(file_path, ext)

                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=500, chunk_overlap=50
                )
                texts = text_splitter.split_documents(documents)

                if not texts:
                    doc.status = 'error'
                    doc.error_message = '文档内容为空，无法提取有效文本'
                    doc.save()
                    return Response({'result': '文档内容为空，无法提取有效文本'})

                for i, text in enumerate(texts):
                    text.metadata = {
                        'document_id': doc.id,
                        'chunk_index': i,
                    }

                embeddings = CustomEmbeddings()
                lancedb_path = os.path.join(settings.BASE_DIR, 'web', 'documents', 'lancedb_storage')
                db = lancedb.connect(lancedb_path)
                mode = 'append' if 'my_knowledge_base' in db.table_names() else 'overwrite'
                LanceDB.from_documents(
                    documents=texts,
                    embedding=embeddings,
                    connection=db,
                    table_name='my_knowledge_base',
                    mode=mode,
                )

                KnowledgeChunk.objects.bulk_create([
                    KnowledgeChunk(
                        document=doc,
                        chunk_index=i,
                        content=text.page_content
                    )
                    for i, text in enumerate(texts)
                ])

                doc.chunk_count = len(texts)
                doc.status = 'ready'
                doc.save()

                return Response({
                    'result': 'success',
                    'document_id': doc.id,
                    'chunk_count': len(texts),
                })

            except Exception as e:
                doc.status = 'error'
                doc.error_message = str(e)
                doc.save()
                return Response({'result': f'文档处理失败: {str(e)}'})

        except Exception:
            return Response({'result': '系统异常，请稍后重试'})
