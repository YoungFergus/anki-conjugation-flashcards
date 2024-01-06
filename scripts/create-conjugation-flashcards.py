from openai import OpenAI
import os
import json
import pandas as pd
from sys import exit

class Flashcard():
    def __init__(self):
        self.infinitive = None
        self.mood = None
        self.tense = None
        self.person = None
        self.conj = None
        self.ex = None
        self.ex_eng = None

    def export(self,df):
        for key, value in vars(self).items():
            if value is None:
                setattr(self, key, "")
        df.loc[df.index.max() + 1] = [self.infinitive,
                                      self.mood,
                                      self.tense,
                                      self.person,
                                      self.conj,
                                      self.ex,
                                      self.ex_eng]
        

verb = input("Type in the verb we need to conjugate: ")

#Begin check if verb exists
df = pd.read_csv('conjugations-db.csv',header=0)
if verb in df['Infinitive'].values:
    print('Verb has already been added to flashcard csv')
    exit()

#Initialize call to ChatGPT
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_SECRET"),
)

with open('conjugation-schema.json','r') as f:
    json_format = f.read()

question = f'Can you give me the conjugations of the Spanish verb "{verb}" in the form of a JSON object formatted as such where "conj" is replaced by the conjugated form of the verb for the correct mood, tense, and person:'

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

# Initialize new flashcards

flashcard = Flashcard()
flashcard.infinitive = resp["infinitive"]

# Create the participle flashcards
for key in ["Gerund", "Past_Participle"]:
    if key in resp:
        flashcard.mood = "Participle"
        flashcard.tense = key
        flashcard.ex = '' #placeholder for future improvement
        flashcard.ex_eng = '' # ditto above
        flashcard.export(df=df)
    else:
        print(f"Key: {key} not found in the dictionary.")
        # should be an exception (SchemaException)

# Create the mood flashcards
for key in ["Indicative", "Subjunctive","Imperative"]:
    if key in resp:
        flashcard.mood = key
        for tense in list(resp[key].keys()):
            flashcard.tense = tense
            for prs in list(resp[key][tense].keys()):
                flashcard.person = prs
                flashcard.conj = resp[key][tense][prs]
                flashcard.ex = ''
                flashcard.ex_eng = ''
                flashcard.export(df=df)

df.to_csv('conjugations-db.csv')