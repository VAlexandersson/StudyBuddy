from tqdm import tqdm
from difflib import SequenceMatcher
from typing import List, Dict, Tuple
import pandas as pd
import uuid


def similar(a: str, b: str, matcher=SequenceMatcher(None, '', '')) -> float:
    matcher.set_seqs(a, b)
    return matcher.ratio()


def identify_potential_headers_or_footers(blocks: List[str], threshold: float = 0.8) -> List[Tuple[int, List[int]]]:
    potential_blocks = []
    for i, block in tqdm(enumerate(blocks)):
        similarities = [similar(block, other_block) for other_block in blocks]
        similar_indices = [j for j, sim in enumerate(similarities) if sim > threshold]
        if len(similar_indices) > 1:
            potential_blocks.append((i, similar_indices))
    return potential_blocks


def has_header_or_footer(num_pages: int, potential_blocks: List[Tuple[int, List[int]]]) -> List[bool]:
    block_indices = {index for index, _ in potential_blocks}
    return [i in block_indices for i in range(num_pages)]


def remove_headers_or_footers(md_p: List[Dict], header: bool, has_block: List[bool]) -> List[Dict]:
    for page, has_header_or_footer in zip(md_p, has_block):
        if has_header_or_footer:
            page["blocks"] = page["blocks"][1:] if header else page["blocks"][:-1]
    return md_p


def remove_headers_and_footers(md_p: List[Dict]) -> List[Dict]:
    for header in [True, False]:
        print("Removing potential headers") if header else print("Removing potential footers")
        blocks = [page["blocks"][0 if header else -1] for page in md_p if page["blocks"]]
        potential_blocks = identify_potential_headers_or_footers(blocks)
        has_block = has_header_or_footer(len(md_p), potential_blocks)
        md_p = remove_headers_or_footers(md_p, header, has_block)
    return md_p


# create a dataframe with the pages, blocks and sentences
import spacy
import re

def create_blocks_df(md_pages_df):
    blocks = []
    for _, row in md_pages_df.iterrows():
        for block in row['blocks']:
            blocks.append({
                "id": uuid.uuid4(),
                "order_id": len(blocks), 
                "text": block, 
                "page_number": row["page_number"], 
                "page_id": row["id"]
            })

    blocks_df = pd.DataFrame(blocks)
    return blocks_df

def create_sentences_df(blocks_df):
    nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser", "ner"])
    nlp.add_pipe("sentencizer")
    sentences = []
    for _, row in blocks_df.iterrows():
        doc = nlp(row['text'])
        for sent in doc.sents:
            sentences.append({
                "id": uuid.uuid4(),
                "order_id": len(sentences),
                "text": sent.text, 
                "block_id": row["id"]})

    sentences_df = pd.DataFrame(sentences)
    return sentences_df

def assign_chapters(df):
    chapters = []
    current_chapter = "None"
    parent_chapter = "None"
    for idx, row in df.iterrows():
        chapter_level = 0
        if row['text'].startswith('#'):
            chapter_level = row['text'].split(" ")[0].count('#')
            if not chapters or chapters[-1][1] < chapter_level:
                chapters.append((row['text'], chapter_level))
            else:
                while(chapters and chapters[-1][1] >= chapter_level):
                    chapters.pop()
                chapters.append((row['text'], chapter_level))
            current_chapter = chapters[-1][0]
            if len(chapters) > 1:
                parent_chapter = chapters[-2][0]
                
        df.at[idx, 'chapter'] = current_chapter.replace('#', '') 
        df.at[idx, 'parent_chapter'] = parent_chapter.replace('#', '')


def determine_block_type(text):
    if re.search(r'^\s*\d+\.\s', text):
        return 'numbered_list'
    elif re.search(r'^\s*[-]\s', text):
        return 'bullet_list'
    elif re.search(r'^\s*[|]\s', text):
        return 'table'
    elif re.search(r'^\s*[>]\s', text):
        return 'quote'
    elif re.search(r'^\s*#+\s', text):
        return 'header'
    elif re.search(r'^\s*\w+\s*=', text) or re.search(r'^\s*\w+\s*:=', text):
        return 'code'
    elif re.search(r'^\s*class\s+\w+', text) or re.search(r'^\s*def\s+\w+', text):
        return 'code'
    elif re.search(r'^\s*if\s+', text) or re.search(r'^\s*for\s+', text) or re.search(r'^\s*while\s+', text):
        return 'code'
    elif re.search(r'^\s*import\s+', text) or re.search(r'^\s*from\s+', text):
        return 'code'
    else:
        return 'n/a'