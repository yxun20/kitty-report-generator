#!/usr/bin/env python3
import os
import sys
import json
import pandas as pd
from openai import OpenAI

# ─── Configuration ────────────────────────────────────────────────────────────
MODEL_NAME        = "gpt-4o-mini"
DEFAULT_CSV_PATH  = "replace_dataset_output.csv"
DEFAULT_OUT_PATH  = "harmful_output.json"

def get_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("Error: OPENAI_API_KEY가 설정되어 있지 않습니다.", file=sys.stderr)
        sys.exit(1)
    return key

# OpenAI client
client = OpenAI(api_key=get_api_key())

PROMPT_TEMPLATE = """\
다음 문장에서 유해한 단어 '{bad_word}'에 대해 아래 JSON 형식으로 응답하세요:
1. reason: 왜 이 단어가 유해한지 어린아이도 알 수 있게 설명하고 , 유래가 있줘면 이 단어의 유래도 설명해줘.
2. quiz: 교육용 객관식 퀴즈 문항으로 앞뒤에 번호 를 붙여서 정답을 번호로 나오게 두문제 정도 부탁해. 

문장: "{sentence}"
"""

class HarmfulContentPipeline:
    def __init__(self, csv_path: str, out_path: str):
        self.csv_path    = csv_path
        self.output_path = out_path
        self.df = None

    def load_data(self):
        if not os.path.isfile(self.csv_path):
            print(f"Error: 입력 파일 '{self.csv_path}'를 찾을 수 없습니다.", file=sys.stderr)
            sys.exit(1)
        self.df = pd.read_csv(self.csv_path)

        # 필수 컬럼 검사
        for col in ("text", "유해_단어", "AI_유해성"):
            if col not in self.df.columns:
                print(f"Error: CSV에 '{col}' 컬럼이 없습니다.", file=sys.stderr)
                sys.exit(1)

        # AI_유해성 == 1인 것만 남깁니다.
        self.df = self.df[self.df["AI_유해성"] == 1].reset_index(drop=True)
        print(f"[INFO] 유해 문장({len(self.df)}개)만 처리 대상으로 설정했습니다.")

    def generate_for_row(self, sentence: str, bad_word: str) -> dict:
        prompt = PROMPT_TEMPLATE.format(bad_word=bad_word, sentence=sentence)
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        text = resp.choices[0].message.content.strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            print(f"[WARN] JSON 파싱 실패: {text[:100]}...", file=sys.stderr)
            data = {}

        return {
            "bad_word": bad_word,
            "reason":   data.get("reason", ""),
            "quiz":     data.get("quiz", "")
        }

    def process_all(self) -> list[dict]:
        results = []
        total = len(self.df)
        for idx, row in self.df.iterrows():
            try:
                entry = self.generate_for_row(row["text"], row["유해_단어"])
                results.append(entry)
                print(f"[{idx+1}/{total}] 생성 완료: '{row['유해_단어']}'")
            except Exception as e:
                print(f"[{idx+1}/{total}] 오류 발생: {e}", file=sys.stderr)
        return results

    def save_json(self, results: list[dict]):
        with open(self.output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 결과가 '{self.output_path}'에 저장되었습니다.")

def main():
    pipeline = HarmfulContentPipeline(DEFAULT_CSV_PATH, DEFAULT_OUT_PATH)
    pipeline.load_data()
    pipeline.df = pipeline.df.head(5)
    results = pipeline.process_all()
    pipeline.save_json(results)

if __name__ == "__main__":
    main()
