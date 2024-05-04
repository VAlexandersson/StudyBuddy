import torch
from sentence_transformers import SentenceTransformer, util

def retrieve_relevant_resources(query: str,
                                embeddings: torch.tensor,
                                embedding_model: SentenceTransformer,
                                n_resources_to_return: int=5):
    """
    Embeds a query with model and returns top k scores and indices from embeddings.
    """
    # Embed query
    query_embedding = embedding_model.encode(query, convert_to_tensor=True)
    
    # Get dot product scores on embeddings
    dot_scores = util.dot_score(a=query_embedding, b=embeddings)[0]
    
    scores, indices = torch.topk(dot_scores, k=n_resources_to_return)
    return scores, indices
