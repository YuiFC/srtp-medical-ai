<template>
  <div id="app">
    <!-- 导航栏 -->
    <header class="main-header">
      <div class="header-content">
        <div class="logo">
          <span class="logo-icon">🏥</span>
          <span class="logo-text">SRTP 医疗AI</span>
        </div>
        <nav class="main-nav">
          <a href="/" :class="{ active: $route.path === '/' }">首页</a>
          <a href="/upload" :class="{ active: $route.path === '/upload' }">文本解读</a>
          <a href="/multimodal" :class="{ active: $route.path === '/multimodal' }">多模态</a>
          <a href="/compare" :class="{ active: $route.path === '/compare' }">对比</a>
          <a href="/questionnaire" :class="{ active: $route.path === '/questionnaire' }">问卷</a>
        </nav>
      </div>
    </header>

    <!-- 主内容 -->
    <main class="main-content">
      <router-view />
    </main>

    <!-- 页脚 -->
    <footer class="main-footer">
      <div class="footer-content">
        <p>SRTP - 多模态AI解读放射学报告对患者健康信念的影响研究</p>
        <p class="copyright">基于健康信念模型(HBM)</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
#app {
  width: 100%;
  max-width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.header-content {
  max-width: 980px;
  margin: 0 auto;
  padding: 0 20px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
}

.logo-icon {
  font-size: 22px;
}

.main-nav {
  display: flex;
  gap: 32px;
}

.main-nav a {
  color: #1d1d1f;
  font-size: 13px;
  text-decoration: none;
  padding: 8px 0;
  position: relative;
  opacity: 0.8;
  transition: opacity 0.3s;
}

.main-nav a:hover,
.main-nav a.active {
  opacity: 1;
  text-decoration: none;
}

.main-nav a.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: #0071e3;
  border-radius: 2px;
}

.main-content {
  flex: 1;
  width: 100%;
}

.main-footer {
  background: #f5f5f7;
  border-top: 1px solid #e5e5e5;
  padding: 40px 20px;
  text-align: center;
}

.footer-content {
  max-width: 980px;
  margin: 0 auto;
}

.footer-content p {
  color: #86868b;
  font-size: 13px;
}

.copyright {
  margin-top: 8px;
}

@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
  }
  
  .main-nav {
    gap: 16px;
  }
  
  .main-nav a {
    font-size: 12px;
  }
}
</style>