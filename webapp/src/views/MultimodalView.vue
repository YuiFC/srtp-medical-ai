<template>
  <div class="page-container">
    <div class="page-header">
      <h1>🖼️ 多模态AI解读</h1>
      <p>上传医学影像 + 报告文本，多模态AI联合分析</p>
    </div>

    <div class="content-card">
      <div class="form-section">
        <div class="form-row">
          <div class="form-col">
            <div class="form-group">
              <label class="form-label">上传医学影像</label>
              <div class="upload-area" @click="triggerUpload">
                <input
                  type="file"
                  ref="fileInput"
                  @change="handleFileChange"
                  accept="image/*"
                  style="display: none"
                >
                <div v-if="!form.imageData" class="upload-placeholder">
                  <span class="upload-icon">📁</span>
                  <p>点击上传或拖拽文件</p>
                  <p class="upload-hint">支持 X光、CT 等医学影像</p>
                </div>
                <div v-else class="upload-preview">
                  <img :src="form.imagePreview" class="preview-image" alt="预览">
                  <div class="preview-info">
                    <span class="preview-name">{{ form.imageName }}</span>
                    <span class="preview-remove" @click.stop="removeImage">×</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="form-col">
            <div class="form-group">
              <label class="form-label">放射学报告文本</label>
              <textarea
                v-model="form.reportText"
                class="form-textarea"
                placeholder="请输入报告文本..."
              ></textarea>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">检查类型</label>
          <select v-model="form.examType" class="form-select">
            <option value="">请选择检查类型</option>
            <option value="chest_xray">胸部X光</option>
            <option value="chest_ct">胸部CT</option>
            <option value="abdomen_ct">腹部CT</option>
            <option value="head_ct">头颅CT</option>
          </select>
        </div>

        <div class="form-actions">
          <button class="btn-primary" @click="analyzeMultimodal" :disabled="loading || !canAnalyze">
            {{ loading ? '分析中...' : '多模态AI联合分析' }}
          </button>
          <button class="btn-secondary" @click="resetForm">重置</button>
        </div>

        <div v-if="error" class="error-banner">
          ⚠️ {{ error }}
        </div>
      </div>

      <div v-if="result" class="result-section">
        <h3>🧠 多模态AI分析结果</h3>

        <div class="result-tabs">
          <button
            :class="['tab-btn', { active: activeTab === 'findings' }]"
            @click="activeTab = 'findings'"
          >
            🔍 主要发现
          </button>
          <button
            :class="['tab-btn', { active: activeTab === 'impression' }]"
            @click="activeTab = 'impression'"
          >
            💬 综合印象
          </button>
          <button
            :class="['tab-btn', { active: activeTab === 'recommendations' }]"
            @click="activeTab = 'recommendations'"
          >
            📋 建议
          </button>
          <button
            :class="['tab-btn', { active: activeTab === 'labels' }]"
            @click="activeTab = 'labels'"
          >
            🏷️ CheXpert标签
          </button>
        </div>

        <div class="tab-content">
          <div v-show="activeTab === 'findings'">
            <div class="result-text">{{ result.findings }}</div>
          </div>
          <div v-show="activeTab === 'impression'">
            <div class="result-text">{{ result.impression }}</div>
          </div>
          <div v-show="activeTab === 'recommendations'">
            <div class="result-text">{{ result.recommendations }}</div>
          </div>
          <div v-show="activeTab === 'labels'">
            <div class="labels-grid">
              <div
                v-for="(value, key) in result.chexpert_labels"
                :key="key"
                :class="['label-item', labelClass(value)]"
              >
                <span class="label-name">{{ formatLabelName(key) }}</span>
                <span class="label-value">{{ value || 'N/A' }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="result-note">
          ⚠️ 本分析仅供参考，不作为医疗诊断依据
        </div>

        <div class="result-actions">
          <button class="btn-outline" @click="copyResult">复制结果</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'

const loading = ref(false)
const activeTab = ref('findings')
const fileInput = ref(null)
const result = ref(null)
const error = ref('')

const form = reactive({
  imageData: null,      // base64 string
  imagePreview: '',     // data URL for preview
  imageName: '',
  reportText: '',
  examType: ''
})

const canAnalyze = computed(() => {
  return form.reportText.trim().length > 0
})

const triggerUpload = () => {
  fileInput.value.click()
}

const handleFileChange = (e) => {
  const file = e.target.files[0]
  if (!file) return

  form.imageName = file.name

  const reader = new FileReader()
  reader.onload = (ev) => {
    const dataUrl = ev.target.result
    form.imagePreview = dataUrl
    // 去掉 data:image/...;base64, 前缀，取纯base64
    const base64 = dataUrl.split(',')[1]
    form.imageData = base64
  }
  reader.readAsDataURL(file)
}

const removeImage = () => {
  form.imageData = null
  form.imagePreview = ''
  form.imageName = ''
  if (fileInput.value) fileInput.value.value = ''
}

const analyzeMultimodal = async () => {
  error.value = ''
  if (!form.reportText.trim()) {
    error.value = '请输入报告文本'
    return
  }

  loading.value = true

  try {
    const payload = {
      report_text: form.reportText,
      mode: 'multimodal',
    }
    if (form.imageData) {
      payload.image_base64 = form.imageData
    }

    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: '未知错误' }))
      throw new Error(errData.detail || `请求失败 (${res.status})`)
    }

    const data = await res.json()
    result.value = data
    activeTab.value = 'findings'
  } catch (err) {
    error.value = err.message || '分析失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  removeImage()
  form.reportText = ''
  form.examType = ''
  result.value = null
  error.value = ''
  activeTab.value = 'findings'
}

