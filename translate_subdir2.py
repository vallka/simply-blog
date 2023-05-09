import deepl
import re
import os

auth_key = os.environ.get('DEEPL_KEY')  # Replace with your key
translator = deepl.Translator(auth_key)

input_path = "en/contact.html"
output_path = "es/contact.html"

lang = "it"


#text = '<p>this is my {shop_name} and i like it</p><img alt= "{shop_name}">'

pattern = r"(?<!('|\"))({[a-zA-Z_]*?})"

def replace(match):
    return '<span class="notranslate">{' + str(match.group(2)) + '}</span>'



# Iterate through all .html and .txt files in the 'en' subdirectory
for root, dirs, files in os.walk('en'):
    for file in files:
        if file.endswith('.html'):
            # Read the file contents
            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                print(file)
                text = f.read()
                new_text = re.sub(pattern, replace, text)

                result = translator.translate_text(new_text, target_lang=lang,formality="more",preserve_formatting=True,tag_handling="html")
                result

                final_text = result.text.replace('<span class="notranslate">{','').replace('}</span>','')

                target_dir = os.path.join(root.replace('en', lang), os.path.dirname(file))
                os.makedirs(target_dir, exist_ok=True)

                # Write the translated text to the target file
                with open(os.path.join(target_dir, file), 'w', encoding='utf-8') as f:
                    f.write(final_text)



