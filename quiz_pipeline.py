import json
import pandas as pd
from openai import OpenAI
from .config import get_api_key, MODEL_NAME
from .prompt_templates import PROMPT_TEMPLATE

class HarmfulContentPipeline:
    def __init__(self, csv_path: str, out_path: str):
        self.csv_path = csv_path
        self.output_path = out_path
        self.df = None
        self.client = OpenAI(api_key=get_api_key())

    def load_data(self):
        self.df = pd.read_csv(self.csv_path)
        self.df = self.df[self.df["AI_유해성"] == 1].reset_index(drop=True)

    def generate_for_row(self, sentence: str, bad_word: str) -> dict:
        prompt = PROMPT_TEMPLATE.format(bad_word=bad_word, sentence=sentence)
        resp = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        try:
            data = json.loads(resp.choices[0].message.content.strip())
        except json.JSONDecodeError:
            data = {}

        return {
            "bad_word": bad_word,
            "reason": data.get("reason", ""),
            "quiz": data.get("quiz", "")
        }

    def process_all(self):
        return [self.generate_for_row(row["text"], row["유해_단어"]) for _, row in self.df.iterrows()]

    def save_json(self, results):
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

