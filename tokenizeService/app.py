from flask import Flask, request, jsonify
from transformers import AutoTokenizer

app = Flask(__name__)

# Initialize BERT tokenizer
tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')

@app.route('/tokenize', methods=['POST'])
def tokenize_text():
    try:
        # Get input text from request
        input_text = request.json['text']

        # Tokenize input text
        inputs = tokenizer.encode_plus(
            input_text,
            add_special_tokens=True,
            max_length=200,
            pad_to_max_length=True,
            return_attention_mask=True,
            return_token_type_ids=True,
            truncation=True
        )

        # Prepare response
        response = {
            'input_ids': inputs['input_ids'],
            'attention_mask': inputs['attention_mask'],
            'token_type_ids': inputs['token_type_ids']
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/', methods=['GET'])
def welcome():
    return "Welcome to VerityVault Tokenizer!"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
