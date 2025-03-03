import pandas as pd
import io
import base64
import streamlit as st

def create_sample_excel():
    """Create a sample Excel file for users to download as a template"""
    data = {
        'Keyword': ['SEO', 'Python', 'Web Scraping', 'Data Analysis', 'Technical SEO'],
        'URL': [
            'https://example.com/seo-guide',
            'https://example.com/python-tutorial',
            'https://example.com/web-scraping',
            'https://example.com/data-analysis',
            'https://example.com/technical-seo'
        ]
    }
    
    df = pd.DataFrame(data)
    
    towrite = io.BytesIO()
    df.to_excel(towrite, index=False, engine='openpyxl')
    towrite.seek(0)
    
    b64 = base64.b64encode(towrite.read()).decode()
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="sample_template.xlsx">Download Sample Template</a>'

def generate_excel_download_link(df, filename="data.xlsx"):
    """Generate a download link for any dataframe as an Excel file"""
    towrite = io.BytesIO()
    df.to_excel(towrite, index=False, engine='openpyxl')
    towrite.seek(0)
    
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">Download Excel File</a>'
    return href
