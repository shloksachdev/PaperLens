from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()
token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
print(f"Token: {token[:4]}...{token[-4:]}")

repo_id = "HuggingFaceH4/zephyr-7b-beta"

try:
    client = InferenceClient(model=repo_id, token=token)
    print("Sending request...")
    # Using text_generation for 0.23.5 compatibility check
    res = client.text_generation("Hello", max_new_tokens=10)
    print("Success:")
    print(res)
except Exception as e:
    print(f"Error: {e}")
