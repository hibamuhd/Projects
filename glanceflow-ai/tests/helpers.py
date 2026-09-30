import time

from src.llm import LLMResponse


class FakeLLM:
    name = "fake"

    def __init__(self, fn):
        self.fn, self.calls = fn, 0

    def complete(self, system, user, max_tokens=400):
        self.calls += 1
        out = self.fn(system, user)
        return out if isinstance(out, LLMResponse) else LLMResponse(out, 50, 20)


def slow_llm(seconds):
    def fn(system, user):
        time.sleep(seconds)
        return "{}"
    return FakeLLM(fn)
