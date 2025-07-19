import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o-mini"

def make_prompt(uid: int, stat: dict) -> str:
    lines = [
        f"사용자 {uid} 유해성 요약을 작성해주세요.\n",
        f"1) 평균값이 가장 높은 유해도 카테고리: {stat['highest_avg_category']['category']} ({stat['highest_avg_category']['average']:.3f})",
        "\n2) 사이트별 유해성 합(sum)이 가장 높은 사이트 5개:",
    ]
    for i, info in enumerate(stat["top5_sites_by_sum"], 1):
        lines.append(f"   {i}. {info['site']} (합계: {info['sum']:.3f})")
    lines.append("\n3) 카테고리별 평균 유해도:")
    for cat, val in stat["category_means"].items():
        lines.append(f"   - {cat}: {val:.3f}")
    lines.append("\n위 정보를 바탕으로 사용자의 웹 사용 유해성 분석 보고서를 작성해주세요.")
    return "\n".join(lines)

def generate_user_report(uid: int, stat: dict) -> str:
    prompt = make_prompt(uid, stat)
    response = openai.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=512
    )
    return response.choices[0].message.content.strip()

