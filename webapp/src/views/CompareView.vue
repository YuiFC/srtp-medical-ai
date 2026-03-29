<template>
  <div class="page-container">
    <div class="page-header">
      <h1>⚖️ 对比分析</h1>
      <p>对比多模态AI与纯文本LLM的解读效果差异</p>
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
                <div v-if="form.imageList.length === 0" class="upload-placeholder">
                  <span class="upload-icon">📁</span>
                  <p>点击上传医学影像</p>
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
        
        <div class="form-actions">
          <button class="btn-warning" @click="compareAnalysis" :disabled="loading">
            {{ loading ? '分析中...' : '开始对比分析' }}
          </button>
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
            <div class="compare-content" v-html="result.textResult"></div>
          </div>
          
          <div class="compare-box multimodal-mode">
            <div class="compare-header">
              <span class="compare-icon">🖼️</span>
              <h4>多模态AI解读</h4>
              <span class="compare-tag">影像+文本</span>
            </div>
            <div class="compare-content" v-html="result.multimodalResult"></div>
          </div>
        </div>
        
        <div class="comparison-summary">
          <h4>📈 对比总结</h4>
          <table class="comparison-table">
            <thead>
              <tr>
                <th>维度</th>
                <th>纯文本</th>
                <th>多模态</th>
                <th>优势方</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>信息完整度</td>
                <td>文本描述</td>
                <td>影像+文本</td>
                <td><span class="advantage-tag multimodal">多模态</span></td>
              </tr>
              <tr>
                <td>诊断准确性</td>
                <td>一般</td>
                <td>更高</td>
                <td><span class="advantage-tag multimodal">多模态</span></td>
              </tr>
              <tr>
                <td>可解释性</td>
                <td>有限</td>
                <td>更强</td>
                <td><span class="advantage-tag multimodal">多模态</span></td>
              </tr>
              <tr>
                <td>响应速度</td>
                <td>更快</td>
                <td>较慢</td>
                <td><span class="advantage-tag text">纯文本</span></td>
              </tr>
            </tbody>
          </table>
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

const form = reactive({
  imageList: [],
  reportText: ''
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

const compareAnalysis = async () => {
  if (!form.reportText) {
    alert('请输入报告文本')
    return
  }
  
  loading.value = true
  
  setTimeout(() => {
    result.value = {
      textResult: `
        <p>根据报告文本分析，双肺可见多个结节，最大者位于右肺上叶，直径约1.2cm。</p>
        <p><strong>建议：</strong>定期复查，监测结节变化。</p>
      `,
      multimodalResult: `
        <p>结合影像和文本分析：</p>
        <ul>
          <li>影像显示结节边界清晰，密度均匀</li>
          <li>与报告描述一致</li>
          <li>可识别影像中未提及的细微变化</li>
        </ul>
        <p><strong>建议：</strong>3个月复查，结合临床症状判断。</p>
      `
    }
    loading.value = false
    alert('对比分析完成')
  }, 2000)
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
  max-width: 1100px;
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
  border-color: #ff9500;
  background: #fffaf5;
}

.upload-placeholder {
  color: #86868b;
}

.upload-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
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
  border-color: #ff9500;
}

.form-actions {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.btn-warning {
  padding: 14px 36px;
  background: #ff9500;
  color: white;
  border: none;
  border-radius: 980px;
  font-size: 17px;
  font-weight: 400;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-warning:hover:not(:disabled) {
  background: #ff8f00;
}

.btn-warning:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.compare-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 40px;
}

.compare-box {
  border-radius: 16px;
  padding: 24px;
}

.text-mode {
  background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
}

.multimodal-mode {
  background: linear-gradient(135deg, #e8f5e9 0%, #e0f2f1 100%);
}

.compare-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.compare-icon {
  font-size: 24px;
}

.compare-header h4 {
  font-size: 17px;
  font-weight: 600;
  color: #1d1d1f;
  flex: 1;
}

.compare-tag {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 500;
}

.text-mode .compare-tag {
  background: #0071e3;
  color: white;
}

.multimodal-mode .compare-tag {
  background: #34c759;
  color: white;
}

.compare-content {
  line-height: 1.8;
  color: #1d1d1f;
  font-size: 15px;
}

.compare-content :deep(ul) {
  padding-left: 20px;
  margin: 12px 0;
}

.compare-content :deep(li) {
  margin-bottom: 6px;
}

.comparison-summary h4 {
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 20px;
}

.comparison-table {
  width: 100%;
  border-collapse: collapse;
  background: #fafafa;
  border-radius: 12px;
  overflow: hidden;
}

.comparison-table th,
.comparison-table td {
  padding: 16px 20px;
  text-align: left;
  border-bottom: 1px solid #e5e5e5;
}

.comparison-table th {
  background: #f5f5f7;
  font-weight: 600;
  font-size: 14px;
  color: #86868b;
}

.comparison-table td {
  font-size: 15px;
  color: #1d1d1f;
}

.comparison-table tr:last-child td {
  border-bottom: none;
}

.advantage-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.advantage-tag.multimodal {
  background: #d4edda;
  color: #155724;
}

.advantage-tag.text {
  background: #cce5ff;
  color: #004085;
}

@media (max-width: 768px) {
  .form-row,
  .compare-grid {
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