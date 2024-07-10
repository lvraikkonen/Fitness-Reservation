from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# 加载 .env 文件中的配置
load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME")
    PROJECT_VERSION: str = os.getenv("PROJECT_VERSION")
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = os.getenv("SMTP_PORT")
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SMTP_TLS: bool = os.getenv("SMTP_TLS")
    FRONTEND_BASE_URL: str = os.getenv("FRONTEND_BASE_URL")
    CANCELLATION_DEADLINE_HOURS: int = os.getenv("CANCELLATION_DEADLINE_HOURS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class MongoSettings(BaseSettings):
    MONGO_HOST: str = os.getenv("MONGO_HOST")
    MONGO_PORT: int = os.getenv("MONGO_PORT")
    MONGO_USER: str = os.getenv("MONGO_USER")
    MONGO_PASSWORD: str = os.getenv("MONGO_PASSWORD")
    MONGO_DATABASE: str = os.getenv("MONGO_DATABASE")
    MONGO_AUTH_SOURCE: str = os.getenv("MONGO_AUTH_SOURCE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class DevelopmentSettings(Settings):
    # 开发环境使用本地数据库
    DATABASE_URL: str = os.getenv("DEVELOPMENT_DATABASE_URL")
    SECRET_KEY: str = os.getenv("DEVELOPMENT_SECRET_KEY")


class TestingSettings(Settings):
    # 测试环境使用本地SQLServer数据库
    DATABASE_URL: str = os.getenv("TESTING_DATABASE_URL")
    SECRET_KEY: str = os.getenv("TESTING_SECRET_KEY")


class ProductionSettings(Settings):
    # 生产环境从环境变量中获取数据库配置和秘钥

    DATABASE_URL: str = os.getenv("PROD_DATABASE_URL")
    SECRET_KEY: str = os.getenv("PROD_SECRET_KEY")


def get_settings() -> Settings:
    """
    根据环境变量 ENV 的值选择相应的配置类。
    - development: 使用 DevelopmentSettings
    - testing: 使用 TestingSettings
    - production: 使用 ProductionSettings
    """
    env = os.getenv("ENV", "development")
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# 创建 settings 实例,用于在整个应用程序中访问配置项
settings = get_settings()

# log db settings
mongo_settings = MongoSettings()
