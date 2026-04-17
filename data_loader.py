"""
RetailGenius - Data Loader
Load product data from CSV or BigQuery with caching
"""

import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)
def load_sample_data() -> pd.DataFrame:
    """Load sample product data from CSV"""
    try:
        df = pd.read_csv('sample_data.csv')
        return df
    except FileNotFoundError:
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_bq_data(dataset: str, table: str, project_id: str = None) -> pd.DataFrame:
    """Load data from BigQuery"""
    try:
        from google.cloud import bigquery
        client = bigquery.Client(project=project_id)
        query = f"SELECT * FROM `{project_id}.{dataset}.{table}` LIMIT 1000"
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        st.error(f"BigQuery Error: {str(e)}")
        return load_sample_data()

def test_data_loader():
    df = load_sample_data()
    assert len(df) > 0, "Data should not be empty"
    print("✅ Test passed")

if __name__ == "__main__":
    test_data_loader()
