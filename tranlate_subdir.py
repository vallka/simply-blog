import os
import requests

url = 'https://blog2.gellifique.co.uk/api/v1/translate/'

#data = {
#    'q': '',
#    'source': 'en',
#    'target': ['es', 'fr', 'de', 'ro', 'it', 'pl', 'uk']
#}

data = {
    'q': '',
    'source': 'en',
    'target': ['es']
}

# Iterate through all .html and .txt files in the 'en' subdirectory
for root, dirs, files in os.walk('en'):
    for file in files:
        if file.endswith('.html') or file.endswith('.txt'):
            # Read the file contents
            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                text = f.read()

            # Translate the text using the API
            data['q'] = text
            res = requests.post(url, json=data)

            # Create the target subdirectories if they don't exist
            for lang in data['target']:
                target_dir = os.path.join(root.replace('en', lang), os.path.dirname(file))
                os.makedirs(target_dir, exist_ok=True)

                # Write the translated text to the target file
                with open(os.path.join(target_dir, file), 'w', encoding='utf-8') as f:
                    translated_text = res.json()['translated_texts'][lang][0]
                    f.write(translated_text)
