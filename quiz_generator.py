import json
import pandas as pd
from openai import OpenAI
from quiz_config import get_api_key, MODEL_NAME
from quiz_prompt_templates import PROMPT_TEMPLATE

class QuizGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=get_api_key())

    def generate_quiz_for_entry(self, sentence: str, bad_word: str) -> dict:
        prompt = PROMPT_TEMPLATE.format(bad_word=bad_word, sentence=sentence)
        resp = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        text = resp.choices[0].message.content.strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            print(f"[WARN] JSON 파싱 실패: {text[:100]}...")
            data = {}

        return {
            "bad_word": bad_word,
            "reason": data.get("reason", ""),
            "quiz": data.get("quiz", "")
        }

    def generate_quizzes_from_data(self, user_data: pd.DataFrame) -> list[dict]:
        results = []
        for _, row in user_data.iterrows():
            # Assuming user_data DataFrame has 'original_text' and 'harmful_words' columns
            # You might need to adjust column names based on your chat_db.csv structure
            sentence = row['original_text']
            bad_word = row['harmful_words']
            
            # Handle cases where harmful_words might be a comma-separated string
            if isinstance(bad_word, str) and ',' in bad_word:
                # For simplicity, let's just take the first harmful word for quiz generation
                # Or you could iterate through all of them and generate multiple quizzes
                bad_word = bad_word.split(',')[0].strip()

            if sentence and bad_word:
                results.append(self.generate_quiz_for_entry(sentence, bad_word))
        return results
