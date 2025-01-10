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


load_dotenv()

# Load environment variables

logging.info("Loading environment variables...")

secret_key = os.getenv("SECRET_KEY", "")
if not secret_key:
    logging.error("SECRET_KEY is not set in .env file")
    sys.exit(1)


algorithms = os.getenv("ALGORITHM", "")
access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1200))

turnstile_site_key = os.getenv("TURNSTILE_SITE_KEY", "")
turnstile_secret_key = os.getenv("TURNSTILE_SECRET_KEY", "")

code_email = os.getenv("CODE_EMAIL", "")

logging.info("secret_key: %s", secret_key)
logging.info("algorithms: %s", algorithms)
logging.info("access_token_expire_minutes: %s", access_token_expire_minutes)
logging.info("turnstile_site_key: %s", turnstile_site_key)
logging.info("turnstile_secret_key: %s", turnstile_secret_key)
logging.info("code_email: %s", code_email)
