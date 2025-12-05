# 使用官方 Python 镜像作为基础
FROM python:3.9-slim 
 
# 设置工作目录 
WORKDIR /app
 
# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* 
 
# 复制项目文件 
COPY slide.py .
 
# 安装 Python 依赖 
RUN pip install --no-cache-dir \
    bottle \
    opencv-python \
    numpy 
 
# 暴露端口
EXPOSE 3001
 
# 启动命令 
CMD ["python", "slide.py"] 
