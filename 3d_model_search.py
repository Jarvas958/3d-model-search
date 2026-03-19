import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse

# Set page configuration
st.set_page_config(page_title="3D Model Finder", page_icon="🧊", layout="wide")

# App Header
st.title("🧊 3D Model Search Engine")
st.markdown("Search for 3D printable models across Thingiverse, Printables, Cults3D, and more (using the Yeggi meta-search engine).")

# Search Input
query = st.text_input("What do you want to 3D print?", placeholder="e.g., benchy, phone stand, vase")

# Scraper function targeting Yeggi (an aggregator for 3D print models)
@st.cache_data(show_spinner=False)
def search_models(q):
    url = f"https://www.yeggi.com/q/{urllib.parse.quote(q)}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        results = []
        # Find model links containing images
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            # Filter for outbound tracking links or model detail pages
            if '/url/' in href or 'thingiverse' in href or 'printables' in href or 'yeggi.com/model/' in href or 'yeggi.com/r' in href:
                img = a_tag.find('img')
                if img and img.get('src') and not 'logo' in img.get('src', '').lower():
                    link = href
                    if link.startswith('/'):
                        link = 'https://www.yeggi.com' + link
                        
                    img_url = img.get('src')
                    if img_url.startswith('/'):
                        img_url = 'https://www.yeggi.com' + img_url
                        
                    title = img.get('alt', '').strip() or a_tag.get('title', '3D Model')
                    
                    # Prevent duplicates
                    if title and not any(res['link'] == link for res in results):
                        results.append({
                            'title': title,
                            'link': link,
                            'image': img_url
                        })
            
            if len(results) >= 24: # Limit to 24 results
                break
                
        return results
    except Exception as e:
        st.error(f"Error fetching results: {e}")
        return []

# Execute Search
if st.button("Search") or query:
    if query:
        with st.spinner(f"Scraping the web for '{query}'..."):
            models = search_models(query)
            
            if not models:
                st.warning("No models found. The site structure may have changed, or your IP is being rate-limited.")
            else:
                st.success(f"Found {len(models)} models!")
                
                # Display results in a responsive grid
                cols = st.columns(4)
                for idx, model in enumerate(models):
                    with cols[idx % 4]:
                        # Streamlit image with markdown link
                        st.image(model['image'], use_container_width=True)
                        
                        # Clean up title for markdown
                        safe_title = model['title'].replace('[', '').replace(']', '')
                        st.markdown(f"**[{safe_title}]({model['link']})**")
                        st.markdown("---")
    else:
        st.info("Please enter a search query above.")