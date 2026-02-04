from typing import Any, List, Optional
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from huggingface_hub import InferenceClient
import os
from pydantic import PrivateAttr

class CustomHuggingFaceLLM(LLM):
    repo_id: str
    temperature: float = 0.1
    max_new_tokens: int = 512
    # Private attribute to hold the client (not serialized/validated by Pydantic)
    _client: Any = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        self._client = InferenceClient(model=self.repo_id, token=token)

    @property
    def _llm_type(self) -> str:
        return "custom_huggingface"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        try:
            # Try text_generation first
            response = self._client.text_generation(
                prompt,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature,
                stop_sequences=stop if stop else []
            )
            return response
        except Exception as e:
            # Fallback for chat-only models
            print(f"Text generation failed, retrying with chat completion: {e}")
            try:
                messages = [{"role": "user", "content": prompt}]
                response = self._client.chat_completion(
                    messages=messages,
                    max_tokens=self.max_new_tokens,
                    temperature=self.temperature,
                    stop=stop if stop else []
                )
                return response.choices[0].message.content
            except Exception as e2:
                raise ValueError(f"Error calling HuggingFace Inference API: {e2}")
