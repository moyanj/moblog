import uvicorn
from app.config import config

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=config.host,
        port=config.port,
        reload=True,
    )
