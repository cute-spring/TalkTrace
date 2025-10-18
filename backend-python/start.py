"""启动脚本"""
import uvicorn
from app.config import settings
from app.utils.logger import logger

def main():
    """启动FastAPI应用"""
    logger.info(
        "Starting Talk Trace API Server",
        version="2.0.0",
        environment=settings.environment,
        host=settings.host,
        port=settings.port
    )

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.environment == "development",
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    main()