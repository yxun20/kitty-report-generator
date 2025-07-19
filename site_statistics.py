import pandas as pd

HARM_COLUMNS = ["abuse", "censure", "discrimination", "hate", "sexual", "violence"]

def build_user_stats(agg_df: pd.DataFrame) -> dict[int, dict]:
    stats = {}
    for uid, sub in agg_df.groupby("id"):
        uid = int(uid)
        cat_means = sub[HARM_COLUMNS].mean()
        highest_avg_cat = cat_means.idxmax()
        highest_avg_val = float(cat_means.max())

        tmp = sub.copy()
        tmp["sum_harm"] = tmp[HARM_COLUMNS].sum(axis=1)
        top5 = tmp.nlargest(5, "sum_harm")[["site", "sum_harm"]]
        top5_list = [{"site": row["site"], "sum": float(row["sum_harm"])} for _, row in top5.iterrows()]
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

