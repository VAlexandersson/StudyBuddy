# services/service_manager.py
from typing import List, Dict

from .factory import ServiceFactory

class ServiceManager:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        self.services: Dict[str, object] = {}
        self._initialize_all_services()
    
    def _initialize_all_services(self):
        service_types = self._get_service_types()
        for service_type in service_types:
            self.services[service_type] = ServiceFactory.create_service(service_type)
        print("All services initialized successfully.")
    
    @staticmethod
    def _get_service_types() -> List[str]:
        return [
            'text_generation',
            'rerank',
            'classification'
            # Add any other service types here
        ]
    
    @classmethod
    def get_service(cls, service_type: str):
      """
      Retrieves the specified service from the service manager.
      'text_generation', 'rerank', 'classification'.

      Args:
        service_type (str): The type of service to retrieve.

      Returns:
        object: The instance of the specified service.

      Raises:
        ValueError: If the specified service is not initialized.
      """
      instance = cls.get_instance()
      if service_type not in instance.services:
        raise ValueError(f"Service {service_type} is not initialized")
      return instance.services[service_type]