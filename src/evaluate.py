# src/evaluate.py

import pandas as pd


def normalize(value) -> str:
    """Clean a value for fair comparison: lowercase, strip spaces, normalize floats like 4000.0 -> 4000.""" 
    if pd.isna(value):
        return ""
    val_str = str(value).strip().lower()
    if val_str.endswith(".0"):
        val_str = val_str[:-2]
    return val_str
    

def calculate_recall(predictions_csv: str, ground_truth_csv: str):
    """
    predictions_csv  -> path to your output file (e.g. predictions/train_predictions.csv)
    ground_truth_csv -> path to the answer key (e.g. data/train.csv)
    Prints per-field Recall score.
    """

    pred_df = pd.read_csv(predictions_csv)
    truth_df = pd.read_csv(ground_truth_csv)

    # In the Train.csv file column name of Agreement is Aggrement so we rename it to Agreement to match
    truth_df.columns = truth_df.columns.str.replace("Aggrement", "Agreement")

    #Match rows by files Name
    merged = pd.merge(pred_df, truth_df, on="File Name", suffixes=("_pred","_true"))

    fields = [
        "Agreement Value",
        "Agreement Start Date",
        "Agreement End Date",
        "Renewal Notice (Days)",
        "Party One",
        "Party Two"
    ]

    print("\n" + "="*50)
    print(" PER-FIELD RECALL SCORES")
    print("="*50)

    total_recall = 0
    for field in fields:
        pred_col = field + "_pred"
        truth_col = field + "_true"


        # Count exact matches (after normalization)
        true_count = sum(
            normalize(merged[pred_col][i]) ==normalize(merged[truth_col][i])
        for i in range(len(merged))
        )
        total_count = len(merged)
        recall = true_count / total_count if total_count > 0 else 0
        total_recall += recall

        print(f"{field:<30} -> {true_count}/{total_count} = {recall:.2f}")
        

    avg = total_recall / len(fields)

    print("-"*50)
    print(f"AVERAGE RECALL: {avg:.2f}")
    print("-"*50 + "\n")
            