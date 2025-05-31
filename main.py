import uvicorn
import sys

if __name__ == "__main__":
    reload = True
    worker = 1
    if sys.argv[1] == "rel":
        reload = False
        worker = 24
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=reload, workers=worker)
