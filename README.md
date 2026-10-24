# 🔧 Fix Data Types (Pandas)

Identify incorrect data types in a dataset and convert columns to the appropriate types, with an explanation of every conversion.

## Objective
Understand why correct data types are important for data analysis and machine learning.

## Tools
- Python
- Pandas
- Jupyter Notebook
- Streamlit (for the deployed demo)

## Dataset
A messy Employee dataset (`employees_raw.csv`, 25 rows) generated inside the notebook, where numbers, dates and flags are stored as text:
`employee_id, name, department, age, salary, bonus_pct, join_date, is_active, rating, experience_years`

## Conversions

| Column | From | To | Method | Why |
|---|---|---|---|---|
| `age` | text | Int64 | `pd.to_numeric(errors='coerce')` | Has bad entries like 'unknown'; they become NaN |
| `salary` | text ('52,000') | number | `str.replace(',', '')` + `to_numeric` | Comma text cannot be summed or sorted correctly |
| `bonus_pct` | text ('10%') | number | `str.replace('%', '')` + `to_numeric` | % sign blocks calculations |
| `join_date` | text | datetime | `pd.to_datetime(errors='coerce')` | Enables year/month extraction and time maths |
| `is_active` | Yes/No text | bool | `map({'Yes': True, 'No': False})` | Cleaner, smaller, filter-friendly |
| `rating` | text | float | `pd.to_numeric(errors='coerce')` | 'not rated' blocked numeric reading |
| `department` | text | category | `astype('category')` | Few repeated values, saves memory |
| `experience_years` | float | int | `astype(int)` | Whole numbers need no decimals |

## Why it matters
- Text numbers sort wrongly (`'100,000'` before `'25,000'`) and cannot be averaged.
- Real dates allow year/month extraction and date arithmetic.
- Category and bool types use much less memory (about 11 KB down to about 3 KB in this sample).
- Machine learning models need numeric inputs.

## Project Structure
```
├── Fix_Data_Types.ipynb   # Main notebook
├── employees_raw.csv      # Dataset (optional, the notebook creates it)
├── app.py                 # Streamlit web app
├── requirements.txt       # Dependencies
└── README.md
```

## Run Locally
```bash
git clone https://github.com/<your-username>/pandas-fix-data-types.git
cd pandas-fix-data-types
pip install -r requirements.txt

jupyter notebook Fix_Data_Types.ipynb   # notebook
streamlit run app.py                    # web app
```

## Deploy (Streamlit Community Cloud)
1. Push this repo to GitHub.
2. Go to share.streamlit.io and click **New app**.
3. Select the repo, branch `main`, main file `app.py`.
4. Click **Deploy**.

The app includes its own sample data, and you can also upload any CSV, choose a type for each column and download the corrected file.

## Interview Questions
- **What is a data type?** It tells Pandas what kind of values a column holds (integer, float, text, datetime, bool, category), which decides what operations are possible.
- **Why should numerical data have a numerical type?** So it can be sorted, averaged and used in calculations and models. Numbers stored as text sort alphabetically and cannot be averaged.
- **How can you convert a column to numeric?** `pd.to_numeric(df['col'], errors='coerce')` (invalid entries become NaN) or `df['col'].astype(float)` when all values are clean.

## Author
Swetha, AI & ML Track, Veda Technology
