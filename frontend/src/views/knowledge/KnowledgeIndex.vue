<script setup>
import { onMounted, ref } from 'vue'
import api from '@/js/http/api.js'

const documents = ref([])
const uploading = ref(false)
const uploadError = ref('')
const uploadSuccess = ref('')

const ALLOWED_EXTENSIONS = '.pdf,.docx,.txt,.md,.csv'

async function loadDocuments() {
  try {
    const res = await api.get('/api/knowledge/document/list/')
    if (res.data.result === 'success') {
      documents.value = res.data.documents
    }
  } catch (e) {
    // silently fail
  }
}

async function handleUpload(e) {
  const file = e.target.files?.[0]
  if (!file) return

  uploadError.value = ''
  uploadSuccess.value = ''
  uploading.value = true

  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post('/api/knowledge/document/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    if (res.data.result === 'success') {
      uploadSuccess.value = `"${file.name}" 上传成功，已切分为 ${res.data.chunk_count} 个片段`
      await loadDocuments()
    } else {
      uploadError.value = res.data.result
    }
  } catch (e) {
    uploadError.value = '上传失败，请稍后重试'
  } finally {
    uploading.value = false
    e.target.value = ''
  }
}

async function removeDocument(docId) {
  try {
    const res = await api.post('/api/knowledge/document/remove/', { document_id: docId })
    if (res.data.result === 'success') {
      documents.value = documents.value.filter(d => d.id !== docId)
    }
  } catch (e) {
    // silently fail
  }
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

onMounted(() => {
  loadDocuments()
})
</script>

<template>
  <div class="flex flex-col items-center px-4 py-8 max-w-3xl mx-auto">
    <h1 class="text-2xl font-bold mb-8">知识库管理</h1>

    <!-- 上传区 -->
    <div class="card bg-base-200 w-full mb-8">
      <div class="card-body">
        <h2 class="card-title text-lg">上传文档</h2>
        <p class="text-sm text-gray-500 mb-3">支持 PDF、Word、Markdown、TXT、CSV 格式</p>

        <div class="flex items-center gap-4">
          <input
            type="file"
            :accept="ALLOWED_EXTENSIONS"
            :disabled="uploading"
            @change="handleUpload"
            class="file-input file-input-bordered w-full max-w-xs"
          />
          <span v-if="uploading" class="loading loading-spinner loading-md"></span>
        </div>

        <div v-if="uploadError" class="alert alert-error mt-3">{{ uploadError }}</div>
        <div v-if="uploadSuccess" class="alert alert-success mt-3">{{ uploadSuccess }}</div>
      </div>
    </div>

    <!-- 文档列表 -->
    <div class="w-full">
      <h2 class="text-lg font-semibold mb-4">已上传文档（{{ documents.length }}）</h2>

      <div v-if="documents.length === 0" class="text-center text-gray-500 py-12">
        暂无文档，请上传
      </div>

      <div v-else class="overflow-x-auto">
        <table class="table table-zebra">
          <thead>
            <tr>
              <th>文件名</th>
              <th>类型</th>
              <th>大小</th>
              <th>分片数</th>
              <th>状态</th>
              <th>上传时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="doc in documents" :key="doc.id">
              <td class="max-w-48 truncate">{{ doc.filename }}</td>
              <td>
                <span class="badge badge-sm">{{ doc.file_type.toUpperCase() }}</span>
              </td>
              <td>{{ formatFileSize(doc.file_size) }}</td>
              <td>{{ doc.chunk_count }}</td>
              <td>
                <span v-if="doc.status === 'ready'" class="badge badge-success badge-sm">就绪</span>
                <span v-else-if="doc.status === 'processing'" class="badge badge-warning badge-sm">处理中</span>
                <span v-else class="badge badge-error badge-sm" :title="doc.error_message">失败</span>
              </td>
              <td class="text-sm">{{ doc.create_time }}</td>
              <td>
                <button class="btn btn-ghost btn-sm text-error" @click="removeDocument(doc.id)">
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
