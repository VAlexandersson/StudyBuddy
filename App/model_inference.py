
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
    
    response = outputs[0][input_ids.shape[-1]:]
    return tokenizer.decode(response)
