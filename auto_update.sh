#!/bin/bash

# 设置日志文件
LOG_FILE="/home/lighthouse/var/www/Bjsys/auto_update.log"
PROJECT_DIR="/home/lighthouse/var/www/Bjsys"

echo "========== 开始自动更新: $(date) ==========" >> "$LOG_FILE"

# 1. 进入项目目录
cd "$PROJECT_DIR" || { echo "错误: 无法进入目录 $PROJECT_DIR" >> "$LOG_FILE"; exit 1; }

# 2. 强制拉取最新代码
echo "正在拉取代码..." >> "$LOG_FILE"
git fetch origin main >> "$LOG_FILE" 2>&1
git reset --hard origin/main >> "$LOG_FILE" 2>&1

# 3. 重新构建前端
echo "正在构建前端..." >> "$LOG_FILE"
cd front/my-vue-app || { echo "错误: 无法进入前端目录" >> "$LOG_FILE"; exit 1; }
# npm install >> "$LOG_FILE" 2>&1 # 如果依赖没变可以注释掉以节省时间
npm run build >> "$LOG_FILE" 2>&1

# 4. 重启后端服务
# 注意：请根据您的实际运行方式取消注释下面对应的行
echo "正在重启服务..." >> "$LOG_FILE"

# 如果使用 uwsgi
# sudo systemctl restart uwsgi >> "$LOG_FILE" 2>&1

# 如果使用 gunicorn
# sudo systemctl restart gunicorn >> "$LOG_FILE" 2>&1

# 如果使用 Nginx
# sudo systemctl reload nginx >> "$LOG_FILE" 2>&1

echo "========== 更新完成: $(date) ==========" >> "$LOG_FILE"
