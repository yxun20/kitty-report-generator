#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
report_generator_site.py

- site_db.csv 로부터 사용자·사이트별 평균 유해도 계산 → site_harmfulness_by_id.csv 저장
- 사용자별로
    1) 6개 유해도 항목 중 평균값이 가장 높은 카테고리
    2) 사이트별 유해성 합(sum_harm)이 가장 높은 사이트 5개
    3) 카테고리별 평균값
    4) GPT-4o Mini 프롬프트 엔지니어링을 통해 유해성 리포트 작성
  결과를 site_report.json 으로 저장
  * 테스트용: 처음 두 사용자만 처리
"""

import os
import sys
import json
import pandas as pd
import openai

# ─── 설정 ──────────────────────────────────────────────────────────────────────

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("Error: 환경변수 OPENAI_API_KEY가 설정되어 있지 않습니다.", file=sys.stderr)
    sys.exit(1)
openai.api_key = API_KEY

MODEL_NAME       = "gpt-4o-mini"
RAW_CSV_PATH     = "site_db.csv"
AGG_CSV_PATH     = "site_harmfulness_by_id.csv"
OUTPUT_JSON_PATH = "site_report.json"

HARM_COLUMNS = [
    "abuse", "censure", "discrimination",
    "hate", "sexual", "violence"
]


# ─── 데이터 집계 ──────────────────────────────────────────────────────────────

def load_and_aggregate() -> pd.DataFrame:
    """site_db.csv → id·site별 평균 유해도 계산 → 저장 → DataFrame 반환"""
    if not os.path.isfile(RAW_CSV_PATH):
        print(f"Error: '{RAW_CSV_PATH}' 파일을 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(RAW_CSV_PATH)
    for col in ["id", "site"] + HARM_COLUMNS:
        if col not in df.columns:
            print(f"Error: '{col}' 컬럼이 없습니다.", file=sys.stderr)
            sys.exit(1)

    agg = df.groupby(["id", "site"], as_index=False)[HARM_COLUMNS].mean()
    agg.to_csv(AGG_CSV_PATH, index=False, encoding="utf-8")
    print(f"[INFO] 평균 유해도 결과를 '{AGG_CSV_PATH}'에 저장했습니다.")
    return agg


# ─── 사용자별 통계 계산 ────────────────────────────────────────────────────────

def build_user_stats(agg_df: pd.DataFrame) -> dict[int, dict]:
    """
    사용자별로 다음 통계를 계산하여 dict로 반환:
      1) highest_avg_category: 카테고리별 평균이 가장 높은 항목
      2) top5_sites_by_sum: 사이트별 유해성 합(sum_harm)이 가장 높은 사이트 5개
      3) category_means: 6개 카테고리별 평균값
    """
    stats = {}

    for uid, sub in agg_df.groupby("id"):
        uid = int(uid)

        # 1) 카테고리별 평균 across 모든 방문 사이트
        cat_means = sub[HARM_COLUMNS].mean()
        highest_avg_cat = cat_means.idxmax()
        highest_avg_val = float(cat_means.max())

        # 2) 사이트별 유해성 합(sum_harm) 계산 → Top 5 추출
        tmp = sub.copy()
        tmp["sum_harm"] = tmp[HARM_COLUMNS].sum(axis=1)
        top5 = tmp.nlargest(5, "sum_harm")[["site", "sum_harm"]]
        top5_list = [
            {"site": row["site"], "sum": float(row["sum_harm"])}
            for _, row in top5.iterrows()
        ]

        # 3) 카테고리별 평균값 딕셔너리
        means_dict = {cat: float(cat_means[cat]) for cat in HARM_COLUMNS}

        stats[uid] = {
            "highest_avg_category": {
                "category": highest_avg_cat,
                "average": highest_avg_val
            },
            "top5_sites_by_sum": top5_list,
            "category_means": means_dict
        }

    return stats


# ─── 프롬프트 생성 & GPT 호출 ─────────────────────────────────────────────────

def make_prompt(uid: int, stat: dict) -> str:
    parts = [
        f"사용자 {uid} 유해성 요약을 작성해주세요.",
        "",
        f"1) 평균값이 가장 높은 유해도 카테고리: "
        f"{stat['highest_avg_category']['category']} "
        f"({stat['highest_avg_category']['average']:.3f})",
        "",
        "2) 사이트별 유해성 합(sum)이 가장 높은 사이트 5개:",
    ]
    for i, info in enumerate(stat["top5_sites_by_sum"], 1):
        parts.append(f"   {i}. {info['site']} (합계: {info['sum']:.3f})")
    parts.extend([
        "",
        "3) 카테고리별 평균 유해도:",
    ])
    for cat, val in stat["category_means"].items():
        parts.append(f"   - {cat}: {val:.3f}")
    parts.append("")
    parts.append(
        "위 정보를 바탕으로, 사용자가 방문한 사이트들이 어떤 위험을 내포하는지 간결하게 요약하고, 권장 대응 방안, 교육 및 인식 증진, 사이트 방문 주의, 정기적인 모니터링 등을 적어서 작성해주세요."
    )
    return "\n".join(parts)

def generate_user_report(uid: int, stat: dict) -> str:
    prompt = make_prompt(uid, stat)
    # OpenAI v1.x 호출 방식
    resp = openai.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=512
    )
    return resp.choices[0].message.content.strip()


# ─── 메인 ─────────────────────────────────────────────────────────────────────

def main():
    # 1) 집계
    agg_df = load_and_aggregate()

    # 2) 사용자별 통계
    stats = build_user_stats(agg_df)

    # 3) 테스트용: 처음 두 사용자만 처리
    sample_ids = list(stats.keys())[:2]

    output = []
    for uid in sample_ids:
        print(f"[INFO] 사용자 {uid} 보고서 생성 중...")
        entry = {"user_id": uid, **stats[uid]}
        entry["report"] = generate_user_report(uid, stats[uid])
        output.append(entry)

    # 4) JSON 저장
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"[INFO] 최종 리포트를 '{OUTPUT_JSON_PATH}'에 저장했습니다.")


if __name__ == "__main__":
    main()
