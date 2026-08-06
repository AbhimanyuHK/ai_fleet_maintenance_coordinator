from __future__ import annotations

from functools import lru_cache
from typing import Iterable

MODEL_ID = "Qwen/Qwen2.5-3B-Instruct"


def ai_runtime_available() -> bool:
    try:
        import torch  # noqa: F401
        import transformers  # noqa: F401
        return True
    except ImportError:
        return False


@lru_cache(maxsize=1)
def _load_model():
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype="auto",
        device_map="auto",
    )
    return tokenizer, model


def generate_answer(question: str, evidence: Iterable[str]) -> str:
    """Generate a grounded answer using only retrieved evidence.

    The model is optional and loaded lazily so CI and the data foundation do not
    require a multi-GB model download.
    """
    if not ai_runtime_available():
        raise RuntimeError("AI runtime is not installed. Install requirements-ai.txt first.")

    context = "\n\n---\n\n".join(evidence)
    if not context.strip():
        return "No approved knowledge evidence was retrieved. No recommendation should be made."

    tokenizer, model = _load_model()
    messages = [
        {
            "role": "system",
            "content": (
                "You are a fleet maintenance assistant. Use only the supplied approved evidence. "
                "Do not invent OEM procedures, fault codes, warranty rules, or compliance requirements. "
                "If the evidence is insufficient, say so. Return a concise recommendation and cite "
                "the evidence by its supplied labels. Human approval is required for operational action."
            ),
        },
        {
            "role": "user",
            "content": f"Question:\n{question}\n\nApproved evidence:\n{context}",
        },
    ]
    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([prompt], return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=350, do_sample=False)
    generated = outputs[0][inputs.input_ids.shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True).strip()
