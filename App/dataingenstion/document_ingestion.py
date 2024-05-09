import fitz
import pandas as pd
import spacy
import re
import uuid
from to_markdown import to_markdown
from data_processing import remove_headers_and_footers, create_blocks_df, create_sentences_df, assign_chapters, determine_block_type


def document_ingestion(file_path:str, start_page: int=None, end_page: int = None):
    
    doc = fitz.open(file_path)
    
    
    if start_page is None:
        start_page = 0
    if end_page is None:
        end_page = doc.page_count
        
    pages = range(start_page, end_page)
    
    md_pages = to_markdown(doc, pages=pages)
    
    md_pages = remove_headers_and_footers(md_pages)


    pages_df = pd.DataFrame(md_pages)
    pages_df = pages_df.rename(columns={"document": "text"})
    pages_df['order_id'] = range(1, len(md_pages) + 1)
    pages_df['id'] = [uuid.uuid4() for _ in range(len(md_pages))]

    blocks_df = create_blocks_df(pages_df)
    pages_df.drop(columns=['blocks'], inplace=True)
    sentences_df = create_sentences_df(blocks_df)

    assign_chapters(sentences_df)

    chapters_df = sentences_df.groupby('block_id')[['chapter', 'parent_chapter']].first().reset_index()
    blocks_df = blocks_df.merge(chapters_df, left_on='id', right_on='block_id', how='left')
    blocks_df = blocks_df.drop(columns=['block_id'])

    chapters_df = blocks_df.groupby('page_id')[['chapter', 'parent_chapter']].first().reset_index()
    pages_df = pages_df.merge(chapters_df, left_on='id', right_on='page_id', how='left')
    pages_df = pages_df.drop(columns=['page_id'])

    blocks_df = blocks_df[~blocks_df["text"].str.startswith("#")]
    sentences_df = sentences_df[~sentences_df["text"].str.startswith("#")]

    blocks_df['block_type'] = blocks_df['text'].apply(determine_block_type)

    # ... (perform any further processing or return the DataFrames)