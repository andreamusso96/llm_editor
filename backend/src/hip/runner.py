import yaml
from google import genai
import os
import asyncio
import jinja2
import json

GOOGLE_API_KEY="AIzaSyDPsfVwLWeWxSm10W0IzWKz7ytz8qjmavU"
base_path = '/Users/andrea/Desktop/PhD/llm_editor/backend/src/hip/'

def load_prompts():
    with open(os.path.join(base_path, 'prompts.yml'), 'r') as file:
        prompts = yaml.safe_load(file)
    return prompts

def load_papers():
    with open(os.path.join(base_path, 'papers.yml'), 'r') as file:
        papers = yaml.safe_load(file)
    return papers


async def run_prompt(prompt_id: int, paper_id: int):
    prompts = load_prompts()
    prompts = {prompt['prompt_id']: prompt['prompt'] for prompt in prompts}
    papers = load_papers()
    papers = {paper['paper_id']: paper['introduction'] for paper in papers}

    prompt = prompts[prompt_id]
    paper = papers[paper_id]

    prompt = jinja2.Template(prompt).render(introduction=paper)

    client = genai.Client(api_key=GOOGLE_API_KEY)
    response = await client.aio.models.generate_content(
        model="gemini-2.5-pro-preview-05-06",
        contents=prompt,
    )

    print(response.text)


async def run_prompt_2(prompt_id: int):
    prompts = load_prompts()
    prompts = {prompt['prompt_id']: prompt['prompt'] for prompt in prompts}
    prompt = prompts[prompt_id]

    papers = load_papers()

    prompts = []
    for paper in papers:
        prompt_paper = jinja2.Template(prompt).render(introduction=paper['introduction'])
        prompts.append(prompt_paper)
        print(prompt_paper)


    print('-'*100)

    client = genai.Client(api_key=GOOGLE_API_KEY)
    lmm_calls = [client.aio.models.generate_content(model="gemini-2.5-pro-preview-05-06", contents=prompt) for prompt in prompts]
    results = await asyncio.gather(*lmm_calls, return_exceptions=True)
    
    save_results = []
    for i, response in enumerate(results):
        clean_response = response.text.replace("```json", "").replace("```", "")
        clean_response = json.loads(clean_response)
        print(clean_response)
        save_results.append({
            'paper_id': 1 + i,
            'response': clean_response
        })
    
    print('-'*100)
    with open(os.path.join(base_path, 'results.json'), 'w') as file:
        json.dump(save_results, file)

def load_results():
    with open(os.path.join(base_path, 'results.json'), 'r') as file:
        results = json.load(file)
    return results

async def run_prompt_3():
    prompts = load_prompts()
    prompts = {prompt['prompt_id']: prompt['prompt'] for prompt in prompts}
    prompt = prompts[2]

    results = load_results()

    prompt = jinja2.Template(prompt).render(json_analyses_of_10_introductions=results)

    print('-'*100)

    print(prompt)

    client = genai.Client(api_key=GOOGLE_API_KEY)
    response = await client.aio.models.generate_content(
        model="gemini-2.5-pro-preview-05-06",
        contents=prompt,
    )

    print('-'*100)

    print(response.text)


if __name__ == "__main__":
    asyncio.run(run_prompt_2(1))
    asyncio.run(run_prompt_3())