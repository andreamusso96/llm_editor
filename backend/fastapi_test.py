from fastapi.testclient import TestClient
from main import app
import time

client = TestClient(app)

def load_text():
    text_path = '/Users/andrea/Desktop/PhD/llm_editor/frontend/public/text.txt'
    with open(text_path, 'r') as file:
        text = file.read()
    return text

def test_list_prompts():
    response = client.get("/api/v1/prompts")
    print(response.json())
    assert response.status_code == 200

def test_create_correction():
    text = load_text()
    list_prompts = client.get("/api/v1/prompts").json()["prompts"]
    prompt_id_refs = [prompt["prompt_id_ref"] for prompt in list_prompts[:5]]
    response = client.post("/api/v1/corrections", json={"text_content": text, "prompt_id_refs": prompt_id_refs})
    print(response.json())
    assert response.status_code == 200

def test_all():
    text = load_text()
    list_prompts = client.get("/api/v1/prompts").json()["prompts"]
    prompt_id_refs = [prompt["prompt_id_ref"] for prompt in list_prompts[:6]]
    response = client.post("/api/v1/corrections", json={"text_content": text, "prompt_id_refs": prompt_id_refs})
    correction_id = response.json()["correction_id"]

    while True:
        response = client.get(f"/api/v1/corrections/{correction_id}/status")
        print(response.json())
        if response.json()["status"] == "completed":
            break
        time.sleep(1)

    response = client.get(f"/api/v1/corrections/{correction_id}/results")
    print(response.json())
    assert response.status_code == 200



if __name__ == "__main__":
    test_create_correction()