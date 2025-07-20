import pandas as pd
from collections import Counter

def generate_chat_statistics(user_data: pd.DataFrame) -> dict:
    stats = {
        "total_harmful_entries": 0,
        "harmful_word_counts": {},
        "top_5_harmful_words": []
    }

    if user_data.empty:
        return stats

    stats["total_harmful_entries"] = len(user_data)

    all_harmful_words = []
    for _, row in user_data.iterrows():
        if row['harmful_words']:
            # Assuming harmful_words can be a comma-separated string
            words = [word.strip() for word in row['harmful_words'].split(',')]
            all_harmful_words.extend(words)

    word_counts = Counter(all_harmful_words)
    stats["harmful_word_counts"] = dict(word_counts)

    # Get top 5 harmful words
    stats["top_5_harmful_words"] = sorted(word_counts.items(), key=lambda item: item[1], reverse=True)[:5]
    stats["top_5_harmful_words"] = [{'word': word, 'count': count} for word, count in stats["top_5_harmful_words"]]

    return stats
