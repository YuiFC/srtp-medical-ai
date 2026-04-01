<template>
  <div class="page-container">
    <div class="page-header">
      <h1>📄 放射学报告文本解读</h1>
      <p>输入放射学报告，使用GLM-4.6V进行智能解读分析</p>
    </div>

    <div class="content-card">
      <div class="form-section">
        <div class="form-group">
          <label class="form-label">放射学报告文本</label>
          <textarea
            v-model="form.reportText"
            class="form-textarea"
            placeholder="请输入放射学报告内容...

例如：PA and lateral chest radiographs demonstrate hyperinflated lungs with flattening of the diaphragms. No focal consolidation or pleural effusion is identified."
          ></textarea>
        </div>

        <div class="form-group">
          <label class="form-label">检查类型</label>
          <select v-model="form.examType" class="form-select">
            <option value="">请选择检查类型</option>
            <option value="chest_xray">胸部X光</option>
            <option value="chest_ct">胸部CT</option>
            <option value="abdomen_ct">腹部CT</option>
            <option value="head_ct">头颅CT</option>
            <option value="other">其他</option>
          </select>
        </div>

        <div class="form-actions">
          <button class="btn-primary" @click="analyzeReport" :disabled="loading || !form.reportText.trim()">
            {{ loading ? '分析中...' : 'AI解读分析' }}
          </button>
          <button class="btn-secondary" @click="resetForm">重置</button>
        </div>

        <div v-if="error" class="error-banner">
          ⚠️ {{ error }}
        </div>
      </div>

      <div v-if="result" class="result-section">
        <h3>📊 AI解读结果</h3>

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
          <h4>🧠 解读说明</h4>
          <p>本分析基于纯文本LLM（GLM-4.6V），仅供参考，不作为医疗诊断依据。</p>
        </div>

        <div class="result-actions">
          <button class="btn-outline" @click="copyResult">复制结果</button>
          <button class="btn-outline" @click="saveResult">保存结果</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const loading = ref(false)
const activeTab = ref('findings')
const result = ref(null)
const error = ref('')

const form = reactive({
  reportText: '',
  examType: ''
})

const analyzeReport = async () => {
  error.value = ''
  if (!form.reportText.trim()) {
    error.value = '请输入报告文本'
    return
  }

  loading.value = true

  try {
    const res = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        report_text: form.reportText,
        mode: 'text_only',
      }),
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
  return key.replace(/([A-Z])/g, ' $1').trim()
}

const copyResult = () => {
  if (!result.value) return
  const text = `【主要发现】\n${result.value.findings}\n\n【综合印象】\n${result.value.impression}\n\n【建议】\n${result.value.recommendations}`
  navigator.clipboard.writeText(text).then(() => {
    alert('已复制到剪贴板')
  })
}

const saveResult = () => {
  if (!result.value) return
  const text = `【主要发现】\n${result.value.findings}\n\n【综合印象】\n${result.value.impression}\n\n【建议】\n${result.value.recommendations}\n\n【CheXpert标签】\n${JSON.stringify(result.value.chexpert_labels, null, 2)}`
  const blob = new Blob([text], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `medical-report-analysis-${Date.now()}.txt`
  a.click()
  URL.revokeObjectURL(url)
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

.content-card { max-width: 800px; margin: 0 auto; padding: 0 20px 60px; }

.form-section {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}

.form-group { margin-bottom: 24px; }

.form-label {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 8px;
}

.form-textarea {
  width: 100%;
  min-height: 200px;
  padding: 16px;
  border: 1px solid #d2d2d7;
  border-radius: 12px;
  font-size: 15px;
  font-family: inherit;
  line-height: 1.5;
  resize: vertical;
  transition: border-color 0.3s;
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
  background: #0071e3;
  color: white;
  border: none;
  border-radius: 980px;
  font-size: 17px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover:not(:disabled) { background: #0077ed; }
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
  background: #f5f5f7;
  border-radius: 12px;
  padding: 20px;
  margin-top: 24px;
}

.result-note h4 { font-size: 15px; font-weight: 600; color: #86868b; margin-bottom: 8px; }
.result-note p { font-size: 14px; color: #86868b; }

.result-actions { display: flex; gap: 12px; margin-top: 16px; }

.btn-outline {
  padding: 12px 24px;
  background: transparent;
  color: #0071e3;
  border: 1px solid #0071e3;
  border-radius: 980px;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-outline:hover { background: #0071e3; color: white; }

@media (max-width: 768px) {
  .page-header h1 { font-size: 28px; }
  .form-section, .result-section { padding: 24px; }
}
</style>
