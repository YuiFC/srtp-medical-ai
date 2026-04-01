<template>
  <div class="page-container">
    <div class="page-header">
      <h1>⚖️ 对比分析</h1>
      <p>对比多模态AI（影像+报告）与纯文本LLM（仅报告）的解读效果差异</p>
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
                  <p>点击上传医学影像</p>
                  <p class="upload-hint">可选，不上传则纯文本对比</p>
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

        <div class="form-actions">
          <button
            class="btn-warning"
            @click="compareAnalysis"
            :disabled="loading || !form.reportText.trim()"
          >
            {{ loading ? '分析中...' : '开始对比分析' }}
          </button>
          <button class="btn-secondary" @click="resetForm">重置</button>
        </div>

        <div v-if="error" class="error-banner">
          ⚠️ {{ error }}
        </div>
      </div>

      <div v-if="result" class="result-section">
        <h3>📊 对比分析结果</h3>

        <div class="compare-grid">
          <div class="compare-box text-mode">
            <div class="compare-header">
              <span class="compare-icon">📄</span>
              <h4>纯文本LLM解读</h4>
              <span class="compare-tag">仅文本分析</span>
            </div>
            <div class="compare-content">
              <div class="compare-block">
                <h5>🔍 主要发现</h5>
                <p>{{ result.text_only.findings }}</p>
              </div>
              <div class="compare-block">
                <h5>💬 综合印象</h5>
                <p>{{ result.text_only.impression }}</p>
              </div>
              <div class="compare-block">
                <h5>📋 建议</h5>
                <p>{{ result.text_only.recommendations }}</p>
              </div>
            </div>
          </div>

          <div class="compare-box multimodal-mode">
            <div class="compare-header">
              <span class="compare-icon">🖼️</span>
              <h4>多模态AI解读</h4>
              <span class="compare-tag">影像+文本</span>
            </div>
            <div class="compare-content">
              <div class="compare-block">
                <h5>🔍 主要发现</h5>
                <p>{{ result.multimodal.findings }}</p>
              </div>
              <div class="compare-block">
                <h5>💬 综合印象</h5>
                <p>{{ result.multimodal.impression }}</p>
              </div>
              <div class="compare-block">
                <h5>📋 建议</h5>
                <p>{{ result.multimodal.recommendations }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="comparison-summary">
          <h4>📈 CheXpert 标签对比</h4>
          <div class="comparison-table-wrapper">
            <table class="comparison-table">
              <thead>
                <tr>
                  <th>标签</th>
                  <th>纯文本</th>
                  <th>多模态</th>
                  <th>差异</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(textVal, key) in result.text_only.chexpert_labels"
                  :key="key"
                >
                  <td>{{ formatLabelName(key) }}</td>
                  <td :class="labelCellClass(textVal)">{{ textVal || 'N/A' }}</td>
                  <td :class="labelCellClass(result.multimodal.chexpert_labels[key])">
                    {{ result.multimodal.chexpert_labels[key] || 'N/A' }}
                  </td>
                  <td>
                    <span
                      v-if="textVal !== result.multimodal.chexpert_labels[key]"
                      class="diff-badge"
                    >有差异</span>
                    <span v-else class="same-badge">一致</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="result-note">
          ⚠️ 本分析仅供参考，不作为医疗诊断依据
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const loading = ref(false)
const fileInput = ref(null)
const result = ref(null)
const error = ref('')

const form = reactive({
  imageData: null,
  imagePreview: '',
  imageName: '',
  reportText: ''
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
    form.imagePreview = ev.target.result
    form.imageData = ev.target.result.split(',')[1]
  }
  reader.readAsDataURL(file)
}

const removeImage = () => {
  form.imageData = null
  form.imagePreview = ''
  form.imageName = ''
  if (fileInput.value) fileInput.value.value = ''
}

const compareAnalysis = async () => {
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

    const res = await fetch('/api/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!res.ok) {
      const errData = await res.json().catch(() => ({ detail: '未知错误' }))
      throw new Error(errData.detail || `请求失败 (${res.status})`)
    }

    result.value = await res.json()
  } catch (err) {
    error.value = err.message || '对比分析失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  removeImage()
  form.reportText = ''
  result.value = null
  error.value = ''
}

const labelCellClass = (value) => {
  if (value === 'positive') return 'cell-positive'
  if (value === 'negative') return 'cell-negative'
  if (value === 'uncertain') return 'cell-uncertain'
  return 'cell-na'
}

const formatLabelName = (key) => {
  return key.replace(/([A-Z])/g, ' $1').trim()
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

.content-card { max-width: 1100px; margin: 0 auto; padding: 0 20px 60px; }

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

.upload-area:hover { border-color: #ff9500; background: #fffaf5; }

.upload-placeholder { color: #86868b; }
.upload-icon { font-size: 48px; display: block; margin-bottom: 12px; }
.upload-hint { font-size: 13px; color: #a1a1a6; }

.upload-preview { width: 100%; }
.preview-image { max-width: 100%; max-height: 140px; border-radius: 8px; margin-bottom: 8px; }
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

.form-textarea:focus { outline: none; border-color: #ff9500; }

.form-actions { display: flex; justify-content: center; gap: 12px; margin-top: 24px; }

.btn-warning {
  padding: 14px 36px;
  background: #ff9500;
  color: white;
  border: none;
  border-radius: 980px;
  font-size: 17px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-warning:hover:not(:disabled) { background: #ff8f00; }
.btn-warning:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-secondary {
  padding: 14px 28px;
  background: transparent;
  color: #ff9500;
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

.compare-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 40px;
}

.compare-box { border-radius: 16px; padding: 24px; }
.text-mode { background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); }
.multimodal-mode { background: linear-gradient(135deg, #e8f5e9 0%, #e0f2f1 100%); }

.compare-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.compare-icon { font-size: 24px; }
.compare-header h4 { font-size: 17px; font-weight: 600; color: #1d1d1f; flex: 1; }

.compare-tag {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 500;
}

.text-mode .compare-tag { background: #0071e3; color: white; }
.multimodal-mode .compare-tag { background: #34c759; color: white; }

.compare-content { display: flex; flex-direction: column; gap: 16px; }

.compare-block h5 {
  font-size: 13px;
  font-weight: 600;
  color: #86868b;
  margin-bottom: 6px;
}

.compare-block p {
  font-size: 14px;
  line-height: 1.7;
  color: #1d1d1f;
  margin: 0;
}

.comparison-summary h4 {
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 20px;
}

.comparison-table-wrapper {
  overflow-x: auto;
  border-radius: 12px;
  background: #fafafa;
}

.comparison-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 500px;
}

.comparison-table th,
.comparison-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid #e5e5e5;
  font-size: 14px;
}

.comparison-table th {
  background: #f0f0f0;
  font-weight: 600;
  font-size: 13px;
  color: #86868b;
}

.comparison-table td { color: #1d1d1f; }

.cell-positive { color: #c0392b; font-weight: 600; }
.cell-negative { color: #27ae60; font-weight: 600; }
.cell-uncertain { color: #e67e22; font-weight: 600; }
.cell-na { color: #999; }

.diff-badge {
  display: inline-block;
  padding: 2px 8px;
  background: #fff3cd;
  color: #856404;
  border-radius: 8px;
  font-size: 12px;
}

.same-badge {
  display: inline-block;
  padding: 2px 8px;
  background: #eaf7ea;
  color: #155724;
  border-radius: 8px;
  font-size: 12px;
}

.result-note {
  background: #fff3cd;
  border-radius: 12px;
  padding: 16px 20px;
  color: #856404;
  font-size: 14px;
  margin-top: 24px;
}

@media (max-width: 768px) {
  .form-row, .compare-grid { grid-template-columns: 1fr; }
  .page-header h1 { font-size: 28px; }
  .form-section, .result-section { padding: 24px; }
}
</style>
