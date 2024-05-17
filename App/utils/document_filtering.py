def filter_documents(documents, min_length=50):
    filtered_documents = [doc for doc in documents if len(doc) >= min_length]
    return filtered_documents