# SRTP 医疗AI原型 - 工作日志

## 2026-04-01 10:15 多模态AI对接完成

### 完成内容

#### 后端 API 服务搭建
- `webapp/api/main.py`：FastAPI 应用
  - `/api/analyze` 接口：单次分析（多模态 or 纯文本）
  - `/api/compare` 接口：对比分析（同时返回两种模式结果）
  - `/health` 健康检查接口
  - CORS 配置允许 localhost:5173
- `webapp/api/analyzer.py`：GLM-4.6V 调用模块
  - 通过独立子进程 + curl -v 调用 GLM API
  - 解决 Python httpx/urllib 在 uvicorn 线程池中超时问题
  - 支持多模态（图片+报告）和纯文本两种模式
- `webapp/api/glm_caller.py`：独立调用脚本
- `webapp/api/models.py`：Pydantic 数据模型
  - AnalyzeRequest、AnalysisResult、ChexpertLabels（14类CheXpert标签）

#### 前端 Vue 组件重构（对接真实 API）
- `MultimodalView.vue`：上传影像+报告 → 调用 `/api/analyze` → 显示结构化解读结果
- `TextReportView.vue`：输入报告文本 → 调用 `/api/analyze` → 显示结构化解读结果
- `CompareView.vue`：上传影像+报告 → 调用 `/api/compare` → 显示多模态 vs 纯文本对比

#### 配置
- `vite.config.js`：添加 `/api` → `http://localhost:8000` 代理
- `.env` 放在 `code/.env`（供 ipynb 使用）

#### 服务状态
- Webapp (Vite): `http://localhost:5173` ✅
- API 服务: `http://localhost:8000` ✅
- GLM API Key: 已配置 ✅
- .env 路径修复: `code/.env` ✅

#### 验证结果
实测调用 `/api/analyze`（纯文本模式）：
- 输入: "Chest X ray shows no abnormality."
- 输出: 结构化 JSON ✅
  ```json
  {
    "findings": "胸部X光片显示双肺、心脏、纵隔、膈肌及胸膜腔未见明显异常。",
    "impression": "胸部X光片未见明显异常。",
    "recommendations": "建议定期体检，如有不适及时就诊。",
    "chexpert_labels": { "Atelectasis": "negative", ... }
  }
  ```
- 注意：首次冷启动约需 60-90 秒，后续会更快

## 下次工作重点
- 多模态上传 + 图片base64传输测试
- 预测试问卷数据收集

---

## 历史记录

### 2026-03-29 多模态AI原型开发
- HomeView: 修复黑边问题，Apple风格设计
- MultimodalView: 实现多模态上传UI
- TextReportView: 实现结果保存和复制功能
- CompareView: 对比分析页面

### 2026-03-27 项目初始化
- Vue 3 + Vite + Element Plus 初始化
- 5个页面路由配置
- Webapp 运行在 5173 端口
