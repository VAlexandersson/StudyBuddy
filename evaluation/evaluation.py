
import shutil

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
from collections import Counter

import nltk
nltk.download('punkt')

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
                    "query": "How do bile salts contribute to both the emulsification and absorption of lipids in the small intestine?",
                    "ground_truth": "Bile salts play a dual role in lipid digestion and absorption in the small intestine. First, they act as emulsifiers, breaking large fat globules into smaller droplets. This increases the surface area for digestive enzymes to act upon. Later in the process, bile salts help with absorption by clustering around the products of fat digestion to form structures called micelles. These micelles help the fats get close enough to the microvilli of intestinal cells for absorption to occur."
                },
                {
                    "query": "Explain how a deficiency in vitamin D can negatively affect bone health",
                    "ground_truth": "Vitamin D plays a crucial role in maintaining blood calcium homeostasis, which is essential for bone health. Our bones are constantly being remodeled throughout our lives, meaning old bone is broken down and new bone is built up. This process requires a steady supply of calcium. [362]\nVitamin D works in conjunction with parathyroid hormone (PTH) to regulate blood calcium levels. When blood calcium levels drop, PTH is released, which stimulates the conversion of vitamin D to its active form, calcitriol. Calcitriol increases calcium absorption in the intestine and works with PTH to reduce calcium loss in urine and stimulate the release of calcium from bone. [369]\nWithout adequate vitamin D, the body can't absorb enough calcium to support the continuous rebuilding of bone tissue during remodeling. This leads to poor bone mineralization, resulting in weaker bones that are more prone to fracture. [392] In children, this deficiency manifests as rickets, a disease characterized by soft, weak, and deformed bones. In adults, it leads to osteomalacia, with softening of bones, reduced bone mineral density, and increased risk of osteoporosis. [363, 392]"
                },
                {
                    "query": "How does the process of photosynthesis contribute to the food we eat?",
                    "ground_truth": "Photosynthesis is the process by which plants capture energy from the sun and convert it into glucose (a type of sugar). This glucose is stored in plants as starch, which is found in seeds, roots, and tubers. When we eat plant foods containing starch, our bodies digest the starch into glucose, which is then absorbed into our bloodstream and used as an energy source by our cells. (order: 10)\nAdditionally, animals that we eat, such as cows and chickens, also rely on photosynthesis. They eat plants to obtain energy, and this energy is passed on to us when we consume these animals. (order: 9)\nEssentially, every food item we consume can be traced back to photosynthesis, as it forms the basis of the food chain. (order: 9)"
                },
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
                "sem_sim": self.calculate_semantic_similarity(response.answer, ground_truth),
                "f1_score": self.calculate_f1_score(response.answer, ground_truth),
                "ans_rel": self.calculate_answer_relevancy(query, response.answer)
            }

            results.append({
                "query": query,
                "response": response.answer,
                "ground_truth": ground_truth,
                "metrics": metrics
            })

        df = pd.DataFrame(results)

        def wrap_text(text, width=None):
            if width is None:
                width = shutil.get_terminal_size().columns
            if isinstance(text, str):
                return "\n".join(textwrap.wrap(text, width=width-20))
            return text
        
        for col in ['query', 'response', 'ground_truth']:
            df[col] = df[col].apply(wrap_text)


        def format_metrics(metrics):
            formatted_metrics = []
            for k, v in metrics.items():
                if k == "rouge_scores":
                    formatted_metrics.append(f"{k}:")
                    for rouge_k, rouge_v in v.items():
                        formatted_metrics.append(f"  {rouge_k}: {rouge_v:.4f}")
                else:
                    formatted_metrics.append(f"{k}: {v:.4f}")
            return "\n".join(formatted_metrics)


        df['metrics'] = df['metrics'].apply(format_metrics)


        for index, row in df.iterrows():
            query_df = pd.DataFrame({
                'evaluation': [row['query'], row['response'], row['ground_truth'], row['metrics']],
            }, index=['query', 'response', 'ground_truth', 'metrics'])

            print(tabulate(query_df, headers=[], tablefmt='grid'))


        output_path = os.path.join(os.getcwd(), 'results.csv')
        df.to_csv(output_path, index=False)
        print(f"Results saved to {output_path}")