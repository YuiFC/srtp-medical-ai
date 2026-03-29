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
                  multiple
                  style="display: none"
                >
                <div v-if="form.imageList.length === 0" class="upload-placeholder">
                  <span class="upload-icon">📁</span>
                  <p>点击上传或拖拽文件</p>
                  <p class="upload-hint">支持 X光、CT 等医学影像</p>
                </div>
                <div v-else class="upload-preview">
                  <div v-for="(img, idx) in form.imageList" :key="idx" class="preview-item">
                    <span class="preview-name">{{ img.name }}</span>
                    <span class="preview-remove" @click.stop="removeImage(idx)">×</span>
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
          <button class="btn-primary" @click="analyzeMultimodal" :disabled="loading">
            {{ loading ? '分析中...' : '多模态AI联合分析' }}
          </button>
          <button class="btn-secondary" @click="resetForm">重置</button>
        </div>
      </div>

      <div v-if="result" class="result-section">
        <h3>🧠 多模态AI分析结果</h3>
        
        <div class="result-tabs">
          <button 
            :class="['tab-btn', { active: activeTab === 'image' }]"
            @click="activeTab = 'image'"
          >
            📷 影像分析
          </button>
          <button 
            :class="['tab-btn', { active: activeTab === 'text' }]"
            @click="activeTab = 'text'"
          >
            📄 文本分析
          </button>
          <button 
            :class="['tab-btn', { active: activeTab === 'combined' }]"
            @click="activeTab = 'combined'"
          >
            🔗 联合结论
          </button>
        </div>
        
        <div class="tab-content">
          <div v-show="activeTab === 'image'" v-html="result.imageAnalysis"></div>
          <div v-show="activeTab === 'text'" v-html="result.textAnalysis"></div>
          <div v-show="activeTab === 'combined'" v-html="result.combined"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'

const loading = ref(false)
const activeTab = ref('image')
const fileInput = ref(null)
const result = ref(null)

const form = reactive({
  imageList: [],
  reportText: '',
  examType: ''
})

const triggerUpload = () => {
  fileInput.value.click()
}

const handleFileChange = (e) => {
  const files = Array.from(e.target.files)
  form.imageList = [...form.imageList, ...files]
}

const removeImage = (idx) => {
  form.imageList.splice(idx, 1)
}

const analyzeMultimodal = async () => {
  if (!form.reportText && form.imageList.length === 0) {
    alert('请上传影像或输入报告文本')
    return
  }
  
  loading.value = true
  
  setTimeout(() => {
    result.value = {
      imageAnalysis: `
        <div class="result-item">
          <h4>📷 影像特征分析</h4>
          <ul>
            <li>检测到多处异常信号影</li>
            <li>最大病灶约1.2cm，位于右肺上叶</li>
            <li>边界清晰，密度均匀</li>
            <li>未见明显胸腔积液</li>
          </ul>
        </div>
      `,
      textAnalysis: `
        <div class="result-item">
          <h4>📄 报告文本解读</h4>
          <ul>
            <li>双肺多发结节</li>
            <li>最大结节位于右肺上叶</li>
            <li>建议定期复查</li>
          </ul>
        </div>
      `,
      combined: `
        <div class="result-item">
          <h4>🔗 联合分析结论</h4>
          <p>基于影像和文本的联合分析，建议：</p>
          <ul>
            <li><strong>综合评估：</strong>影像表现与报告描述一致</li>
            <li><strong>复查建议：</strong>3个月后复查CT对比</li>
            <li><strong>注意事项：</strong>如有咳嗽、胸痛等症状请及时就医</li>
          </ul>
        </div>
        <div class="result-note">
          ⚠️ 本分析仅供参考，不作为医疗诊断依据
        </div>
      `
    }
    loading.value = false
    alert('多模态分析完成')
  }, 2000)
}

const resetForm = () => {
  form.imageList = []
  form.reportText = ''
  form.examType = ''
  result.value = null
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
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px 60px;
}

.form-section {
  background: white;
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.form-col {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 24px;
  flex: 1;
}

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
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: #0071e3;
  background: #f9f9f9;
}

.upload-placeholder {
  color: #86868b;
}

.upload-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.upload-hint {
  font-size: 13px;
  color: #a1a1a6;
}

.upload-preview {
  width: 100%;
}

.preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f5f7;
  border-radius: 8px;
  margin-bottom: 8px;
}

.preview-name {
  font-size: 14px;
  color: #1d1d1f;
}

.preview-remove {
  font-size: 20px;
  color: #86868b;
  cursor: pointer;
}

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
  background: #34c759;
  color: white;
  border: none;
  border-radius: 980px;
  font-size: 17px;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover:not(:disabled) {
  background: #30b350;
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

.result-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 1px solid #e5e5e5;
  padding-bottom: 16px;
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

.tab-btn.active {
  background: #0071e3;
  color: white;
}

.tab-content {
  line-height: 1.8;
  color: #1d1d1f;
}

.tab-content :deep(.result-item) {
  margin-bottom: 20px;
}

.tab-content :deep(h4) {
  font-size: 17px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 12px;
}

.tab-content :deep(ul) {
  padding-left: 20px;
}

.tab-content :deep(li) {
  margin-bottom: 8px;
  color: #86868b;
}

.result-note {
  background: #fff3cd;
  border-radius: 12px;
  padding: 16px 20px;
  color: #856404;
  font-size: 14px;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .page-header h1 {
    font-size: 28px;
  }
  
  .form-section,
  .result-section {
    padding: 24px;
  }
}
</style>