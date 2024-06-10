from models.data_models import DocumentObject
from typing import List
from knowledge_base.retrieval_interface import RetrieveDocumentsInterface

class KnowledgeBaseInterface(RetrieveDocumentsInterface):
# TODO: when we using more then one db
  def add_data(self, documents: List[DocumentObject]):
    pass
