import os
import pandas as pd
from src.document_loader import load_document
from src.extractor import extract_fields
from src.evaluate import calculate_recall


# CONFIGURATION — change paths here

TRAIN_FOLDER     = "data/train"
TRAIN_CSV        = "data/train.csv"

TEST_FOLDER      = "data/test"       
TEST_CSV         = "data/test.csv"   

TRAIN_OUTPUT     = "predictions/train_predictions.csv"
TEST_OUTPUT      = "predictions/test_predictions.csv"


def process_folder(folder_path: str, output_csv: str):
    """
    Loops through all .docx and .png files in folder_path.
    Extracts 6 fields from each file.
    Saves results to output_csv.
    """

    result = []
    supported = (".docx", ".png")

    files = [f for f in os.listdir(folder_path) if f.lower().endswith(supported)]
    print(f"\nProcessing {len(files)} files in '{folder_path}'")

    for filename in files:
        filepath = os.path.join(folder_path, filename)
        #File name column = filename without extension (to match train.csv)
        # Strip all known file extensions from the end (e.g. .pdf.docx, .png.docx)
        known_exts = (".docx", ".doc", ".pdf", ".png", ".jpg", ".jpeg")
        file_name_key = filename
        while any(file_name_key.lower().endswith(ext) for ext in known_exts):
            file_name_key = os.path.splitext(file_name_key)[0]


        print(f"Processing: {filename}...", end=" ")
        try:
            content, content_type = load_document(filepath)
            fields = extract_fields(content, content_type)
            fields["File Name"] = file_name_key
            result.append(fields)
            print(" Done")

        except Exception as e:
            print(f" Error: {e}")
            result.append({
                "File Name": file_name_key,
                "Agreement Value": "",
                "Agreement Start Date": "",
                "Agreement End Date": "",
                "Renewal Notice (Days)": "",
                "Party One": "",
                "Party Two": ""
                })

    # Create DataFrame and reorder columns to match train.csv format
    column_order = [
        "File Name",
        "Agreement Value",
        "Agreement Start Date",
        "Agreement End Date",
        "Renewal Notice (Days)",
        "Party One",
        "Party Two"
    ]

    df = pd.DataFrame(result)[column_order]

    # Ensure prediction folder exists   
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv,index=False)
    print(f"Predictions saved to: {output_csv}")
    return output_csv

# -------------------------
# RUN THE PIPELINE
# -------------------------

if __name__ == "__main__":

    # print("\n STEP 1: Processing TRAIN set...")
    # process_folder(TRAIN_FOLDER, TRAIN_OUTPUT)

    # print("\n STEP 2: Evaluating TRAIN predictions vs ground truth...")
    # calculate_recall(TRAIN_OUTPUT, TRAIN_CSV)

    print("\n STEP 3: Processing TEST set...")
    process_folder(TEST_FOLDER, TEST_OUTPUT)
    
    print("\n STEP 4: Evaluating TEST predictions...")
    calculate_recall(TEST_OUTPUT, TEST_CSV)