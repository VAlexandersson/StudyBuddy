import textwrap
import torch
import pandas as pd
import numpy as np
from time import perf_counter 
from sentence_transformers import SentenceTransformer, util

 
def print_wrapped(text, width = 80):
    print(textwrap.fill(text, width))

    
def retrieve_relevant_resources(query: str,
                                embeddings: torch.tensor,
                                embedding_model: SentenceTransformer,
                                n_resources_to_return: int=5,
                                print_time: bool=True):
    """
    Embeds a query with model and returns top k scores and indices from embeddings.
    """
    # Embed query
    query_embedding = embedding_model.encode(query, convert_to_tensor=True)
    
    # Get dot product scores on embeddings
    start_time = perf_counter()
    dot_scores = util.dot_score(a=query_embedding, b=embeddings)[0]
    end_time = perf_counter()
    
    if print_time:
        print(f"Time taken to compute dot scores on ({len(embeddings)}): {end_time - start_time} seconds")
    scores, indices = torch.topk(dot_scores, k=n_resources_to_return)
    return scores, indices


def print_top_results_and_scores(scores: torch.tensor,
                                 indices: torch.tensor,
                                 pages_and_chunks: list[dict]):
    """"
    Retrieves the top results prints their text, chapter and score out.
    """ 
    for score, idx in zip(scores, indices):
        print_wrapped(f"Score: {score.item()}")
        print_wrapped(f"Chapter: {pages_and_chunks[idx]['chapter']}")
        print("Text:")
        print_wrapped(pages_and_chunks[idx]['text'])
        print("\n")

def import_chunks_with_embeddings(csv_path: str):
    """
    Imports the chunks with embeddings from a csv file.
    """
    text_chunks_with_embeddings_df = pd.read_csv(csv_path, index_col=0)
    text_chunks_with_embeddings_df['embedding'] = text_chunks_with_embeddings_df['embedding'].apply(lambda x: np.fromstring(x[1:-1], sep=' '))
    chunks_with_embeddings = text_chunks_with_embeddings_df.to_dict(orient='records')
    return chunks_with_embeddings

def get_chunks_embeddings_as_tensor(chunks_with_embeddings: list[dict]):
    """
    Converts the embeddings of chunks to a tensor.
    """
    embeddings_list = [chunk['embedding'] for chunk in chunks_with_embeddings]
    embeddings = torch.tensor(np.stack(embeddings_list, axis=0), dtype=torch.float32)
    # embeddings = torch.tensor(np.stack(chunks_with_embeddings['embedding'].tolist(), axis=0), dtype=torch.float32)
    return embeddings