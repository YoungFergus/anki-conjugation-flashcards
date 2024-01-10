from openai import OpenAI
import os
import json
import pandas as pd
from sys import exit
from pathlib import Path
from dotenv import load_dotenv

class Base_Flashcard():
    def __init__(self) -> None:
        pass

    def export(self, df):
        for key, value in vars(self).items():
            if value is None:
                setattr(self, key, "")

        all_attributes = dir(self)
        property_names = [attr for attr in all_attributes if not attr.startswith('__')]

        df.loc[df.index.max() + 1] = [self.prop for prop in property_names]

class Vocab_Flashcard(Base_Flashcard):
    def __init__(self) -> None:
        super().__init__()
        self.word = None
        self.translation = None
        self.ex = None
        self.ex_eng = None

word = input("Type in the verb we need to conjugate: ")

df = pd.read_csv(Path('outputs/spanish-vocab-db.csv'),header=0)
if verb in df['Spanish'].values:
    print('Verb has already been added to flashcard deck')
    exit()

load_dotenv()

#Initialize call to ChatGPT
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_SECRET"),
)

with open('templates/vocab-schema.json','r') as f:
    json_format = f.read()

question = f'Please give me the translation for the Spanish word "tiroteo", its part of speech, gender if a noun, and an example sentence with its English translation in json form: '
prompt = question + '\n' + json_format

response = client.chat.completions.create(
  response_format={"type": "json_object"},
  model="gpt-3.5-turbo-1106",
  messages=[
    {"role": "user", "content": prompt}
  ]
)

content = response.choices[0].message.content
content = content.replace('\n','')

resp = json.loads(content)

flashcard = Vocab_Flashcard()

if resp["pos"][0] == "noun":
    flashcard.word = resp["Spanish_Word"] + " " + resp["pos"][0] + resp["pos"][1][0]
else:
    flashcard.word = resp["Spanish_Word"] + " " + resp["pos"][0]

flashcard.translation = resp["Translation"]
flashcard.ex = resp["Example"]
flashcard.ex_eng = resp["Example_Translation"]
"""
{
  "Spanish_Word": "tiroteo",
  "Translation": "shooting (incident)",
  "pos": ["noun", "masculine"],
  "Example": "El tiroteo ocurrió en el centro de la ciudad.",
  "Example_Translation": "The shooting incident occurred in the city center."
}
"""

df.to_csv(Path('outputs/spanish-vocab-db.csv'), index=False)