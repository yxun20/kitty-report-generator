import pandas as pd
import os
import re
from typing import Dict, Optional
from pydantic import BaseModel

# --- Pydantic Models ---
class ProcessedTextRequest(BaseModel):
    user_id: int
    original_text: str
    processed_text: str

class ChatDataEntry(BaseModel):
    id: int
    original_text: str
    processed_text: str
    harmful_words: Optional[str] = None
    replacement_format: Optional[str] = None
    replacement_text: Optional[str] = None
    ai_harmfulness: int = 1 # Assuming 1 if it's processed harmful text

# --- Chat Data Manager ---
CHAT_DB_PATH = "chat_db.csv"

def parse_processed_text(processed_text: str) -> Dict[str, Optional[str]]:
    harmful_words_match = re.search(r'문장 중 유해한 단어들: \[(.*?)]', processed_text)
    replacement_format_match = re.search(r"대체 제안 형식: '(.*?)'", processed_text)
    replacement_text_match = re.search(r"대체 문장: '(.*?)'", processed_text)

    harmful_words = harmful_words_match.group(1) if harmful_words_match else None
    replacement_format = replacement_format_match.group(1) if replacement_format_match else None
    replacement_text = replacement_text_match.group(1) if replacement_text_match else None

    return {
        "harmful_words": harmful_words,
        "replacement_format": replacement_format,
        "replacement_text": replacement_text
    }

def append_chat_data(data: ProcessedTextRequest):
    parsed_data = parse_processed_text(data.processed_text)
    new_entry = ChatDataEntry(
        id=data.user_id,
        original_text=data.original_text,
        processed_text=data.processed_text,
        harmful_words=parsed_data["harmful_words"],
        replacement_format=parsed_data["replacement_format"],
        replacement_text=parsed_data["replacement_text"],
        ai_harmfulness=1
    )

    df = pd.DataFrame([new_entry.dict()])

    if not os.path.exists(CHAT_DB_PATH):
        df.to_csv(CHAT_DB_PATH, index=False)
    else:
        df.to_csv(CHAT_DB_PATH, mode='a', header=False, index=False)

def get_user_harmful_chat_count(user_id: int) -> int:
    if not os.path.exists(CHAT_DB_PATH):
        return 0
    df = pd.read_csv(CHAT_DB_PATH)
    return len(df[(df['id'] == user_id) & (df['ai_harmfulness'] == 1)])

def get_user_harmful_chat_data(user_id: int) -> pd.DataFrame:
    if not os.path.exists(CHAT_DB_PATH):
        return pd.DataFrame()
    df = pd.read_csv(CHAT_DB_PATH)
    return df[(df['id'] == user_id) & (df['ai_harmfulness'] == 1)]
