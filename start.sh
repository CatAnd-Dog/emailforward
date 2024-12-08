#!/bin/sh

# 如果目标目录为空，则复制初始内容
if [ -z "$(ls -A /app/templates/else)" ]; then
   echo "Initializing /app/templates/else..."
   cp -r /app/templates/else_default/* /app/templates/else/
fi

# 启动主服务
exec gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 1 --threads 4