const labelClass = (value) => {
  if (value === 'positive') return 'label-positive'
  if (value === 'negative') return 'label-negative'
  if (value === 'uncertain') return 'label-uncertain'
  return 'label-na'
}

const formatLabelName = (key) => {
  // CamelCase转空格分隔
  return key.replace(/([A-Z])/g, ' $1').trim()
}

const copyResult = () => {
  if (!result.value) return
  const text = `【主要发现】\n${result.value.findings}\n\n【综合印象】\n${result.value.impression}\n\n【建议】\n${result.value.recommendations}`
  navigator.clipboard.writeText(text).then(() => {
    alert('已复制到剪贴板')
  })
}
</script>

<style scoped>
.page-container { width: 100%; max-width: 100%; }

.page-header {
  text-align: center;
  padding: 60px 20px 40px;
  background: linear-gradient(180deg, #f5f5f7 0%, white 100%);
}

.page-header h1 { font-size: 40px; font-weight: 600; color: #1d1d1f; margin-bottom: 12px; }
.page-header p { font-size: 19px; color: #86868b; }

.content-card { max-width: 1000px; margin: 0 auto; padding: 0 20px 60px; }

.form-section {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
.form-col { display: flex; flex-direction: column; }
.form-group { margin-bottom: 24px; flex: 1; }

.form-label {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 8px;
}

.upload-area {
  border: 2px dashed #d2d2d7;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover { border-color: #0071e3; background: #f9f9f9; }

.upload-placeholder { color: #86868b; }
.upload-icon { font-size: 48px; display: block; margin-bottom: 12px; }
.upload-hint { font-size: 13px; color: #a1a1a6; }

.upload-preview { width: 100%; }
.preview-image { max-width: 100%; max-height: 160px; border-radius: 8px; margin-bottom: 8px; }
.preview-info { display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #f5f5f7; border-radius: 8px; }
.preview-name { font-size: 13px; color: #1d1d1f; }
.preview-remove { font-size: 20px; color: #86868b; cursor: pointer; }

.form-textarea {
  width: 100%;
  min-height: 180px;
  padding: 16px;
  border: 1px solid #d2d2d7;
  border-radius: 12px;
  font-size: 15px;
  font-family: inherit;
  line-height: 1.5;
  resize: vertical;
}

.form-textarea:focus { outline: none; border-color: #0071e3; }

.form-select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d2d2d7;
  border-radius: 12px;
  font-size: 15px;
  background: white;
  cursor: pointer;
}

.form-select:focus { outline: none; border-color: #0071e3; }

.form-actions { display: flex; gap: 12px; margin-top: 32px; }

.btn-primary {
  padding: 14px 28px;
  background: #34c759;
  color: white;
  border: none;
  border-radius: 980px;
  font-size: 17px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover:not(:disabled) { background: #30b350; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-secondary {
  padding: 14px 28px;
  background: transparent;
  color: #0071e3;
  border: none;
  font-size: 17px;
  cursor: pointer;
}

.btn-secondary:hover { text-decoration: underline; }

.error-banner {
  margin-top: 16px;
  padding: 12px 16px;
  background: #fff0f0;
  border: 1px solid #ffcccc;
  border-radius: 8px;
  color: #cc0000;
  font-size: 14px;
}

.result-section {
  margin-top: 40px;
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}

.result-section h3 { font-size: 22px; font-weight: 600; color: #1d1d1f; margin-bottom: 24px; }

.result-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 1px solid #e5e5e5;
  padding-bottom: 16px;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 10px 20px;
  background: transparent;
  border: none;
  border-radius: 20px;
  font-size: 15px;
  color: #86868b;
  cursor: pointer;
  transition: all 0.3s;
}

.tab-btn.active { background: #0071e3; color: white; }

.tab-content { line-height: 1.8; color: #1d1d1f; }

.result-text { font-size: 16px; line-height: 1.8; color: #1d1d1f; }

.labels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.label-item {
  display: flex;
  flex-direction: column;
  padding: 12px 16px;
  border-radius: 12px;
  gap: 4px;
}

.label-positive { background: #ffeaea; border: 1px solid #ffcccc; }
.label-negative { background: #eaf7ea; border: 1px solid #ccffcc; }
.label-uncertain { background: #fff8e6; border: 1px solid #ffe4a0; }
.label-na { background: #f5f5f7; border: 1px solid #e5e5e5; }

.label-name { font-size: 12px; color: #86868b; }
.label-value { font-size: 15px; font-weight: 600; color: #1d1d1f; text-transform: capitalize; }

.result-note {
  background: #fff3cd;
  border-radius: 12px;
  padding: 16px 20px;
  color: #856404;
  font-size: 14px;
  margin-top: 24px;
}

.result-actions { display: flex; gap: 12px; margin-top: 16px; }

.btn-outline {
  padding: 12px 24px;
  background: transparent;
  color: #0071e3;
  border: 1px solid #0071e3;
  border-radius: 980px;
  font-size: 15px;
  cursor: pointer;
}

.btn-outline:hover { background: #0071e3; color: white; }

@media (max-width: 768px) {
  .form-row { grid-template-columns: 1fr; }
  .page-header h1 { font-size: 28px; }
  .form-section, .result-section { padding: 24px; }
}
</style>
