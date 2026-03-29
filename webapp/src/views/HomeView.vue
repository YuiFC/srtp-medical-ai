<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">多模态AI解读放射学报告</h1>
        <p class="hero-subtitle">基于健康信念模型(HBM)的AI医疗报告解读原型系统</p>
        <p class="hero-desc">探究多模态AI与纯文本LLM解读效果的差异</p>
        <div class="hero-cta">
          <a href="/upload" class="btn-primary">开始体验</a>
          <a href="#about" class="btn-secondary">了解更多</a>
        </div>
      </div>
      <div class="hero-image">
        <img src="https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&q=80" alt="Medical AI" />
      </div>
    </section>

    <!-- Features Section -->
    <section class="features-section" id="about">
      <div class="section-header">
        <h2>核心功能</h2>
        <p>四大模块，全方位体验AI医疗报告解读</p>
      </div>
      
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">📄</div>
          <h3>文本解读</h3>
          <p>输入放射学报告文本，LLM智能解读分析</p>
          <a href="/upload" class="feature-link">体验 →</a>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">🖼️</div>
          <h3>多模态解读</h3>
          <p>上传医学影像结合报告文本，多模态AI联合分析</p>
          <a href="/multimodal" class="feature-link">体验 →</a>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">⚖️</div>
          <h3>对比分析</h3>
          <p>同时展示多模态与纯文本解读效果对比</p>
          <a href="/compare" class="feature-link">体验 →</a>
        </div>
        
        <div class="feature-card">
          <div class="feature-icon">📋</div>
          <h3>健康问卷</h3>
          <p>基于HBM模型的健康信念问卷调查</p>
          <a href="/questionnaire" class="feature-link">参与 →</a>
        </div>
      </div>
    </section>

    <!-- About Section -->
    <section class="about-section">
      <div class="about-content">
        <h2>关于项目</h2>
        <div class="about-grid">
          <div class="about-item">
            <h4>研究背景</h4>
            <p>SRTP大学生创新创业训练计划项目，探究多模态AI（结合影像+文本）解读放射学报告对患者健康信念的影响。</p>
          </div>
          <div class="about-item">
            <h4>理论基础</h4>
            <p>基于健康信念模型(HBM)进行分析，研究AI解读对患者感知易感性、感知严重性、感知益处等因素的影响。</p>
          </div>
          <div class="about-item">
            <h4>技术创新</h4>
            <p>对比多模态AI与纯文本LLM的解读效果差异，探索技术系统与社会子系统的双向作用机制。</p>
          </div>
          <div class="about-item">
            <h4>应用价值</h4>
            <p>为AI医疗应用提供理论支撑，优化患者健康信念和就医行为决策。</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
</script>

<style scoped>
.home-page {
  width: 100%;
  max-width: 100%;
}

/* Hero Section */
.hero-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
  padding: 80px 20px;
  max-width: 1200px;
  margin: 0 auto;
  min-height: 80vh;
}

.hero-content {
  padding-right: 40px;
}

.hero-title {
  font-size: 56px;
  font-weight: 700;
  color: #1d1d1f;
  margin-bottom: 16px;
  letter-spacing: -0.02em;
}

.hero-subtitle {
  font-size: 24px;
  color: #86868b;
  margin-bottom: 12px;
  font-weight: 500;
}

.hero-desc {
  font-size: 19px;
  color: #86868b;
  margin-bottom: 32px;
}

.hero-cta {
  display: flex;
  gap: 16px;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  padding: 14px 28px;
  background: #0071e3;
  color: white;
  border-radius: 980px;
  font-size: 17px;
  text-decoration: none;
  transition: all 0.3s;
}

.btn-primary:hover {
  background: #0077ed;
  text-decoration: none;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  padding: 14px 28px;
  color: #0071e3;
  font-size: 17px;
  text-decoration: none;
}

.btn-secondary:hover {
  text-decoration: underline;
}

.hero-image {
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);
}

.hero-image img {
  width: 100%;
  height: auto;
  display: block;
}

/* Features Section */
.features-section {
  background: #f5f5f7;
  padding: 100px 20px;
}

.section-header {
  text-align: center;
  margin-bottom: 60px;
}

.section-header h2 {
  font-size: 40px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 12px;
}

.section-header p {
  font-size: 19px;
  color: #86868b;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-card {
  background: white;
  border-radius: 20px;
  padding: 40px 28px;
  text-align: center;
  transition: all 0.4s ease;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.feature-card h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 12px;
}

.feature-card p {
  font-size: 15px;
  color: #86868b;
  line-height: 1.5;
  margin-bottom: 20px;
}

.feature-link {
  font-size: 15px;
  color: #0071e3;
  font-weight: 500;
}

/* About Section */
.about-section {
  padding: 100px 20px;
  background: white;
}

.about-content {
  max-width: 980px;
  margin: 0 auto;
}

.about-content h2 {
  font-size: 40px;
  font-weight: 600;
  color: #1d1d1f;
  text-align: center;
  margin-bottom: 60px;
}

.about-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 48px;
}

.about-item h4 {
  font-size: 20px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 12px;
}

.about-item p {
  font-size: 15px;
  color: #86868b;
  line-height: 1.6;
}

/* Responsive */
@media (max-width: 968px) {
  .hero-section {
    grid-template-columns: 1fr;
    text-align: center;
    padding: 60px 20px;
    min-height: auto;
  }
  
  .hero-content {
    padding-right: 0;
  }
  
  .hero-title {
    font-size: 36px;
  }
  
  .hero-subtitle {
    font-size: 20px;
  }
  
  .hero-cta {
    justify-content: center;
  }
  
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .about-grid {
    grid-template-columns: 1fr;
    gap: 32px;
  }
}

@media (max-width: 600px) {
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header h2 {
    font-size: 28px;
  }
}
</style>