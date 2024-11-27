# 使用 Python 3.9 Alpine 版本作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 将依赖文件复制到容器中
COPY requirements.txt .

# 安装依赖，添加 `--no-cache` 避免缓存
RUN pip install --no-cache-dir -r requirements.txt

# 安装 gunicorn 和 uvicorn
RUN pip install --no-cache-dir gunicorn uvicorn

# 将当前目录下的所有文件复制到容器的工作目录
COPY . /app


# 设置环境变量，确保 Python 输出不被缓冲
ENV PYTHONUNBUFFERED=1

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# 暴露端口
EXPOSE 8000

# 启动命令，使用 gunicorn 运行 FastAPI 应用，配置 4 个工作线程
CMD ["gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "4"]

