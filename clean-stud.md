```python
import importlib
import resource_utils
importlib.reload(resource_utils)
from resource_utils import get_total_vram, get_available_vram, get_gpu_processes_usage, kill_gpu_processes

print(f"PROCCESSES: ", get_gpu_processes_usage())
print("TOTAL VRAM: ", get_total_vram())
print("AVAILABLE VRAM: ", get_available_vram())
```

    PROCCESSES:  []
    TOTAL VRAM:  23.988
    AVAILABLE VRAM:  23.613



```python
kill_gpu_processes(get_gpu_processes_usage(), verbose=True)
```


```python
import torch
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForCausalLM
import pandas as pd
import numpy as np
import random

with open('questions.md', 'r') as file:
    query_list = file.read().splitlines()

CONFIG = {
    'csv_path': './data/text_chunks_with_embeddings.csv',
    'device': 'cuda' if torch.cuda.is_available() else 'cpu',
    'attn_implementation': 'sdpa',
    'model_id': 'meta-llama/Meta-Llama-3-8B-Instruct',
    'embedding_model_id': 'all-mpnet-base-v2',
}

SYS_PROMPT = {
    "education": """
    You are Study-Buddy. An educational chatbot that will aid students in their studies.
    You are given the extracted parts of curriculum specific documents and a question. Provide a conversational and educational answer with good and easily read formatting.
    Give yourself room to think by extracting relevant passages from the context before answering the query.
    Don't return the thinking, only return the answer.
    If you don't know the answer, just say "I do not know." Don't make up an answer.
    """,
    "relevance": """
    You are a grader assessing relevance of a retrieved document to a user question. If the document contains keywords related to the user question, grade it as relevant. It does not need to be a stringent test. The goal is to filter out erroneous retrievals.
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.
    Provide the binary score as a JSON with a single key 'score' and no premable or explaination.
    """,
    "socratic_sage": """
    You are an AI assistant capable of having in-depth Socratic style conversations on a wide range of topics. Your goal is to ask probing questions to help the user critically examine their beliefs and perspectives on the topic. Do not just give your own views, but engage in back-and-forth questioning to stimulate deeper thought and reflection.
    """
}

```

## Text and Embedding


```python

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

# Load chunks and embeddings
chunks_with_embeddings = import_chunks_with_embeddings(CONFIG['csv_path'])
embeddings = get_chunks_embeddings_as_tensor(chunks_with_embeddings).to(CONFIG['device'])
```

## Retrieval and Inference

- Using Llama 3: https://huggingface.co/blog/llama3



```python
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


def generate_model_response(prompt: str, tokenizer, model, terminators, device="cuda"):
    input_ids = tokenizer.apply_chat_template(
        prompt,
        add_generation_prompt=True,
        return_tensors="pt"
    ).to(device)
    
    outputs = model.generate(
        input_ids, 
        max_new_tokens=1024, 
        eos_token_id=terminators,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
        pad_token_id=tokenizer.eos_token_id
    )
    
    # Generated response at outputs[0] but starting at position input_ids.shape[-1]. 
    # [input_ids.shape[-1]:] is done to remove the input tokens and only keep the generated text.
    response = outputs[0][input_ids.shape[-1]:] 
    return tokenizer.decode(response)


def get_user_prompt(query: str, retrieved_documents: list[dict]):
    """
    Formats the prompt with the query and the retreived documents.
    """
    base_prompt = f"Query: {query}\nContext:"
    for item in retrieved_documents:
        base_prompt += f"\n- {item['text']}"
    return base_prompt

def format_prompt(formatted_prompt: str, sys_prompt: str):
    message = [
        { "role": "system", "content": SYS_PROMPT[sys_prompt] },
        { "role": "user", "content": formatted_prompt }
    ]
    return message
```


```python
# Load models
embedding_model = SentenceTransformer(model_name_or_path=CONFIG['embedding_model_id'], device=CONFIG['device'])
tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=CONFIG['model_id'])
model = AutoModelForCausalLM.from_pretrained(
    pretrained_model_name_or_path=CONFIG['model_id'], 
    torch_dtype=torch.float16, 
    #low_cpu_mem_usage=False, 
    attn_implementation=CONFIG['attn_implementation']
    ).to(CONFIG['device'])

terminators = [
    tokenizer.eos_token_id,
    tokenizer.convert_tokens_to_ids("<|eot_id|>")
]
```

## Query


