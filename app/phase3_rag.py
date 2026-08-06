from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.phase3_embeddings import MODEL_NAME

DEFAULT_LLM = "Qwen/Qwen2.5-3B-Instruct"


@dataclass(frozen=True)
class RAGAnswer:
    answer: str
    evidence: list[dict[str, Any]]
    grounded: bool
    model: str


def build_prompt(question: str, evidence: list[dict[str, Any]]) -> str:
    context = "\n\n".join(
        f"SOURCE {i}: {item.get('title', 'Unknown')} | authority={item.get('authority', 'unknown')}\n{item.get('text', '')}"
        for i, item in enumerate(evidence, 1)
    )
    return f"""You are a fleet maintenance knowledge assistant. Use ONLY the approved evidence below. Do not invent procedures, warranty decisions, compliance requirements, or technical facts. If the evidence is insufficient, say exactly: INSUFFICIENT_APPROVED_EVIDENCE. Do not make a final repair authorization decision. Return a concise recommendation, reason, and source numbers.\n\nAPPROVED EVIDENCE:\n{context}\n\nQUESTION:\n{question}\n\nANSWER:"""


def grounded_answer(question: str, evidence: list[dict[str, Any]], model_name: str = DEFAULT_LLM, tokenizer: Any = None, model: Any = None) -> RAGAnswer:
    if not evidence:
        return RAGAnswer("INSUFFICIENT_APPROVED_EVIDENCE", [], False, model_name)
    if tokenizer is None or model is None:
        raise RuntimeError("Qwen runtime is not loaded. Install requirements-ai.txt and provide tokenizer/model.")
    prompt = build_prompt(question, evidence)
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=300, do_sample=False)
    generated = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()
    grounded = "INSUFFICIENT_APPROVED_EVIDENCE" not in generated and any(str(i) in generated for i in range(1, min(len(evidence), 3) + 1))
    if not grounded:
        generated = "INSUFFICIENT_APPROVED_EVIDENCE"
    return RAGAnswer(generated, evidence, grounded, model_name)


def load_qwen(model_name: str = DEFAULT_LLM):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto", device_map="auto")
    return tokenizer, model
