import requests
import traceback

def test_analyze():
    # 1. Upload
    url_upload = "http://localhost:8000/upload"
    doc_id = ""
    print("Uploading test.pdf...")
    try:
        files = {'file': open('test.pdf', 'rb')}
        response = requests.post(url_upload, files=files)
        if response.status_code == 200:
            data = response.json()
            doc_id = data.get("doc_id")
            print(f"Upload Success. Doc ID: {doc_id}")
        else:
            print(f"Upload Failed: {response.text}")
            return
    except Exception as e:
        print(f"Upload Exception: {e}")
        return

    # 2. Analyze
    if not doc_id:
        print("No doc_id, skipping analysis.")
        return

    url_analyze = f"http://localhost:8000/analyze/{doc_id}"
    print(f"Requesting analysis for {doc_id}...")
    try:
        response = requests.post(url_analyze)
        print(f"Analyze Status: {response.status_code}")
        if response.status_code == 200:
            print("Analyze Success!")
            print(response.json())
        else:
            print(f"Analyze Failed Body: {response.text}")
    except Exception as e:
        print(f"Analyze Exception: {e}")

if __name__ == "__main__":
    try:
        test_analyze()
    except:
        traceback.print_exc()
