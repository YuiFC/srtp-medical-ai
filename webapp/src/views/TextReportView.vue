<template>
  <div class="page-container">
    <div class="page-header">
      <h1>📄 放射学报告文本解读</h1>
      <p>输入放射学报告，使用LLM进行智能解读分析</p>
    </div>

    <div class="content-card">
      <div class="form-section">
        <div class="form-group">
          <label class="form-label">放射学报告文本</label>
          <textarea 
            v-model="form.reportText" 
            class="form-textarea"
            placeholder="请输入放射学报告内容...

例如：胸部CT检查：双肺可见多个大小不等结节，最大者位于右肺上叶，直径约1.2cm，边界清晰..."
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
          <button class="btn-primary" @click="analyzeReport" :disabled="loading">
            {{ loading ? '分析中...' : 'AI解读分析' }}
          </button>
          <button class="btn-secondary" @click="resetForm">重置</button>
        </div>
      </div>

      <div v-if="result" class="result-section">
        <h3>📊 AI解读结果</h3>
        <div class="result-content" v-html="result"></div>
        <div class="result-actions">
          <button class="btn-outline" @click="saveResult">保存结果</button>
          <button class="btn-outline" @click="copyResult">复制</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const loading = ref(false)
const result = ref('')

const form = reactive({
  reportText: '',
  examType: ''
})

const analyzeReport = async () => {
  if (!form.reportText) {
    alert('请输入报告文本')
    return
  }
  
  loading.value = true
  
  // 模拟API调用
  setTimeout(() => {
    const examTypeName = {
      chest_xray: '胸部X光',
      chest_ct: '胸部CT',
      abdomen_ct: '腹部CT',
      head_ct: '头颅CT',
      other: '其他'
    }[form.examType] || '未指定'
    
    result.value = `
      <div class="result-item">
        <h4>🔍 报告分析</h4>
        <p><strong>检查类型：</strong>${examTypeName}</p>
      </div>
      <div class="result-item">
        <h4>📋 主要发现</h4>
        <p>${form.reportText.substring(0, 300)}${form.reportText.length > 300 ? '...' : ''}</p>
      </div>
      <div class="result-item">
        <h4>💡 健康建议</h4>
        <ul>
          <li>建议定期复查，监测病情变化</li>
          <li>如有不适，请及时就医</li>
          <li>保持健康生活方式</li>
        </ul>
      </div>
      <div class="result-note">
        <h4>🧠 解读说明</h4>
        <p>本分析基于纯文本LLM，仅供参考，不作为医疗诊断依据。</p>
      </div>
    `
    loading.value = false
    alert('分析完成')
  }, 1500)
}

const resetForm = () => {
  form.reportText = ''
  form.examType = ''
  result.value = ''
}

const saveResult = () => {
  const blob = new Blob([result.value.replace(/<[^>]*>/g, '')], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `medical-report-analysis-${Date.now()}.txt`
  a.click()
  URL.revokeObjectURL(url)
}

const copyResult = () => {
  const text = result.value.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim()
  navigator.clipboard.writeText(text).then(() => {
    alert('已复制到剪贴板')
  }).catch(() => {
    alert('复制失败，请手动复制')
  })
}
</script>

<style scoped>
.page-container {
  width: 100%;
  max-width: 100%;
}

.page-header {
  text-align: center;
  padding: 60px 20px 40px;
  background: linear-gradient(180deg, #f5f5f7 0%, white 100%);
}

.page-header h1 {
  font-size: 40px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 12px;
}

.page-header p {
  font-size: 19px;
  color: #86868b;
}

.content-card {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 20px 60px;
}

.form-section {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}

.form-group {
  margin-bottom: 24px;
}

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

.form-textarea:focus {
  outline: none;
  border-color: #0071e3;
}

.form-select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #d2d2d7;
  border-radius: 12px;
  font-size: 15px;
  background: white;
  cursor: pointer;
}

.form-select:focus {
  outline: none;
  border-color: #0071e3;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
}

.btn-primary {
  padding: 14px 28px;
  background: #0071e3;
  color: white;
  border: none;
  border-radius: 980px;
  font-size: 17px;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover:not(:disabled) {
  background: #0077ed;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 14px 28px;
  background: transparent;
  color: #0071e3;
  border: none;
  font-size: 17px;
  cursor: pointer;
}

.btn-secondary:hover {
  text-decoration: underline;
}

.result-section {
  margin-top: 40px;
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}

.result-section h3 {
  font-size: 22px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 24px;
}

.result-content {
  line-height: 1.8;
  color: #1d1d1f;
}

.result-content :deep(.result-item) {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f5f5f7;
}

.result-content :deep(.result-item:last-child) {
  border-bottom: none;
}

.result-content :deep(h4) {
  font-size: 17px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 12px;
}

.result-content :deep(ul) {
  padding-left: 20px;
}

.result-content :deep(li) {
  margin-bottom: 8px;
  color: #86868b;
}

.result-note {
  background: #f5f5f7;
  border-radius: 12px;
  padding: 20px;
  margin-top: 20px;
}

.result-note h4 {
  font-size: 15px;
  font-weight: 600;
  color: #86868b;
  margin-bottom: 8px;
}

.result-note p {
  font-size: 14px;
  color: #86868b;
}

.result-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

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

.btn-outline:hover {
  background: #0071e3;
  color: white;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 28px;
  }
  
  .form-section,
  .result-section {
    padding: 24px;
  }
}
</style>