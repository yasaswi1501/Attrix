import pandas as pd

def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    """
    Converts a pandas DataFrame to CSV bytes ready for Streamlit's download button.
    """
    if df is None or df.empty:
        return b""
    return df.to_csv(index=False).encode('utf-8')

def convert_text_to_bytes(text: str) -> bytes:
    """
    Converts string report content (like markdown or txt summaries) to bytes for download.
    """
    if not text:
        return b""
    return text.encode('utf-8')
