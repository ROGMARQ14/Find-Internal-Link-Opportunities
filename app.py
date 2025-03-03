import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import io
import time
import base64
from utils import create_sample_excel, generate_excel_download_link

st.set_page_config(
    page_title="Inlink Opportunities Finder for SEO",
    page_icon="🔗",
    layout="wide"
)

# Custom CSS to improve appearance
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
    .stAlert {
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔗 Inlink Opportunities Finder for SEO")
st.markdown("""
This app helps you find internal linking opportunities by analyzing your website content.
Upload an Excel file with keywords and URLs, and we'll identify where keywords match text content.
""")

# Functions for processing
def process_excel_file(uploaded_file):
    """Process the uploaded Excel file and extract data"""
    try:
        df = pd.read_excel(uploaded_file)
        return df
    except Exception as e:
        st.error(f"Error processing Excel file: {e}")
        return None

def get_unique_urls(df, url_column):
    """Extract unique URLs from the dataframe"""
    try:
        urls = df[url_column].unique().tolist()
        return list(dict.fromkeys(urls))  # Remove duplicates while preserving order
    except Exception as e:
        st.error(f"Error extracting URLs: {e}")
        return []

def create_keyword_url_pairs(df, keyword_column, url_column):
    """Create pairs of keywords and URLs"""
    keyword_url_pairs = []
    try:
        for _, row in df.iterrows():
            keyword_url_pairs.append([row[keyword_column], row[url_column]])
        return keyword_url_pairs
    except Exception as e:
        st.error(f"Error creating keyword-URL pairs: {e}")
        return []

def crawl_pages_find_matches(urls, keyword_url_pairs, timeout=10, user_agent=None):
    """Crawl pages and find matches between keywords and paragraph content"""
    internal_linking_opportunities = []
    
    headers = {
        'User-Agent': user_agent or 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, url in enumerate(urls):
        try:
            status_text.text(f"Processing URL {i+1}/{len(urls)}: {url}")
            progress_bar.progress((i+1)/len(urls))
            
            response = requests.get(url, headers=headers, timeout=timeout)
            
            if response.status_code != 200:
                st.warning(f"Failed to retrieve {url}: Status code {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            paragraphs = [p.text for p in soup.find_all('p')]
            
            for keyword_pair in keyword_url_pairs:
                keyword, keyword_url = keyword_pair
                
                # Skip if we're checking the same URL that the keyword is from
                if url == keyword_url:
                    continue
                    
                for paragraph in paragraphs:
                    # Case-insensitive search for keyword in paragraph
                    if keyword.lower() in paragraph.lower():
                        internal_linking_opportunities.append([keyword, paragraph, url, keyword_url])
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            st.warning(f"Error processing {url}: {e}")
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    return internal_linking_opportunities

# Main application logic
st.header("Step 1: Upload Excel File")
st.markdown("Upload your Excel file containing keywords and URLs. The file should have columns for keywords and their corresponding URLs.")

# Add sample template download
st.markdown("Need a template? Download our sample file to get started:")
st.markdown(create_sample_excel(), unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload your Excel file containing keywords and URLs", type=["xlsx", "xls"])

if uploaded_file is not None:
    st.success("File uploaded successfully!")
    
    # Process the uploaded file
    with st.spinner("Processing Excel file..."):
        df = process_excel_file(uploaded_file)
    
    if df is not None:
        st.dataframe(df.head())
        
        st.header("Step 2: Configure Settings")
        
        # Column selection
        available_columns = df.columns.tolist()
        
        col1, col2 = st.columns(2)
        with col1:
            keyword_column = st.selectbox("Select the column containing keywords", available_columns)
        with col2:
            url_column = st.selectbox("Select the column containing URLs", available_columns)
        
        # Advanced settings in expander
        with st.expander("Advanced Settings"):
            user_agent = st.text_input(
                "User Agent",
                value="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            timeout = st.slider("Request Timeout (seconds)", min_value=5, max_value=30, value=10)
        
        # Start processing button
        if st.button("Find Inlink Opportunities"):
            with st.spinner("Processing... This may take a while depending on the number of URLs."):
                # Get unique URLs
                urls = get_unique_urls(df, url_column)
                st.info(f"Found {len(urls)} unique URLs to analyze")
                
                # Create keyword-URL pairs
                keyword_url_pairs = create_keyword_url_pairs(df, keyword_column, url_column)
                st.info(f"Created {len(keyword_url_pairs)} keyword-URL pairs")
                
                # Crawl pages and find matches
                result = crawl_pages_find_matches(urls, keyword_url_pairs, timeout, user_agent)
                
                if result:
                    st.header("Step 3: Results")
                    st.success(f"Found {len(result)} potential inlink opportunities!")
                    
                    # Create DataFrame for results
                    result_df = pd.DataFrame(
                        result,
                        columns=["Keyword", "Text", "URL", "Keyword Source URL"]
                    )
                    
                    # Display results
                    st.dataframe(result_df)
                    
                    # Provide download link
                    st.markdown(generate_excel_download_link(result_df, "inlink_opportunities.xlsx"), unsafe_allow_html=True)
                    
                    # Display helpful charts
                    st.header("Data Visualization")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Count of opportunities by URL
                        st.subheader("Opportunities by URL")
                        url_counts = result_df["URL"].value_counts().head(10)
                        st.bar_chart(url_counts)
                    
                    with col2:
                        # Count of opportunities by keyword
                        st.subheader("Opportunities by Keyword")
                        keyword_counts = result_df["Keyword"].value_counts().head(10)
                        st.bar_chart(keyword_counts)
                else:
                    st.warning("No inlink opportunities found. Try adjusting your keywords or URLs.")

# Footer
st.markdown("---")
st.markdown("&copy; 2025 Inlink Opportunities Finder for SEO | Built with Streamlit")
