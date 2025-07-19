import os
import sys

def get_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("Error: OPENAI_API_KEY가 설정되어 있지 않습니다.", file=sys.stderr)
        sys.exit(1)
    return key

MODEL_NAME = "gpt-4o-mini"

