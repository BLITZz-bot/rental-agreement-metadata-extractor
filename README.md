# Rental Agreement Metadata Extractor

## Problem Statement
AI/ML system to extract key metadata from rental agreement documents (`.docx` and `.png`) without using rule-based (RegEx) approaches.

## Fields Extracted
1. **Agreement Value** — Monthly rent amount (number only)
2. **Agreement Start Date** — Effective start date (`DD.MM.YYYY`)
3. **Agreement End Date** — Effective end date (`DD.MM.YYYY`)
4. **Renewal Notice (Days)** — Required notice period in days (number only)
5. **Party One** — Landlord / Lessor name
6. **Party Two** — Tenant / Lessee name

---

## Approach
* **Multi-Modal LLM (Google Gemini):** Used Gemini Flash for zero-shot structured information extraction.
* **Document Processing:**
  * `.docx`: Parsed paragraphs and table cells using `python-docx`.
  * `.png`: Read via `Pillow` and passed directly to Gemini Vision for visual understanding without external OCR tools.
* **Prompt Engineering & Calendar Arithmetic:**
  * Enforced strict JSON schema outputs.
  * Added calendar arithmetic logic to calculate end dates from durations (e.g., *11 months from start date*) while respecting leap years and month lengths without hallucinating invalid dates.
  * Stripped honorific titles (Mr., Mrs., Shri, etc.) to capture clean entity names.
* **Robust File Handling:** Automatically strips single or chained extensions (such as `.pdf.docx`) to match ground truth document identifiers.

---

## Project Structure
```
Assignment-1/
|-- data/train/          → training documents
|-- data/test/           → test documents
|-- src/
|   |-- document_loader.py
|   |-- extractor.py
|   |-- evaluate.py
|-- predictions/         → output CSVs saved here
|-- main.py
|-- api.py
|-- requirements.txt
```
create an empty folder called predictions in root of the project here the output will be produced.

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Add your Gemini API key
create an .env file in the root directory and add your Gemini API key in format given in .env

# .env
GOOGLE_API_KEY="YOUR_GEMINI_API_KEY_HERE"
once added the API KEY please check the available model for your API KEY and change according to your supported model in src/extractor.py 

### 3. Run extraction on train set (to verify)
```bash
python main.py
```

### 4. Run on test set
Add test files to `data/test/` (please change name of the file according to your file names in main.py if needed)

## Predictions
Test predictions saved to: `predictions/test_predictions.csv`

## Recall Scores (Test Set)
| Field                        | Recall |
|------------------------------|--------|
| Agreement Value              | 1.00   |
| Agreement Start Date         | 1.00   |
| Agreement End Date           | 0.75   |
| Renewal Notice (Days)        | 0.75   |
| Party One                    | 1.00   |
| Party Two                    | 0.50   |
| **Average Recall**           | **0.83** |



## API Usage ** 
```bash
uvicorn api:app --reload
# POST file to http://127.0.0.1:8000/extract
```


---

### How to Run the Pipeline (`main.py`)

Open `main.py` to configure what you want to process:

#### Configuration (at top of `main.py`):
```python
# Please change name of the file and csv if needed
TRAIN_FOLDER = "data/train"       # Path to training documents (.docx, .png)
TRAIN_CSV    = "data/train.csv"   # Ground truth CSV (optional, for scoring)

TEST_FOLDER  = "data/test"        # Path to test documents (.docx, .png)
TEST_CSV     = "data/test.csv"    # Ground truth CSV (optional, for scoring)
```

**Note on Evaluation (`calculate_recall`):**
* If you have a ground truth CSV (`train.csv` or `test.csv`): The pipeline will extract metadata AND automatically calculate recall scores.
* If you DO NOT have a ground truth CSV (e.g. evaluating unseen documents): Simply comment out `calculate_recall(...)` in `main.py`. The extraction will still run completely fine and save all results to `predictions/test_predictions.csv`.
