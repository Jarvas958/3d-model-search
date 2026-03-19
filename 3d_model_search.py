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
        # ddgs.images returns dictionaries with 'title', 'image', 'url', 'source'
        images = ddgs.images(search_query, max_results=24)
        
        for img in images:
            # We only want results that link to actual models, not user profiles or tag pages
            url = img.get('url', '')
            if '/user/' in url or '/tag/' in url:
                continue
                
            results.append({
                'title': img.get('title', '3D Model').split('・')[0][:60] + "...",
                'link': url,
                'image': img.get('image')
            })
            
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
                st.success(f"Found {len(models)} models!")
                
                cols = st.columns(4)
                for idx, model in enumerate(models):
                    with cols[idx % 4]:
                        try:
                            st.image(model['image'], use_container_width=True)
                        except:
                            st.write("*(Image unavailable)*")
                        
                        safe_title = model['title'].replace('[', '').replace(']', '')
                        st.markdown(f"**[{safe_title}]({model['link']})**")
                        st.markdown("---")
    else:
        st.info("Please enter a search query above.")
