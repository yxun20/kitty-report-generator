# generator.py

import os
import sys
import json
import pandas as pd
import openai

HARMFUL_WORDS_COL = "harmful_words"

def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    expected = [
        "text", "intensity", "id",
        "abuse", "censure", "discrimination",
        "hate", "sexual", "violence",
        "prior_harmfulness", "ai_harmfulness",
        HARMFUL_WORDS_COL,
        "replacement_format", "replacement_text",
        "spend_receive"
    ]
    missing = [c for c in expected if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    return df


def top_n_harmful_words(df: pd.DataFrame, n: int = 3) -> list[dict]:
    all_words = (
        df[HARMFUL_WORDS_COL]
        .fillna("")
        .astype(str)
        .str.split(",")
        .explode()
        .str.strip()
    )
    all_words = all_words[all_words != ""]
    counts = all_words.value_counts().head(n)
    return [{"word": w, "count": int(c)} for w, c in counts.items()]


def spend_receive_stats(df: pd.DataFrame) -> dict:
    stats = {}
    for val, label in [(1, "spend"), (0, "receive")]:
        grp = df[df["spend_receive"] == val]
        total = len(grp)
        harmful = grp[grp[HARMFUL_WORDS_COL].fillna("").astype(str).str.strip() != ""].shape[0]
        clean = total - harmful
        stats[label] = {
            "total_messages": total,
            "harmful_messages": harmful,
            "clean_messages": clean,
            "harmful_pct": round(harmful / total * 100, 1) if total else 0.0,
            "clean_pct": round(clean / total * 100, 1) if total else 0.0
        }
    return stats


def make_prompt(user_id: int, top3: list, sr_stats: dict) -> str:
    lines = [
        f"## 사용자 {user_id} 채팅 유해성 요약 보고서",
        "",
        "### 1) 자주 쓴 유해 단어 Top 3"
    ]
    for i, entry in enumerate(top3, 1):
        lines.append(f"{i}. `{entry['word']}` — {entry['count']}회")
    lines.extend([
        "",
        "### 2) 메시지별 유해 vs 클린 비율",
        f"- 보냄(spend): 총 {sr_stats['spend']['total_messages']}건",
        f"  - 유해 {sr_stats['spend']['harmful_messages']}건 ({sr_stats['spend']['harmful_pct']}%)",
        f"  - 클린 {sr_stats['spend']['clean_messages']}건 ({sr_stats['spend']['clean_pct']}%)",
        "",
        f"- 받음(receive): 총 {sr_stats['receive']['total_messages']}건",
        f"  - 유해 {sr_stats['receive']['harmful_messages']}건 ({sr_stats['receive']['harmful_pct']}%)",
        f"  - 클린 {sr_stats['receive']['clean_messages']}건 ({sr_stats['receive']['clean_pct']}%)",
        "",
        "위 통계를 바탕으로, 해당 사용자의 채팅 경향을 요약하고, "
        "유해 콘텐츠 대응 방안을 Markdown 형식으로 작성해주세요."
    ])
    return "\n".join(lines)


def generate_report_with_gpt(prompt: str, model="gpt-4o-mini") -> str:
    resp = openai.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500
    )
    return resp.choices[0].message.content.strip()


def generate_chat_report(input_path: str, output_path: str):
    df = load_data(input_path)
    output = []

    for user_id, user_df in df.groupby("id"):
        print(f"[INFO] 사용자 {user_id} 처리 중...")
        top3 = top_n_harmful_words(user_df)
        sr_stats = spend_receive_stats(user_df)
        bad_msgs = user_df[user_df[HARMFUL_WORDS_COL].fillna("").astype(str).str.strip() != ""]
        records = [
            {"text": row["text"], "harmful_words": [w.strip() for w in str(row[HARMFUL_WORDS_COL]).split(",") if w.strip()]}
            for _, row in bad_msgs.iterrows()
        ]
        prompt = make_prompt(user_id, top3, sr_stats)
        report_md = generate_report_with_gpt(prompt)

        output.append({
            "user_id": user_id,
            "top3_harmful_words": top3,
            "spend_receive_stats": sr_stats,
            "records": records,
            "gpt_report": report_md
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"[INFO] 리포트를 '{output_path}'에 저장했습니다.")

