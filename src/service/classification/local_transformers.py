from src.interfaces.services.classification import ClassificationService
from typing import Any, Dict, List
from transformers import pipeline
import asyncio

class LocalTransformerClassification(ClassificationService):
    def __init__(self, model_id: str) -> None:
        self.zero_shot_classifier = pipeline(
            "zero-shot-classification", 
            model=model_id
        )

    async def classify(self, query: str, labels: List[str], hypothesis_template: str, multi_label: bool = True) -> Dict[str, Any]:
        loop = asyncio.get_event_loop()
        output = await loop.run_in_executor(
            None,
            self._classify_sync,
            query,
            labels,
            hypothesis_template,
            multi_label
        )
        return output

    def _classify_sync(self, query: str, labels: List[str], hypothesis_template: str, multi_label: bool):
        return self.zero_shot_classifier(
            sequences=query,
            candidate_labels=labels,
            hypothesis_template=hypothesis_template,
            multi_label=multi_label
        )