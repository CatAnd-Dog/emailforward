from dotenv import load_dotenv
import os
import sys
import logging


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],  # 日志输出到控制台
)

# 首先加载.env文件中的环境变量（如果文件存在）
load_dotenv()

logging.info("Loading configuration...")

# 加载核心配置，提供合理的默认值以支持Docker环境
secret_key = os.getenv("SECRET_KEY", "yoursecretkeyhere")
algorithms = os.getenv("ALGORITHM", "HS256")
access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1200))


# Cloudflare Turnstile 配置（可选）
turnstile_site_key = os.getenv("TURNSTILE_SITE_KEY", "")
turnstile_secret_key = os.getenv("TURNSTILE_SECRET_KEY", "")

# 其他可选配置
code_email = os.getenv("CODE_EMAIL", "")

# 记录配置信息（敏感信息只显示是否已设置）
logging.info("Configuration loaded:")
logging.info("SECRET_KEY: %s", "[SET]" if secret_key else "[NOT SET]")
logging.info("ALGORITHM: %s", algorithms)
logging.info("ACCESS_TOKEN_EXPIRE_MINUTES: %s", access_token_expire_minutes)
logging.info("TURNSTILE_SITE_KEY: %s", "[SET]" if turnstile_site_key else "[NOT SET]")
logging.info("TURNSTILE_SECRET_KEY: %s", "[SET]" if turnstile_secret_key else "[NOT SET]")
logging.info("CODE_EMAIL: %s", code_email if code_email else "[NOT SET]")

# 警告不建议使用默认值的情况
if secret_key == "yoursecretkeyhere":
    logging.warning("Using default SECRET_KEY. This is not secure for production environments.")