```python
query = random.choice(query_list)

# similarity scores and indices on chunk embeddings
scores, indices = retrieve_relevant_resources(
    query=query, 
    embeddings=embeddings, 
    embedding_model=embedding_model)

user_prompt = get_user_prompt(query=query, retrieved_documents=[chunks_with_embeddings[i] for i in indices])

formatted_prompt = format_prompt(user_prompt, "education") 

response = generate_model_response(formatted_prompt, tokenizer, model, terminators)

print(f"Query: {query}")
print("----")
print(response)
```

    Query: Why is achieving full distribution transparency often impractical or even undesirable?
    ----
    Achieving full distribution transparency is often impractical or even undesirable because it may not always be possible to hide all distribution aspects from users. In some cases, making distribution explicit can be beneficial, as it allows users and application developers to understand the sometimes unexpected behavior of a distributed system and be better prepared to deal with it. Additionally, hiding distribution can lead to poorly understood semantics, and may not be necessary or desirable in all situations, such as with location-based services that rely on exposing distribution.<|eot_id|>


TODO:
- Contextual Compression


## Test.


```python
q = "Why is achieving full distribution transparency often impractical or even undesirable?"
scores, indices = retrieve_relevant_resources(
    query=q, 
    embeddings=embeddings, 
    embedding_model=embedding_model)

```


```python
from helpers import print_top_results_and_scores

def grade_retreival(query: str, retrieved_document: str, verbose: bool = False, temperature: float = 0.6, top_p: float =0.9):
    """
    Grades the retrieval of documents based on the query.
    """
    
    # Adds retrieved documents to the prompt
    user_prompt = f"Query: {query}\nRetrieved Document: {retrieved_document}"
    
    # Format prompt with system info and user query
    message = format_prompt(user_prompt, "relevance")
    
    #message = [
    #    { "role": "system", "content": SYS_PROMPT['relevance'] },
    #    { "role": "user", "content": base_prompt }
    #]
    
    #  Apply chat template to prompt
    prompt = tokenizer.apply_chat_template(
        message,
        tokenize=False,
        add_generation_prompt=True #, 
        # return_tensors="pt"
    )

    # Tokenize prompt ( can be done in previous step with return_tensors="pt" and tokenize=True )
    input_ids =  tokenizer(prompt, return_tensors="pt").to(CONFIG['device'])["input_ids"]
    if verbose:
        print(prompt)
        #print(input_ids)
        print(input_ids.shape)
    # Generate response, gets it decoded.
    outputs = model.generate(
        input_ids, 
        max_new_tokens=256, 
        eos_token_id=terminators,
        do_sample=True,
        temperature=temperature,
        top_p=top_p,
        pad_token_id=tokenizer.eos_token_id
    )
    
    # Decode response
    outputs = outputs[0][input_ids.shape[-1]:]
    return outputs

retrieved_documents = [chunks_with_embeddings[i] for i in indices]
grad = grade_retreival(q, retrieved_documents[0]["text"], True)
    
```

    <|begin_of_text|><|start_header_id|>system<|end_header_id|>
    
    You are a grader assessing relevance of a retrieved document to a user question. If the document contains keywords related to the user question, grade it as relevant. It does not need to be a stringent test. The goal is to filter out erroneous retrievals.
        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.
        Provide the binary score as a JSON with a single key 'score' and no premable or explaination.<|eot_id|><|start_header_id|>user<|end_header_id|>
    
    Query: Why is achieving full distribution transparency often impractical or even undesirable?
    Retrieved Document: Although distribution transparency is generally considered preferable for any distributed system, there are situations in which blindly attempting to hide all distribution aspects from users is not a good idea. A simple example is requesting your electronic newspaper to appear in your mailbox before 7 AM local time, as usual, while you are currently at the other end of the world living in a different time zone. Your morning paper will not be the morning paper you are used to.<|eot_id|><|start_header_id|>assistant<|end_header_id|>
    
    
    torch.Size([1, 221])



```python
from helpers import print_wrapped
print(f"Q: {q}\n--")
print_wrapped(retrieved_documents[0]['text'])
output_text = tokenizer.decode(grad, skip_special_tokens=True)
print(output_text)
```

    Q: Why is achieving full distribution transparency often impractical or even undesirable?
    --
    Although distribution transparency is generally considered preferable for any
    distributed system, there are situations in which blindly attempting to hide all
    distribution aspects from users is not a good idea. A simple example is
    requesting your electronic newspaper to appear in your mailbox before 7 AM local
    time, as usual, while you are currently at the other end of the world living in
    a different time zone. Your morning paper will not be the morning paper you are
    used to.
    {"score": "yes"}



```python
for i, document in enumerate(retrieved_documents):
    grad = grade_retreival(q, document['text'])
    output_text = tokenizer.decode(grad, skip_special_tokens=True)
    print(f"assessment {i+1}: {output_text}")

```

    assessment 1: {"score": "no"}
    assessment 2: {"score": "yes"}
    assessment 3: {"score": "yes"}
    assessment 4: {"score": "no"}
    assessment 5: {"score": "yes"}



