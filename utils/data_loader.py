import pandas as pd
import streamlit as st

@st.cache_data(show_spinner="Loading workforce dataset...")
def load_default_data(file_path: str) -> pd.DataFrame:
    """
    Loads the default CSV file from the local workspace.
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        st.error(f"Default dataset not found at: {file_path}")
        return None
    except Exception as e:
        st.error(f"Failed to load default dataset: {str(e)}")
        return None

def load_uploaded_data(uploaded_file) -> pd.DataFrame:
    """
    Loads and parses a CSV uploaded via the file_uploader component.
    """
    try:
        # Reset pointer if it's a file buffer
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file)
        return df
    except Exception as e:
        st.error(f"Failed to parse uploaded CSV: {str(e)}")
        return None
