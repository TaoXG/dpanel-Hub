FROM dpanel/dpanel:lite

# 设置时区
RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone

# 使用 apk 安装依赖
RUN apk add --no-cache \
    python3 \
    py3-pip \
    nodejs npm \
    bash \
    curl

# 创建虚拟环境并安装 Python 依赖
#RUN python3 -m venv /app/myenv && \
#    . /app/myenv/bin/activate && \
#    pip install --no-cache-dir pypinyin tqdm requests pysocks telethon pyyaml pytz httpx bs4 aiohttp && \
#    deactivate
#RUN python3 -m venv /app/myenv && \
#    /app/myenv/bin/pip install --upgrade pip && \
#    /app/myenv/bin/pip install --no-cache-dir pypinyin tqdm requests pysocks pyyaml pytz httpx bs4 aiohttp && \
#    /app/myenv/bin/pip install --no-cache-dir --upgrade telethon
RUN python3 -m venv /app/myenv && \
    /app/myenv/bin/pip install --upgrade pip && \
    /app/myenv/bin/pip install --no-cache-dir --upgrade pypinyin tqdm requests pysocks pyyaml pytz httpx bs4 aiohttp telethon docker
    
# 列出目录内容（调试用）
RUN ls -al

# 设置入口点
ENTRYPOINT [ "sh", "-c", "/app/server/dpanel server:start -f /app/server/config.yaml" ]
