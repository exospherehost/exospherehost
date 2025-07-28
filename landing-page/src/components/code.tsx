import { CodeComparison } from "@/components/magicui/code-comparison";

const beforeCode = `
import requests

def load_files_from_s3(bucket, keys):
    print("Loading files from S3...")
    res = requests.post("https://api.example.com/s3/generate-urls", json={
        "bucket": bucket,
        "keys": keys
    })
    res.raise_for_status()
    return res.json()["urls"]

def send_inference_request(deployment_id, file_urls):
    print("Sending inference request to Gemma...")
    res = requests.post("https://api.example.com/gemma/infer", json={
        "deployment_id": deployment_id,
        "files": file_urls
    })
    res.raise_for_status()
    return res.json()["job_id"]

def poll_for_completion(job_id, interval=5, max_retries=20):
    print("Polling for job completion...")
    for attempt in range(max_retries):
        res = requests.get(f"https://api.example.com/gemma/status/{job_id}")
        res.raise_for_status()
        status = res.json()["status"]

        if status == "completed":
            return True
        elif status == "failed":
            raise Exception("Job failed")

        time.sleep(interval)
    
    raise TimeoutError("Polling timed out")

def fetch_inference_result(job_id):
    print("Fetching inference result...")
    res = requests.get(f"https://api.example.com/gemma/result/{job_id}")
    res.raise_for_status()
    return res.json()

def main(string bucket, string[] keys):
    file_urls = with_retries(load_files_from_s3, bucket, keys)  # [!code highlight]
    job_id = with_retries(send_inference_request, deployment_id, file_urls)  # [!code highlight]

    if with_retries(poll_for_completion, job_id):
        result = with_retries(fetch_inference_result, job_id)  # [!code highlight]
        ocr_result = with_retries(run_ocr_on_images, result["images"])  # [!code highlight]
        summary = summarize_output(ocr_result)  # [!code highlight]
        return summary

if __name__ == "__main__":
    main()`;

const afterCode = `
from exosphere import run_workflow

def main():
    result = run_workflow( # [!code focus]
        "gemma_gpu_pipeline.yaml", # [!code focus]
        input={ 
            "bucket": "user-bucket", # [!code focus]
            "files": ["doc1.pdf", "doc2.pdf"] # [!code focus]
        },
        sla_minutes=360  # [!code focus]
    )
    print("Final Summary:", result)

if __name__ == "__main__":
    main()
`;

export function CodeComparisonDemo() {
  return (
    <CodeComparison
      beforeCode={beforeCode}
      afterCode={afterCode}
      language="python"
      filename="workflow.py"
      lightTheme="github-light"
      darkTheme="kanagawa-wave"
      highlightColor="rgba(228, 88, 125, 0.16)"
    />
  );
}
