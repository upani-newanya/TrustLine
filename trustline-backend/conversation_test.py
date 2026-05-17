import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Paths to local models
DISTRESS_MODEL_PATH = './ml_models/suicide_model_distilbert_cpu_v2'
EMOTION_MODEL_PATH = './ml_models/emotion_model_distilbert_cpu_4class_best'

def load_model_and_tokenizer(model_path):
    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = AutoModelForSequenceClassification.from_pretrained(model_path, local_files_only=True)
    model.eval()
    return tokenizer, model

def predict(model, tokenizer, text, max_length=256):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=max_length)
    # Remove token_type_ids if present (DistilBERT does not use them)
    if 'token_type_ids' in inputs:
        del inputs['token_type_ids']
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=1)
        conf, idx = torch.max(probs, dim=1)
        label = model.config.id2label[idx.item()]
        return label, conf.item()

def main():
    print('Loading models...')
    distress_tokenizer, distress_model = load_model_and_tokenizer(DISTRESS_MODEL_PATH)
    emotion_tokenizer, emotion_model = load_model_and_tokenizer(EMOTION_MODEL_PATH)
    print('Models loaded. Type your message (type "exit" to quit).')
    while True:
        user_input = input('\nYou: ')
        if user_input.strip().lower() in {'exit', 'quit'}:
            print('Exiting.')
            break
        distress_label, distress_conf = predict(distress_model, distress_tokenizer, user_input, max_length=256)
        emotion_label, emotion_conf = predict(emotion_model, emotion_tokenizer, user_input, max_length=128)
        print(f'Distress: {distress_label} (confidence: {distress_conf:.4f})')
        print(f'Emotion: {emotion_label} (confidence: {emotion_conf:.4f})')

if __name__ == '__main__':
    main()
