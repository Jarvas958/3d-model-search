import streamlit as st
from ddgs import DDGS
import urllib.parse

st.set_page_config(page_title="3D Model Finder", page_icon="🧊", layout="wide")

st.title("🧊 3D Model Search Engine")
st.markdown("Search for 3D printable models across Thingiverse, Printables, and Cults3D (powered by DuckDuckGo Search to avoid rate limits).")

query = st.text_input("What do you want to 3D print?", placeholder="e.g., benchy, phone stand, vase")

@st.cache_data(show_spinner=False, ttl=3600)
def search_models(q):
    try:
        ddgs = DDGS()
        # Search specifically for 3D models on popular sites
        search_query = f"{q} 3d model site:thingiverse.com OR site:printables.com OR site:cults3d.com"
        
        results = []
        seen_links = set()
        
        # Request more than we need to account for duplicates and filtering
        images = ddgs.images(search_query, max_results=50)
        
        for img in images:
            url = img.get('url', '')
            # Filter out user profiles, tag pages, or non-model pages
            if '/user/' in url or '/tag/' in url or not url:
                continue
                
            # Prevent duplicates
            if url in seen_links:
                continue
                
            seen_links.add(url)
                
            # Clean up the title a bit (remove site suffixes and markdown brackets)
            title = img.get('title', '3D Model').split('・')[0][:60]
            title = title.replace('[', '').replace(']', '') + ("..." if len(title) == 60 else "")
            
            results.append({
                'title': title,
                'link': url,
                'image': img.get('image')
            })
            
            if len(results) >= 24:
                break
                
        return results
    except Exception as e:
        st.error(f"Search API error: {e}")
        return []

if st.button("Search") or query:
    if query:
        with st.spinner(f"Searching for '{query}'..."):
            models = search_models(query)
            
            if not models:
                st.warning("No models found or search engine rate limit reached. Try a different search.")
            else:
                st.success(f"Found {len(models)} unique models!")
                
                cols = st.columns(4)
                for idx, model in enumerate(models):
                    with cols[idx % 4]:
                        try:
                            # Added a generic fallback in case the image fails to load
                            st.image(model['image'], use_container_width=True)
                        except Exception:
                            st.write("*(Image unavailable)*")
                        
                        st.markdown(f"**[{model['title']}]({model['link']})**")
                        st.markdown("---")
    else:
        st.info("Please enter a search query above.")
