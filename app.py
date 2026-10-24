import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Fix Data Types", page_icon="🔧", layout="wide")
st.title("🔧 Identify and Fix Data Types with Pandas")
st.caption("Upload a CSV (or use the built-in messy Employee sample), inspect the data types, choose the right type for each column and download the corrected data.")


@st.cache_data
def make_sample():
    rng = np.random.default_rng(22)
    n = 25
    names = ['Aarav', 'Diya', 'Rohan', 'Sneha', 'Karthik', 'Priya', 'Vikram', 'Ananya', 'Arjun', 'Meera',
             'Rahul', 'Kavya', 'Nikhil', 'Isha', 'Suresh', 'Lakshmi', 'Manoj', 'Divya', 'Harsh', 'Pooja',
             'Varun', 'Neha', 'Gautam', 'Swati', 'Ajay']
    age = [str(a) for a in rng.integers(22, 58, n)]
    age[3], age[11] = 'unknown', 'not given'
    salary = [f'{s:,}' for s in rng.integers(25000, 120000, n)]
    bonus = [f'{b}%' for b in rng.integers(5, 20, n)]
    dates = (pd.Timestamp('2018-01-01') + pd.to_timedelta(rng.integers(0, 2500, n), 'D')).strftime('%Y-%m-%d').tolist()
    dates[7] = 'Unknown'
    rating = [str(r) for r in rng.choice([3.0, 3.5, 4.0, 4.5, 5.0], n)]
    rating[5] = 'not rated'
    raw = pd.DataFrame({
        'employee_id': np.arange(101, 101 + n), 'name': names,
        'department': rng.choice(['HR', 'IT', 'Finance', 'Sales', 'Marketing'], n),
        'age': age, 'salary': salary, 'bonus_pct': bonus, 'join_date': dates,
        'is_active': rng.choice(['Yes', 'No'], n, p=[0.8, 0.2]), 'rating': rating,
        'experience_years': rng.integers(1, 15, n).astype(float)})
    return raw


def clean_text(s):
    """Remove commas, %, currency symbols and spaces so text numbers can be converted."""
    return s.astype(str).str.replace(r"[,%$₹£€\s]", "", regex=True)


def convert(series, target):
    if target == "Keep as is":
        return series
    if target == "Integer (Int64)":
        return pd.to_numeric(clean_text(series), errors="coerce").round().astype("Int64")
    if target == "Float (number)":
        return pd.to_numeric(clean_text(series), errors="coerce")
    if target == "Datetime":
        return pd.to_datetime(series, errors="coerce")
    if target == "Category":
        return series.astype("category")
    if target == "Boolean (Yes/No, True/False)":
        m = {"yes": True, "y": True, "true": True, "1": True, "no": False, "n": False, "false": False, "0": False}
        return series.astype(str).str.strip().str.lower().map(m).astype("boolean")
    if target == "Text":
        return series.astype(str)
    return series


uploaded = st.file_uploader("Upload a CSV file", type=["csv"])
try:
    df = pd.read_csv(uploaded) if uploaded is not None else make_sample()
except Exception as e:
    st.error(f"Could not load the dataset: {e}")
    st.stop()

# ---------------- Original types ----------------
st.header("1. Original data types")
st.dataframe(df.head(8), use_container_width=True)
orig = df.dtypes.astype(str).rename("original type")
st.dataframe(orig, use_container_width=True)

# ---------------- Choose types ----------------
st.header("2. Choose the correct type for each column")
OPTIONS = ["Keep as is", "Integer (Int64)", "Float (number)", "Datetime", "Category", "Boolean (Yes/No, True/False)", "Text"]


def suggest(col):
    s = df[col]
    if pd.api.types.is_numeric_dtype(s):
        return "Keep as is"
    name = col.lower()
    if "date" in name or "time" in name:
        return "Datetime"
    sample = clean_text(s.dropna().head(50))
    if len(sample) and pd.to_numeric(sample, errors="coerce").notna().mean() > 0.7:
        return "Float (number)"
    if s.nunique() <= 2 or s.astype(str).str.lower().isin(["yes", "no", "true", "false"]).mean() > 0.9:
        return "Boolean (Yes/No, True/False)"
    if s.nunique() <= 10:
        return "Category"
    return "Keep as is"


fixed = df.copy()
cols = st.columns(3)
for i, c in enumerate(df.columns):
    choice = cols[i % 3].selectbox(f"{c}  ({orig[c]})", OPTIONS, index=OPTIONS.index(suggest(c)), key=f"t_{c}")
    fixed[c] = convert(df[c], choice)

# ---------------- Result ----------------
st.header("3. Corrected data types")
comp = pd.DataFrame({"original": orig, "corrected": fixed.dtypes.astype(str)})
comp["changed"] = comp["original"] != comp["corrected"]
st.dataframe(comp, use_container_width=True)

m1, m2, m3 = st.columns(3)
m1.metric("Columns changed", int(comp["changed"].sum()))
m2.metric("New missing values from bad entries", int(fixed.isnull().sum().sum() - df.isnull().sum().sum()))
m3.metric("Memory", f"{fixed.memory_usage(deep=True).sum():,} B", f"{fixed.memory_usage(deep=True).sum() - df.memory_usage(deep=True).sum():,} B")

st.dataframe(fixed.head(15), use_container_width=True)
st.download_button("⬇️ Download corrected CSV", fixed.to_csv(index=False).encode("utf-8"),
                   file_name="corrected_data.csv", mime="text/csv")

with st.expander("Why data types matter"):
    st.markdown("""
- Numbers stored as **text** sort wrongly (`'100,000'` comes before `'25,000'`) and cannot be averaged.
- **Datetime** columns allow year/month extraction and date calculations.
- **Category** saves memory for columns with few repeated values.
- **Bool** is smaller and works directly in filters.
- Machine learning models need **numeric** inputs, so text numbers must be converted first.
- `errors='coerce'` turns invalid entries into missing values instead of crashing.
""")
