import json
from openai import OpenAI
from quiz_config import get_api_key, MODEL_NAME

PROMPT_TEMPLATE = """
다음은 사용자의 유해 콘텐츠 접촉 통계입니다. 이 데이터를 바탕으로 사용자가 이해하기 쉬운 요약 리포트를 생성해주세요.
리포트는 다음 JSON 형식으로 응답해야 합니다:
1. summary: 사용자의 전반적인 유해 콘텐츠 접촉 경향에 대한 요약.
2. advice: 유해 콘텐츠에 대한 노출을 줄이거나 건강한 디지털 습관을 위한 조언.

통계 데이터:
{statistics}
"""

class ReportGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=get_api_key())

    def generate_report(self, stats_data: dict) -> dict:
        prompt = PROMPT_TEMPLATE.format(statistics=json.dumps(stats_data, indent=2, ensure_ascii=False))
        resp = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000
        )
        text = resp.choices[0].message.content.strip()
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            print(f"[WARN] JSON 파싱 실패: {text[:100]}...")
            data = {}
        return data
