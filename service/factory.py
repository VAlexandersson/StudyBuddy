# services/factory.py
from .text_generation.transformer_service import TransformerTextGenerationService
from .classification.transformer_service import TransformerClassificationService
from .reranking.transformer_service import TransformerRerankingService
# Import other services as needed

class ServiceFactory:
    @staticmethod
    def create_service(service_type: str):
      if service_type == 'text_generation':
        return TransformerTextGenerationService()
      elif service_type == 'classification':
        return TransformerClassificationService()
      elif service_type == 'reranking':
        return TransformerRerankingService()
      else:
        raise ValueError(f"Unknown service type: {service_type}")