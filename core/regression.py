import httpx
from core.db import (
    get_test_cases, add_test_result,
    get_test_results, get_version
)
from core.semantic import generate_embedding, load_embedding, cosine_distance, describe_distance
from models.schemas import Version

OLLAMA_URL = "http://localhost:11434/api/generate"


def run_prompt(prompt_content: str, input_text: str, model: str = "llama3.2") -> str:
    full_prompt = f"{prompt_content}\n\nInput: {input_text}"
    try:
        response = httpx.post(
            OLLAMA_URL,
            json={
                "model": model,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=60.0
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except httpx.ConnectError:
        raise RuntimeError("Ollama is not running. Start it with: ollama serve")
    except Exception as e:
        raise RuntimeError(f"Model error: {e}")


def run_regression(
    prompt_id: int,
    version: Version,
    model: str = "llama3.2"
) -> list[dict]:
    test_cases = get_test_cases(prompt_id)
    if not test_cases:
        return []

    results = []
    for tc in test_cases:
        output = run_prompt(version.content, tc.input, model)
        embedding = generate_embedding(output)
        add_test_result(version.id, tc.id, output, model)
        results.append({
            "test_case": tc,
            "output": output,
            "embedding": embedding
        })

    return results


def compare_regression(
    prompt_id: int,
    v1: Version,
    v2: Version,
    model: str = "llama3.2"
) -> list[dict]:
    test_cases = get_test_cases(prompt_id)
    if not test_cases:
        return []

    comparisons = []
    for tc in test_cases:
        v1_results = get_test_results(v1.id)
        v2_results = get_test_results(v2.id)

        v1_output = next((r.output for r in v1_results if r.test_case_id == tc.id), None)
        v2_output = next((r.output for r in v2_results if r.test_case_id == tc.id), None)

        if not v1_output:
            v1_output = run_prompt(v1.content, tc.input, model)
            v1_emb = generate_embedding(v1_output)
            add_test_result(v1.id, tc.id, v1_output, model)
        else:
            v1_emb = generate_embedding(v1_output)

        if not v2_output:
            v2_output = run_prompt(v2.content, tc.input, model)
            v2_emb = generate_embedding(v2_output)
            add_test_result(v2.id, tc.id, v2_output, model)
        else:
            v2_emb = generate_embedding(v2_output)

        e1 = load_embedding(v1_emb)
        e2 = load_embedding(v2_emb)
        distance = cosine_distance(e1, e2)
        status = "STABLE" if distance < 0.2 else "CHANGED"

        comparisons.append({
            "test_name": tc.name,
            "input": tc.input,
            "v1_output": v1_output,
            "v2_output": v2_output,
            "distance": distance,
            "description": describe_distance(distance),
            "status": status
        })

    return comparisons