from app.phase3_rag import build_prompt, grounded_answer


def test_prompt_forbids_unsupported_claims():
    prompt = build_prompt("What should we do?", [{"title": "OEM Brake Manual", "authority": "HIGH", "text": "Inspect brake chamber before return to service."}])
    assert "ONLY the approved evidence" in prompt
    assert "INSUFFICIENT_APPROVED_EVIDENCE" in prompt


def test_no_evidence_falls_back_safely():
    result = grounded_answer("What repair is needed?", [])
    assert result.grounded is False
    assert result.answer == "INSUFFICIENT_APPROVED_EVIDENCE"


def test_generated_answer_must_reference_evidence():
    class Tokenizer:
        def __call__(self, prompt, return_tensors):
            return {"input_ids": FakeTensor([[1, 2]])}
        def decode(self, output, skip_special_tokens=True):
            return "Source 1: inspect the brake chamber."

    class FakeTensor:
        def __init__(self, value): self.value = value
        @property
        def shape(self): return (1, len(self.value[0]))
        def __getitem__(self, item): return self

    class Model:
        def generate(self, **kwargs): return FakeTensor([[3, 4]])

    evidence = [{"title": "OEM Brake Manual", "authority": "HIGH", "text": "Inspect brake chamber."}]
    result = grounded_answer("What should be checked?", evidence, tokenizer=Tokenizer(), model=Model())
    assert result.grounded is True
    assert result.evidence == evidence
