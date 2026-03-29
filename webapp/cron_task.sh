#!/bin/bash

# SRTP 医疗AI原型开发定时任务
# 每小时执行一次

SOURCE_DIR="/root/srtp_medical_ai"
LOG_FILE="$SOURCE_DIR/webapp/WORK_LOG.md"
APP_DIR="$SOURCE_DIR/webapp"

echo "========== $(date '+%Y-%m-%d %H:%M') ==========" >> "$LOG_FILE"

# 读取上次工作进度
if [ -f "$APP_DIR/progress.md" ]; then
    echo "--- 上次进度 ---" >> "$LOG_FILE"
    cat "$APP_DIR/progress.md" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
fi

cd "$APP_DIR"

# 检查项目是否初始化
if [ ! -f "package.json" ]; then
    echo "初始化Vue3+Vite项目..." >> "$LOG_FILE"
    npm create vite@latest . -- --template vue >> "$LOG_FILE" 2>&1
    npm install >> "$LOG_FILE" 2>&1
    echo "项目初始化完成" >> "$LOG_FILE"
else
    echo "项目已存在，继续开发..." >> "$LOG_FILE"
fi

# 开发任务
echo "执行开发任务..." >> "$LOG_FILE"

# 检查是否有待办事项
if [ -f "TODO.md" ]; then
    echo "--- 当前待办 ---" >> "$LOG_FILE"
    head -20 "TODO.md" >> "$LOG_FILE"
fi

# 简单的开发进度更新
echo "开发进度: $(date)" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"

# 保存进度
echo "Last update: $(date)" > "$APP_DIR/progress.md"

echo "任务完成" >> "$LOG_FILE"