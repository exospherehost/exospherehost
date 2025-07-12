import uvicorn
import multiprocessing
from dotenv import load_dotenv
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--mode", type=str, required=True)
parser.add_argument("--workers", type=int, default=multiprocessing.cpu_count())
parser.add_argument("--max-tokens-per-session", type=int, default=3)
args = parser.parse_args()

load_dotenv()
os.environ["MAX_TOKENS_PER_SESSION"] = str(args.max_tokens_per_session)

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
