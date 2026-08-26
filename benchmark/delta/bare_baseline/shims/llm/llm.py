from __future__ import annotations

import json
import os

import httpx
from openai import OpenAI
from transformers import AutoTokenizer


VLLM_MAX_NEW_TOKENS = int(os.getenv("DELTA_VLLM_MAX_NEW_TOKENS", "2048"))
VLLM_BASE_URL = os.getenv("DELTA_VLLM_BASE_URL", "http://127.0.0.1:8004/v1")
VLLM_API_KEY = os.getenv("DELTA_VLLM_API_KEY", "not-needed")
VLLM_MODEL = os.getenv("DELTA_VLLM_MODEL", "Qwen3.6-27B")
VLLM_TOKENIZER = os.getenv("DELTA_VLLM_TOKENIZER", VLLM_MODEL)
VLLM_TIMEOUT = float(os.getenv("DELTA_VLLM_TIMEOUT_SEC", "900"))


class LLMBase:
    def __init__(self, temp: float = 0.0, top_p: float = 1.0):
        self.temperature = temp
        self.top_p = top_p
        self.prompt_chain: list[dict[str, str]] = []

    def reset(self):
        self.prompt_chain = []

    def init_prompt_chain(self, content: str, prompt: str):
        assert len(self.prompt_chain) == 0, "Prompt chain is not empty!"
        self.prompt_chain.extend(
            [
                {"role": "system", "content": content},
                {"role": "user", "content": prompt},
            ]
        )

    def update_prompt_chain(self, content: str, prompt: str):
        self.prompt_chain[0]["content"] = content
        self.prompt_chain.append({"role": "user", "content": prompt})

    def update_prompt_chain_w_response(self, response: str, role: str = "assistant"):
        self.prompt_chain.append({"role": role, "content": response})

    @staticmethod
    def log(context: str, save_name: str):
        with open(save_name, "w", encoding="utf-8") as f:
            f.write(context)


class LocalVLLM(LLMBase):
    def __init__(self, model_name: str, temp: float = 0.0, top_p: float = 1.0):
        super().__init__(temp, top_p)
        self.model_id = model_name or VLLM_MODEL
        self.client = OpenAI(
            api_key=VLLM_API_KEY,
            base_url=VLLM_BASE_URL,
            timeout=VLLM_TIMEOUT,
            max_retries=2,
            http_client=httpx.Client(timeout=VLLM_TIMEOUT, trust_env=False),
        )
        self.tokenizer = None
        for candidate in [VLLM_TOKENIZER, self.model_id, VLLM_MODEL]:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(
                    candidate,
                    trust_remote_code=True,
                    local_files_only=True,
                )
                break
            except Exception:
                continue

    def count_tokens(self, string: str):
        if self.tokenizer is not None:
            try:
                return len(self.tokenizer.encode(string))
            except Exception:
                pass
        return max(1, len(string) // 4)

    def _chat_request(self, messages: list[dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=messages,
            temperature=self.temperature,
            top_p=self.top_p,
            max_tokens=VLLM_MAX_NEW_TOKENS,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
        message = response.choices[0].message
        if isinstance(message.content, str) and message.content.strip():
            return message.content
        return json.dumps(response.model_dump(), ensure_ascii=False)

    def query(self, content: str, prompt: str):
        return self._chat_request(
            [
                {"role": "system", "content": content},
                {"role": "user", "content": prompt},
            ]
        )

    def query_msg_chain(self):
        return self._chat_request(self.prompt_chain)


def load_llm(model_name: str, temp: float = 0.0, top_p: float = 1.0):
    return LocalVLLM(model_name, temp, top_p)
