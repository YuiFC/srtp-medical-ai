<template>
  <div class="questionnaire-page">
    <div class="page-header">
      <h1>健康信念问卷</h1>
      <p>基于健康信念模型(HBM) - 您的反馈对我们非常重要</p>
    </div>
    
    <div class="questionnaire-container">
      <iframe 
        id='idy_frame' 
        height="700px" 
        width="100%" 
        src="https://wj.qq.com/s2/25961724/cc23/" 
        frameborder="0" 
        style='min-height:700px' 
        allowfullscreen 
        sandbox="allow-same-origin allow-scripts allow-modals allow-downloads allow-forms allow-popups"
      ></iframe>
    </div>
    
    <div class="questionnaire-info">
      <h3>关于问卷</h3>
      <p>本问卷基于健康信念模型(HBM)的5个核心维度设计，旨在评估您对AI解读医疗报告的看法。</p>
      <ul>
        <li><strong>感知易感性</strong> - 您认为理解医学报告的困难程度</li>
        <li><strong>感知严重性</strong> - 误解报告可能带来的后果</li>
        <li><strong>感知益处</strong> - AI解读能带来的帮助</li>
        <li><strong>行动线索</strong> - 促使您使用AI解读的因素</li>
        <li><strong>自我效能</strong> - 您使用AI工具的信心程度</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.questionnaire-page {
  width: 100%;
  max-width: 100%;
  padding: 0;
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

.questionnaire-container {
  max-width: 100%;
  margin: 0 auto;
  background: white;
  min-height: 700px;
}

.questionnaire-container iframe {
  width: 100%;
  display: block;
}

.questionnaire-info {
  max-width: 700px;
  margin: 60px auto;
  padding: 40px;
  background: #f5f5f7;
  border-radius: 20px;
}

.questionnaire-info h3 {
  font-size: 22px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 16px;
}

.questionnaire-info p {
  font-size: 15px;
  color: #86868b;
  line-height: 1.6;
  margin-bottom: 20px;
}

.questionnaire-info ul {
  list-style: none;
  padding: 0;
}

.questionnaire-info li {
  font-size: 15px;
  color: #1d1d1f;
  padding: 8px 0;
  border-bottom: 1px solid #e5e5e5;
}

.questionnaire-info li:last-child {
  border-bottom: none;
}

.questionnaire-info li strong {
  color: #0071e3;
}

@media (max-width: 768px) {
  .page-header h1 {
    font-size: 28px;
  }
  
  .page-header p {
    font-size: 16px;
  }
  
  .questionnaire-info {
    margin: 40px 16px;
    padding: 24px;
  }
}
</style>