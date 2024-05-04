import pandas as pd
import numpy as np
import torch

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