from objects.document import DocumentObject

def concat_documents(retrieved_documents: DocumentObject) -> str:
    documents = [doc.document for doc in retrieved_documents]
    return "\n-  ".join(documents)