from transformers import AutoTokenizer, AutoModelForSequenceClassification

def grade_response(query, response):
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
    model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased")

    input_text = f"Query: {query}\nResponse: {response}"
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    output = model(input_ids)
    predicted_class = output.logits.argmax().item()

    if predicted_class == 1:
        return "A"
    else:
        return "B"