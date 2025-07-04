import uvicorn, multiprocessing
from dotenv import load_dotenv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--mode", type=str, required=True)
parser.add_argument("--workers", type=int, default=multiprocessing.cpu_count())
args = parser.parse_args()

load_dotenv()

def serve():
    mode = args.mode
    if mode == "development":
        uvicorn.run("app.main:app", reload=True, host="0.0.0.0", port=8000)
    elif mode == "production":
        workers = args.workers
        print(f"Running with {workers} workers")
        uvicorn.run("app.main:app", workers=workers, host="0.0.0.0", port=8000)
    else:
        raise ValueError(f"Invalid mode: {mode}")

if __name__ == "__main__":
    serve()
