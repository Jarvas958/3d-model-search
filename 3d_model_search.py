import streamlit as st
import time
from urllib.parse import urlparse
import json
import urllib.request
import re

# --- PAGE CONFIG & CSS ---
st.set_page_config(page_title="PrintSeeker | 3D Models", page_icon="🧊", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Clean up the top padding */
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    /* Style the image containers to be uniform */
    [data-testid="stImage"] img {
        border-radius: 8px;
        object-fit: cover;
        height: 200px;
        width: 100%;
        border: 1px solid #eef0f4;
    }
    /* Style headers */
    h1 { font-weight: 800; color: #1E88E5; }
    /* Link buttons styling */
    .stLinkButton { width: 100%; margin-top: 10px; }
    .stLinkButton > a { 
        width: 100%; 
        text-align: center; 
        display: block; 
        font-weight: 600;
    }
    /* Model card title constraint */
    .model-title {
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 0.2rem;
        height: 3em;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR & SETTINGS ---
with st.sidebar:
    st.title("🧊 PrintSeeker")
    st.markdown("Your unified search engine for 3D printable models.")
    st.divider()
    
    st.subheader("⚙️ Search Filters")
    st.markdown("Select repositories to search:")
    use_thingiverse = st.checkbox("Thingiverse", value=True)
    use_printables = st.checkbox("Printables", value=True)
    use_cults3d = st.checkbox("Cults3D", value=True)
    use_makerworld = st.checkbox("MakerWorld", value=True)
    use_thangs = st.checkbox("Thangs", value=False)
    
    st.divider()
    max_results = st.slider("Max Results", min_value=12, max_value=60, value=24, step=12)
    
    st.divider()
    st.caption("Using lightweight web search to bypass strict Cloudflare blocks instantly.")

# --- HELPERS ---
def get_site_badge(url):
    domain = urlparse(url).netloc.lower()
    if 'thingiverse' in domain: return "🔵 Thingiverse"
    if 'printables' in domain: return "🟠 Printables"
    if 'cults3d' in domain: return "🟣 Cults3D"
    if 'makerworld' in domain: return "🟢 MakerWorld"
    if 'thangs' in domain: return "🟡 Thangs"
    return "🌐 " + domain.replace('www.', '')

@st.cache_data(show_spinner=False, ttl=3600)
def search_models(q, sites_list, max_res):
    if not sites_list:
        return []
        
    try:
        from duckduckgo_search import DDGS
        ddgs = DDGS()
        site_query = " OR ".join([f"site:{site}" for site in sites_list])
        search_query = f"{q} 3d model {site_query}"
        
        results = []
        seen_links = set()
        
        images = ddgs.images(search_query, max_results=max_res * 2)
        
        for img in images:
            url = img.get('url', '')
            # Filter non-model pages
            if '/user/' in url or '/tag/' in url or '/search/' in url or not url:
                continue
                
            if url in seen_links:
                continue
            seen_links.add(url)
                
            raw_title = img.get('title', '3D Model')
            # Clean title up to first separator to keep it punchy
            clean_title = raw_title.split('・')[0].split('|')[0].split('-')[0].strip()
            # Remove brackets often added by search engines
            clean_title = clean_title.replace('[', '').replace(']', '')
                
            results.append({
                'title': clean_title,
                'link': url,
                'image': img.get('image'),
                'source': get_site_badge(url)
            })
            
            if len(results) >= max_res:
                break
                
        return results
    except Exception as e:
        # Fallback to duckduckgo_search v5 compatible interface if v6 fails
        try:
             from duckduckgo_search import ddg_images
             site_query = " OR ".join([f"site:{site}" for site in sites_list])
             search_query = f"{q} 3d model {site_query}"
             
             results = []
             seen_links = set()
             
             images = ddg_images(search_query, max_results=max_res * 2)
             
             if not images:
                return []
                
             for img in images:
                 url = img.get('url', '')
                 if '/user/' in url or '/tag/' in url or '/search/' in url or not url:
                     continue
                     
                 if url in seen_links:
                     continue
                 seen_links.add(url)
                     
                 raw_title = img.get('title', '3D Model')
                 clean_title = raw_title.split('・')[0].split('|')[0].split('-')[0].strip()
                 clean_title = clean_title.replace('[', '').replace(']', '')
                     
                 results.append({
                     'title': clean_title,
                     'link': url,
                     'image': img.get('image'),
                     'source': get_site_badge(url)
                 })
                 
                 if len(results) >= max_res:
                     break
                     
             return results
        except Exception as fallback_e:
             st.error(f"Search API error: {fallback_e}")
             return []

# --- MAIN UI ---
st.title("Find your next 3D print 🚀")
st.markdown("Search thousands of free and premium models across the top 3D printing communities in one place.")

# Build Site List from Sidebar
active_sites = []
if use_thingiverse: active_sites.append("thingiverse.com")
if use_printables: active_sites.append("printables.com")
if use_cults3d: active_sites.append("cults3d.com")
if use_makerworld: active_sites.append("makerworld.com")
if use_thangs: active_sites.append("thangs.com")

# Search Bar
query = st.chat_input("Search for a model (e.g., 'Articulated Dragon', 'Gridfinity', 'Benchy')...")

# Quick Suggestion Chips (only show if no query)
if not query:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🔥 Trending Searches")
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        if st.button("🛥️ 3D Benchy", use_container_width=True): query = "3D Benchy"
    with sc2:
        if st.button("🐉 Articulated Dragon", use_container_width=True): query = "Articulated Dragon"
    with sc3:
        if st.button("📦 Gridfinity", use_container_width=True): query = "Gridfinity"
    with sc4:
        if st.button("🪴 Planter", use_container_width=True): query = "Planter"

if query:
    if not active_sites:
        st.warning("⚠️ Please select at least one site to search from the sidebar menu.")
    else:
        st.divider()
        start_time = time.time()
        
        with st.spinner(f"🔍 Searching the multiverse for '{query}'..."):
            models = search_models(query, active_sites, max_results)
            
        elapsed = time.time() - start_time
        
        if not models:
            st.warning(f"No models found for '{query}'. Try using different keywords or selecting more sites in the sidebar.")
        else:
            st.success(f"✨ Found **{len(models)}** unique models in {elapsed:.2f} seconds!")
            
            # Display results in a beautifully spaced grid
            cols = st.columns(4, gap="medium")
            for idx, model in enumerate(models):
                with cols[idx % 4]:
                    # Use a container with a border to act like a card
                    with st.container(border=True):
                        try:
                            st.image(model['image'], use_container_width=True)
                        except Exception:
                            st.info("🖼️ Image unavailable")
                        
                        st.markdown(f"<div class='model-title'>{model['title']}</div>", unsafe_allow_html=True)
                        st.caption(f"{model['source']}")
                        st.link_button("📥 View & Download", model['link'], type="primary", use_container_width=True)
