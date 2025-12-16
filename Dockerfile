FROM dpanel/dpanel:lite

# 设置时区
RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

# 使用 apk 安装依赖（包含 coreutils 解决 nohup 问题）
RUN apk add --no-cache \
    python3 \
    py3-pip \
    nodejs npm \
    bash \
    curl \
    coreutils  # 确保 nohup 可用

RUN python3 -m venv /app/myenv && \
    /app/myenv/bin/pip install --upgrade pip && \
    /app/myenv/bin/pip install --no-cache-dir --upgrade pypinyin tqdm requests pysocks pyyaml pytz httpx bs4 aiohttp telethon docker qrcode webdavclient3 dotenv schedule
    
# 列出目录内容（调试用）
RUN ls -al

# 创建启动脚本：先执行自定义命令，再执行原命令（原命令作为主进程）
# 移除了命令中的注释，避免构建错误
RUN echo '#!/bin/sh' > /entrypoint.sh && \
    echo 'set -x' >> /entrypoint.sh && \
    echo 'if [ -n "$STARTUP_COMMAND" ]; then' >> /entrypoint.sh && \
    echo '  echo "执行前置自定义命令: $STARTUP_COMMAND"' >> /entrypoint.sh && \
    echo '  eval "$STARTUP_COMMAND"' >> /entrypoint.sh && \
    echo 'fi' >> /entrypoint.sh && \
    echo '/app/server/dpanel server:start -f /app/server/config.yaml' >> /entrypoint.sh && \
    chmod +x /entrypoint.sh

# 设置入口点为自定义脚本
ENTRYPOINT ["/entrypoint.sh"]
