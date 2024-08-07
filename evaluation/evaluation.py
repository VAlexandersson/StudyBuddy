import nltk
nltk.download('punkt')

import json
from src.rag_system import RAGSystem
from typing import List, Dict
from tabulate import tabulate
import textwrap
import pandas as pd
import os
from rouge import Rouge
from nltk.translate.bleu_score import sentence_bleu
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np
from collections import Counter

class RAGEvaluator:
    def __init__(self, rag_system: RAGSystem, dataset_path: str = None):
        self.dataset = self.load_dataset(dataset_path)
        self.rag_system = rag_system
        self.rouge = Rouge()
        self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')

    def load_dataset(self, path: str) -> List[Dict]:
        if path:
            with open(path, 'r') as f:
                return json.load(f)
        else:
            return [
                {
                    "query": "Explain how a deficiency in vitamin D can negatively affect bone health",
                    "ground_truth": "Vitamin D plays a crucial role in maintaining blood calcium homeostasis, which is essential for bone health. Our bones are constantly being remodeled throughout our lives, meaning old bone is broken down and new bone is built up. This process requires a steady supply of calcium. [362]\nVitamin D works in conjunction with parathyroid hormone (PTH) to regulate blood calcium levels. When blood calcium levels drop, PTH is released, which stimulates the conversion of vitamin D to its active form, calcitriol. Calcitriol increases calcium absorption in the intestine and works with PTH to reduce calcium loss in urine and stimulate the release of calcium from bone. [369]\nWithout adequate vitamin D, the body can't absorb enough calcium to support the continuous rebuilding of bone tissue during remodeling. This leads to poor bone mineralization, resulting in weaker bones that are more prone to fracture. [392] In children, this deficiency manifests as rickets, a disease characterized by soft, weak, and deformed bones. In adults, it leads to osteomalacia, with softening of bones, reduced bone mineral density, and increased risk of osteoporosis. [363, 392]"
                },
                {
                    "query": "How does the process of photosynthesis contribute to the food we eat?",
                    "ground_truth": "Photosynthesis is the process by which plants capture energy from the sun and convert it into glucose (a type of sugar). This glucose is stored in plants as starch, which is found in seeds, roots, and tubers. When we eat plant foods containing starch, our bodies digest the starch into glucose, which is then absorbed into our bloodstream and used as an energy source by our cells. (order: 10)\nAdditionally, animals that we eat, such as cows and chickens, also rely on photosynthesis. They eat plants to obtain energy, and this energy is passed on to us when we consume these animals. (order: 9)\nEssentially, every food item we consume can be traced back to photosynthesis, as it forms the basis of the food chain. (order: 9)"
                }
            ]

    def calculate_rouge(self, hypothesis, reference):
        scores = self.rouge.get_scores(hypothesis, reference)
        return {
            'rouge-1': scores[0]['rouge-1']['f'],
            'rouge-2': scores[0]['rouge-2']['f'],
            'rouge-l': scores[0]['rouge-l']['f']
        }

    def calculate_bleu(self, hypothesis, reference):
        return sentence_bleu([reference.split()], hypothesis.split())

    def calculate_semantic_similarity(self, hypothesis, reference):
        hyp_embedding = self.sentence_model.encode([hypothesis])[0]
        ref_embedding = self.sentence_model.encode([reference])[0]
        return cosine_similarity([hyp_embedding], [ref_embedding])[0][0]

    def calculate_exact_match(self, hypothesis, reference):
        return int(hypothesis.strip().lower() == reference.strip().lower())

    def calculate_f1_score(self, hypothesis, reference):
        hyp_tokens = hypothesis.lower().split()
        ref_tokens = reference.lower().split()
        
        common = Counter(hyp_tokens) & Counter(ref_tokens)
        num_same = sum(common.values())
        
        if len(hyp_tokens) == 0 or len(ref_tokens) == 0:
            return int(hyp_tokens == ref_tokens)
        
        precision = 1.0 * num_same / len(hyp_tokens)
        recall = 1.0 * num_same / len(ref_tokens)
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        return f1

    def calculate_answer_relevancy(self, query, response):
        query_embedding = self.sentence_model.encode([query])[0]
        response_embedding = self.sentence_model.encode([response])[0]
        return cosine_similarity([query_embedding], [response_embedding])[0][0]

    async def run(self):
        results = []
        
        for instance in self.dataset:
            query = instance['query']
            ground_truth = instance.get('ground_truth', None)

            response = await self.rag_system.process_query(query)

            rouge_scores = self.calculate_rouge(response.answer, ground_truth)
            metrics = {
                "rouge_scores": rouge_scores,
                "bleu_score": self.calculate_bleu(response.answer, ground_truth),
                "semantic_similarity": self.calculate_semantic_similarity(response.answer, ground_truth),
                "exact_match": self.calculate_exact_match(response.answer, ground_truth),
                "f1_score": self.calculate_f1_score(response.answer, ground_truth),
                "answer_relevancy": self.calculate_answer_relevancy(query, response.answer)
            }

            results.append({
                "query": query,
                "response": response.answer,
                "ground_truth": ground_truth,
                **metrics
            })

            print(f"Query: {query}")
            print(f"Response: {response.answer}")
            if ground_truth:
                print(f"Ground Truth: {ground_truth}")
            print(f"Metrics: {metrics}\n")

        df = pd.DataFrame(results)

        def wrap_text(text, width=50):
            if isinstance(text, str):
                return "\n".join(textwrap.wrap(text, width=width))
            return text
        
        for col in ['query', 'response', 'ground_truth']:
            df[col] = df[col].apply(wrap_text)
        
        df['rouge_scores'] = df['rouge_scores'].apply(lambda x: f"ROUGE-1: {x['rouge-1']:.5f}\nROUGE-2: {x['rouge-2']:.5f}\nROUGE-L: {x['rouge-l']:.5f}")
        
        numeric_cols = ['bleu_score', 'semantic_similarity', 'exact_match', 'f1_score', 'answer_relevancy']
        for col in numeric_cols:
            df[col] = df[col].apply(lambda x: f"{x:.5f}")
        
        print(tabulate(df, headers='keys', tablefmt='grid'))


        summary_df = df[['rouge_scores', 'bleu_score', 'semantic_similarity', 'exact_match', 'f1_score', 'answer_relevancy']]
        summary_df['rouge_scores'] = summary_df['rouge_scores'].apply(lambda x: x.replace('\n', ', '))
        
        print("\nSummary Results:")
        print(tabulate(summary_df, headers='keys', tablefmt='simple'))
        
        
        output_path = os.path.join(os.getcwd(), 'results.csv')
        df.to_csv(output_path, index=False)
        print(f"Results saved to {output_path}")

        avg_scores = {
            'ROUGE-1': df['rouge_scores'].apply(lambda x: float(x.split('\n')[0].split(': ')[1])).mean(),
            'ROUGE-2': df['rouge_scores'].apply(lambda x: float(x.split('\n')[1].split(': ')[1])).mean(),
            'ROUGE-L': df['rouge_scores'].apply(lambda x: float(x.split('\n')[2].split(': ')[1])).mean(),
            'BLEU': df['bleu_score'].apply(float).mean(),
            'Semantic Similarity': df['semantic_similarity'].apply(float).mean(),
            'Exact Match': df['exact_match'].apply(float).mean(),
            'F1 Score': df['f1_score'].apply(float).mean(),
            'Answer Relevancy': df['answer_relevancy'].apply(float).mean()
        }
        print("\nAverage Scores:")
        for metric, score in avg_scores.items():
            print(f"{metric}: {score:.5f}")