```python
def assess_documents(temperature = 0.6, top_p = 0.9):
    for i, document in enumerate(retrieved_documents):
        grad = grade_retreival(q, document['text'], False, temperature, top_p)
        output_text = tokenizer.decode(grad, skip_special_tokens=True)
        print(f"assessment {i+1}: {output_text}")
```


```python
assess_documents(temperature=0.6, top_p=0.9)
```

    assessment 1: {"score": "yes"}
    assessment 2: {"score": "yes"}
    assessment 3: {"score": "yes"}
    assessment 4: {"score": "no"}
    assessment 5: {"score": "no"}



```python
assess_documents(temperature=0.1, top_p=0.9)
```

    assessment 1: {"score": "no"}
    assessment 2: {"score": "yes"}
    assessment 3: {"score": "yes"}
    assessment 4: {"score": "no"}
    assessment 5: {"score": "yes"}



```python
for i, text in enumerate(retrieved_documents):
    print(f"<start_assessment_{i+1}>")
    print(f"QUERY:\n{q}")
    print("RETRIEVED TEXT:")
    print_wrapped(text['text'])
    grad = grade_retreival(q, text['text'])
    output_text = tokenizer.decode(grad, skip_special_tokens=True)
    print(f"RELEVANCE:\n{output_text}")
    print(f"<end_assessment_{i+1}>\n")

    
#grad = grade_retreival(q, chunks_with_embeddings[0]['text'])

#output_text = tokenizer.decode(grad, skip_special_tokens=True)
#print(output_text)

```

    <start_assessment_1>
    QUERY:
    Why is achieving full distribution transparency often impractical or even undesirable?
    RETRIEVED TEXT:
    Although distribution transparency is generally considered preferable for any
    distributed system, there are situations in which blindly attempting to hide all
    distribution aspects from users is not a good idea. A simple example is
    requesting your electronic newspaper to appear in your mailbox before 7 AM local
    time, as usual, while you are currently at the other end of the world living in
    a different time zone. Your morning paper will not be the morning paper you are
    used to.
    RELEVANCE:
    {"score": "no"}
    <end_assessment_1>
    
    <start_assessment_2>
    QUERY:
    Why is achieving full distribution transparency often impractical or even undesirable?
    RETRIEVED TEXT:
    There are other arguments against distribution transparency. Recognizing that
    full distribution transparency is simply impossible, we should ask ourselves
    whether it is even wise to pretend that we can achieve it. It may be much better
    to make distribution explicit so that the user and application developer are
    never tricked into believing that there is such a thing as transparency. The
    result will be that users will much better understand the (sometimes unexpected)
    behavior of a distributed system, and are thus much better prepared to deal with
    this behavior.
    RELEVANCE:
    {"score": "yes"}
    <end_assessment_2>
    
    <start_assessment_3>
    QUERY:
    Why is achieving full distribution transparency often impractical or even undesirable?
    RETRIEVED TEXT:
    The conclusion is that aiming for distribution transparency may be a nice goal
    when designing and implementing distributed systems, but that it should be
    considered together with other issues such as performance and comprehensibility.
    The price for achieving full transparency may be surprisingly high.
    RELEVANCE:
    {"score": "yes"}
    <end_assessment_3>
    
    <start_assessment_4>
    QUERY:
    Why is achieving full distribution transparency often impractical or even undesirable?
    RETRIEVED TEXT:
    Finally, there are situations in which it is not at all obvious that hiding
    distribution is a good idea. As distributed systems are expanding to devices
    that people carry around and where the very notion of location and context
    awareness is becoming increasingly important, it may be best to actually expose
    distribution rather than trying to hide it. An obvious example is making use of
    location-based services, which can often be found on mobile phones, such as
    finding a nearest shop or any nearby friends.
    RELEVANCE:
    {"score": "no"}
    <end_assessment_4>
    
    <start_assessment_5>
    QUERY:
    Why is achieving full distribution transparency often impractical or even undesirable?
    RETRIEVED TEXT:
    Several researchers have argued that hiding distribution will lead to only
    further complicating the development of distributed systems, exactly for the
    reason that full distribution transparency can never be achieved. A popular
    technique for achieving access transparency is to extend procedure calls to
    remote servers. However, (<>)Waldo et al. [(<>)1997] already pointed out that
    attempting to hide distribution by such remote procedure calls can lead to
    poorly understood semantics, for the simple reason that a procedure call does
    change when executed over a faulty communication link.
    RELEVANCE:
    {"score": "yes"}
    <end_assessment_5>
    



```python
print(SYS_PROMPT["relevance"])
```

    
        You are a grader assessing relevance of a retrieved document to a user question. If the document contains keywords related to the user question, grade it as relevant. It does not need to be a stringent test. The goal is to filter out erroneous retrievals.
        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.
        Provide the binary score as a JSON with a single key 'score' and no premable or explaination.
        

