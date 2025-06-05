import uvicorn
from app.config import server_config

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=server_config.host,
        port=server_config.port,
        reload=True,
    )
