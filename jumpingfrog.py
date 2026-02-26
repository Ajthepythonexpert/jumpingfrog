import streamlit as st
import pandas as pd
import io
import threading
import queue
import time
from urllib.parse import urlparse
 
# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Crawl-x",
    page_icon="🐸",
    layout="wide",
    initial_sidebar_state="collapsed",
)
 
# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap%27);
 
:root {
    --bg: #000000;
    --surface: #000000;
    --card: #162016;
    --border: #2a4a2a;
    --green: #4ade80;
    --green-dim: #22c55e;
    --green-muted: #16a34a;
    --text: #e2ffe2;
    --text-dim: #8aaa8a;
    --accent: #86efac;
    --red: #f87171;
    --yellow: #fbbf24;
}
 
* { box-sizing: border-box; }
 
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif;
}
 
[data-testid="stHeader"] { background: transparent !important; }
 
/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }
 
/* Main container */
.main-wrapper {
    max-width: 1100px;
    margin: 0 auto;
    padding: 2rem 1rem;
}
 
/* Top nav bar */
.top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 0 2.5rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2.5rem;
}
 
.logo-area {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
 
.logo-text {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.4rem;
    color: var(--green);
    letter-spacing: -0.02em;
}
 
.logo-sub {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: var(--text-dim);
    letter-spacing: 0.15em;
    text-transform: uppercase;
}
 
/* Frog mascot — lives in st.components.v1.html iframe */
 
/* Hero Section */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
}
 
.hero-tag {
    display: inline-block;
    background: #162a16;
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 0.3rem 1rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: var(--green);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
}
 
.hero-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: clamp(2.2rem, 5vw, 3.8rem);
    line-height: 1.1;
    color: var(--text);
    letter-spacing: -0.03em;
    margin: 0 0 1rem;
}
 
.hero-title span { color: var(--green); }
 
.hero-desc {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    color: var(--text-dim);
    max-width: 480px;
    margin: 0 auto 2.5rem;
    line-height: 1.8;
}
 
/* Feature cards */
.cards-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.25rem;
    margin-top: 1.5rem;
}
 
.feat-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.75rem 1.5rem;
    cursor: pointer;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}
 
.feat-card::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, #4ade8011 0%, transparent 60%);
    opacity: 0;
    transition: opacity 0.25s;
}
 
.feat-card:hover::before { opacity: 1; }
 
.feat-card:hover {
    border-color: var(--green-muted);
    transform: translateY(-3px);
    box-shadow: 0 12px 40px #4ade8018;
}
 
.card-icon { font-size: 2.2rem; margin-bottom: 1rem; }
 
.card-title {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1.05rem;
    color: var(--text);
    margin-bottom: 0.5rem;
}
 
.card-desc {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-dim);
    line-height: 1.7;
}
 
.card-tag {
    display: inline-block;
    margin-top: 1rem;
    padding: 0.2rem 0.7rem;
    background: #1a2e1a;
    border: 1px solid var(--border);
    border-radius: 999px;
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem;
    color: var(--green-dim);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
 
/* Back button */
.back-btn-wrapper {
    margin-bottom: 2rem;
}
 
/* Tool page header */
.tool-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.5rem;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    margin-bottom: 2rem;
}
 
.tool-icon { font-size: 2.5rem; }
 
.tool-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.6rem;
    color: var(--text);
}
 
.tool-sub {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-dim);
    margin-top: 0.25rem;
}
 
/* Input styling */
.stTextInput > div > div > input {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
    padding: 0.65rem 1rem !important;
}
 
.stTextInput > div > div > input:focus {
    border-color: var(--green) !important;
    box-shadow: 0 0 0 2px #4ade8022 !important;
}
 
.stTextInput > label {
    color: var(--text-dim) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.75rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.05em !important;
}
 
/* Buttons */
.stButton > button {
    background: var(--green) !important;
    color: #0a0f0a !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.65rem 1.8rem !important;
    transition: all 0.2s !important;
    letter-spacing: 0.01em !important;
}
 
.stButton > button:hover {
    background: var(--green-dim) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px #4ade8040 !important;
}
 
/* Divider */
.stDivider { border-color: var(--border) !important; }
 
/* Progress & spinners */
.stProgress > div > div {
    background: var(--green) !important;
}
 
/* Metrics */
[data-testid="stMetric"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}
 
[data-testid="stMetricLabel"] {
    color: var(--text-dim) !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.72rem !important;
}
 
[data-testid="stMetricValue"] {
    color: var(--green) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
}
 
/* Data frames */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}
 
/* Expander */
.streamlit-expanderHeader {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}
 
/* Alerts */
.stAlert {
    border-radius: 8px !important;
    border-left: 3px solid var(--green) !important;
}
 
/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
 
/* Info box override */
[data-testid="stInfo"] {
    background: #162a16 !important;
    border-color: var(--green-muted) !important;
    color: var(--text) !important;
}
 
/* Select box */
.stSelectbox > div > div {
    background: var(--card) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}
 
/* Download button */
.stDownloadButton > button {
    background: transparent !important;
    color: var(--green) !important;
    border: 1px solid var(--green) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
}
 
.stDownloadButton > button:hover {
    background: #4ade8018 !important;
}
 
/* Log output */
.log-box {
    background: #000000;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1rem;
    font-family: 'Space Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-dim);
    max-height: 320px;
    overflow-y: auto;
    line-height: 1.8;
}
 
.log-match { color: #f87171; }
.log-ok { color: var(--green-dim); }
.log-redirect { color: var(--yellow); }
 
/* Status chips */
.chip {
    display: inline-block;
    padding: 0.15rem 0.6rem;
    border-radius: 999px;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}
 
.chip-green { background: #162a16; color: var(--green); border: 1px solid var(--green-muted); }
.chip-red { background: #2a1010; color: var(--red); border: 1px solid #7f1d1d; }
.chip-yellow { background: #2a2010; color: var(--yellow); border: 1px solid #78350f; }
 
</style>
""", unsafe_allow_html=True)
 
# ─── Session state init ─────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"
if "frog_jump" not in st.session_state:
    st.session_state.frog_jump = False
 
# ─── Helpers ───────────────────────────────────────────────────────────────────
def go_to(page):
    st.session_state.page = page
    st.rerun()
 
def go_home():
    st.session_state.page = "home"
    st.rerun()
 
def top_bar():
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("""
        <div class="logo-area">
            <div>
                <div class="logo-text">🌐 Crawl-X</div>
                <div class="logo-sub">SEO Crawl & Audit Suite</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        import streamlit.components.v1 as components
        components.html("""
        <style>
          body { margin:0; background:transparent; display:flex; flex-direction:column; align-items:flex-end; padding-right:4px; }
 
          @keyframes frogJump {
            0%   { transform: translateY(0)    scaleY(1)    scaleX(1)    rotate(0deg); }
            10%  { transform: translateY(0)    scaleY(0.65) scaleX(1.35) rotate(0deg); }
            35%  { transform: translateY(-70px) scaleY(1.1)  scaleX(0.9)  rotate(-12deg); }
            55%  { transform: translateY(-90px) scaleY(1)    scaleX(1)    rotate(8deg); }
            72%  { transform: translateY(-18px) scaleY(0.75) scaleX(1.25) rotate(0deg); }
            82%  { transform: translateY(0)    scaleY(1.2)  scaleX(0.85) rotate(0deg); }
            91%  { transform: translateY(-6px)  scaleY(0.95) scaleX(1.05) rotate(0deg); }
            100% { transform: translateY(0)    scaleY(1)    scaleX(1)    rotate(0deg); }
          }
 
          #frog {
            font-size: 2.8rem;
            cursor: pointer;
            display: inline-block;
            filter: drop-shadow(0 0 14px rgba(74,222,128,0.55));
            transform-origin: bottom center;
            transition: filter 0.2s;
            user-select: none;
            -webkit-user-select: none;
          }
 
          #frog:hover {
            filter: drop-shadow(0 0 22px rgba(74,222,128,0.9));
          }
 
          #frog.jumping {
            animation: frogJump 0.72s cubic-bezier(0.36,0.07,0.19,0.97) forwards;
          }
 
          #label {
            font-family: 'Space Mono', monospace;
            font-size: 0.6rem;
            color: #4a6a4a;
            margin-top: 2px;
          }
 
          /* particle burst */
          .particle {
            position: fixed;
            pointer-events: none;
            font-size: 1rem;
            animation: burst 0.7s ease-out forwards;
          }
          @keyframes burst {
            0%   { opacity:1; transform: translate(0,0) scale(1); }
            100% { opacity:0; transform: translate(var(--tx), var(--ty)) scale(0.3); }
          }
        </style>
 
        <span id="frog" title="Click me!">🐸</span>
        <div id="label">click the frog!</div>
 
        <script>
          const frog = document.getElementById('frog');
          const emojis = ['💚','✨','🌿','⭐','🍃','💫'];
 
          frog.addEventListener('click', function(e) {
            // Trigger jump
            frog.classList.remove('jumping');
            void frog.offsetWidth;
            frog.classList.add('jumping');
            frog.addEventListener('animationend', () => frog.classList.remove('jumping'), { once: true });
 
            // Particle burst
            const rect = frog.getBoundingClientRect();
            const cx = rect.left + rect.width / 2;
            const cy = rect.top + rect.height / 2;
            for (let i = 0; i < 8; i++) {
              const p = document.createElement('span');
              p.className = 'particle';
              p.textContent = emojis[Math.floor(Math.random() * emojis.length)];
              const angle = (i / 8) * Math.PI * 2;
              const dist = 45 + Math.random() * 40;
              p.style.setProperty('--tx', Math.cos(angle) * dist + 'px');
              p.style.setProperty('--ty', Math.sin(angle) * dist + 'px');
              p.style.left = cx + 'px';
              p.style.top  = cy + 'px';
              document.body.appendChild(p);
              setTimeout(() => p.remove(), 750);
            }
          });
        </script>
        """, height=90)
 
# ─── Run Scrapy in subprocess ───────────────────────────────────────────────────
import subprocess, sys, os, json, tempfile
 
def safe_path(p: str) -> str:
    """Normalise Windows backslash paths to forward slashes so they are safe
    to embed as string literals inside generated Python scripts."""
    return p.replace("\\", "/")
 
def run_scrapy_spider(spider_script: str, tmp_dir: str) -> tuple[list, str]:
    """Write spider to temp file and run via subprocess."""
    spider_file = os.path.join(tmp_dir, "spider_run.py")
    with open(spider_file, "w", encoding="utf-8") as f:
        f.write(spider_script)
    result = subprocess.run(
        [sys.executable, spider_file],
        capture_output=True, text=True, cwd=tmp_dir
    )
    return result.stdout, result.stderr
 
def build_keyword_script(sitemap_url, search_text, path_filter, out_json):
    out_json = safe_path(out_json)
    return f"""
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
import advertools as adv
from urllib.parse import urlparse
import json
 
class KWSpider(scrapy.Spider):
    name = 'kw_spider'
    custom_settings = {{
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'DOWNLOAD_DELAY': 0.3,
        'LOG_LEVEL': 'ERROR',
        'HTTPERROR_ALLOWED_CODES': [404, 400, 403, 301, 308],
        'RETRY_TIMES': 2,
        'ROBOTSTXT_OBEY': False,
    }}
 
    def __init__(self):
        parsed = urlparse("{sitemap_url}")
        self.allowed_domains = [parsed.netloc]
        self.base_folder = parsed.path.replace('sitemap.xml', '')
        self.search_text = "{search_text}".lower()
        self.path_filter = "{path_filter}"
        self.results = []
        self.visited = set()
        self.sitemap_urls = set()
        try:
            import advertools as adv
            df = adv.sitemap_to_df("{sitemap_url}")
            self.sitemap_urls = set(df['loc'].dropna().unique())
        except: pass
 
    def start_requests(self):
        homepage = "{sitemap_url}".replace('sitemap.xml', '')
        yield scrapy.Request(homepage, callback=self.parse_page, meta={{'from': 'Homepage'}})
        for u in self.sitemap_urls:
            yield scrapy.Request(u, callback=self.parse_page, meta={{'from': 'XML Sitemap'}})
 
    def parse_page(self, response):
        if response.url in self.visited:
            return
        self.visited.add(response.url)
        kw_found = False
        if response.status == 200:
            kw_found = self.search_text in response.text.lower()
        self.results.append({{
            'URL': response.url,
            'Status': response.status,
            'Keyword_Found': kw_found,
            'Found_On': response.meta.get('from','Unknown')
        }})
        if response.status == 200:
            fp = self.path_filter if self.path_filter else self.base_folder
            from scrapy.linkextractors import LinkExtractor
            for link in LinkExtractor(allow=fp).extract_links(response):
                if link.url not in self.visited:
                    yield scrapy.Request(link.url, callback=self.parse_page, meta={{'from': response.url}})
 
    def closed(self, reason):
        with open("{out_json}", "w") as f:
            json.dump({{'results': self.results, 'sitemap': list(self.sitemap_urls)}}, f)
 
process = CrawlerProcess()
process.crawl(KWSpider)
process.start()
"""
 
def build_redirect_script(sitemap_url, path_filter, out_json):
    out_json = safe_path(out_json)
    return f"""
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
import advertools as adv
from urllib.parse import urlparse
import json
 
class RedirectSpider(scrapy.Spider):
    name = 'redirect_spider'
    custom_settings = {{
        'USER_AGENT': 'Mozilla/5.0 AppleWebKit/537.36',
        'DOWNLOAD_DELAY': 0.3,
        'LOG_LEVEL': 'ERROR',
        'REDIRECT_ENABLED': False,
        'HTTPERROR_ALLOWED_CODES': [301, 302, 307, 308, 404],
    }}
 
    def __init__(self):
        parsed = urlparse("{sitemap_url}")
        self.domain = parsed.netloc
        self.allowed_domains = [self.domain]
        self.base_folder = parsed.path.replace('sitemap.xml', '')
        self.path_filter = "{path_filter}"
        self.results = []
        self.visited = set()
        self.sitemap_urls = set()
        try:
            df = adv.sitemap_to_df("{sitemap_url}")
            self.sitemap_urls = set(df['loc'].dropna().unique())
        except: pass
 
    def start_requests(self):
        parsed = urlparse("{sitemap_url}")
        hp = f"{{parsed.scheme}}://{{self.domain}}{{self.base_folder}}"
        yield scrapy.Request(hp, callback=self.trace, meta={{'path': [hp], 'from': 'Entry'}})
 
    def trace(self, response):
        path = response.meta.get('path', [])
        source = response.meta.get('from', 'Unknown')
        if response.url in self.visited and response.status == 200:
            return
        self.visited.add(response.url)
        if response.status in [301, 302, 307, 308]:
            loc = response.headers.get('Location', b'').decode('utf-8')
            if loc.startswith('/'):
                parsed = urlparse(response.url)
                loc = f"{{parsed.scheme}}://{{self.domain}}{{loc}}"
            if loc in path:
                self.results.append({{'URL': path[0], 'Status': 'LOOP', 'Final_Dest': loc, 'Chain': ' -> '.join(path) + f' -> {{loc}}', 'Source': source}})
                return
            yield scrapy.Request(loc, callback=self.trace, meta={{'path': path + [loc], 'from': source}})
            return
        self.results.append({{'URL': path[0], 'Status': response.status, 'Final_Dest': response.url if len(path)>1 else 'Direct', 'Chain': ' -> '.join(path) if len(path)>1 else 'None', 'Source': source}})
        if response.status == 200:
            fp = self.path_filter if self.path_filter else self.base_folder
            for link in LinkExtractor(allow=fp).extract_links(response):
                if link.url not in self.visited:
                    yield scrapy.Request(link.url, callback=self.trace, meta={{'path': [link.url], 'from': response.url}})
 
    def closed(self, reason):
        with open("{out_json}", "w") as f:
            json.dump({{'results': self.results, 'sitemap': list(self.sitemap_urls)}}, f)
 
process = CrawlerProcess()
process.crawl(RedirectSpider)
process.start()
"""
 
def build_sitemap_script(sitemap_url, out_json):
    out_json = safe_path(out_json)
    return f"""
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
import advertools as adv
from urllib.parse import urlparse
import json

class SitemapSpider(scrapy.Spider):
    name = 'sitemap_spider'
    custom_settings = {{
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'DOWNLOAD_DELAY': 0.3,
        'LOG_LEVEL': 'INFO',
        'ROBOTSTXT_OBEY': False,
    }}

    def __init__(self):
        super().__init__()
        parsed = urlparse("{sitemap_url}")
        self.allowed_domains = [parsed.netloc]
        # Set start URL to the folder level
        self.start_url = "{sitemap_url}".replace('sitemap.xml', '')
        self.folder_path = parsed.path.replace('sitemap.xml', '')
        self.live_urls = []
        self.sitemap_urls = []
        self.visited = set()
        
        # Pull Sitemap URLs immediately
        try:
            df = adv.sitemap_to_df("{sitemap_url}")
            self.sitemap_urls = df['loc'].dropna().unique().tolist()
        except: 
            pass

    def start_requests(self):
        yield scrapy.Request(self.start_url, callback=self.parse_item)

    def parse_item(self, response):
        if response.url in self.visited:
            return
        self.visited.add(response.url)
        
        if response.status == 200:
            self.live_urls.append(response.url)
            
            # Extract and follow links recursively
            le = LinkExtractor(allow=self.folder_path)
            for link in le.extract_links(response):
                if link.url not in self.visited:
                    yield scrapy.Request(link.url, callback=self.parse_item)

    def closed(self, reason):
        with open("{out_json}", "w") as f:
            json.dump({{'live': list(set(self.live_urls)), 'sitemap': self.sitemap_urls}}, f)

process = CrawlerProcess()
process.crawl(SitemapSpider)
process.start()
"""

def df_to_excel_bytes(sheets: dict) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name[:31], index=False)
    return buf.getvalue()
 
# ═══════════════════════════════════════════════════════════════════
# HOME PAGE
# ═══════════════════════════════════════════════════════════════════
def page_home():
    top_bar()
 
    st.markdown("""
    <style>
    .center-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 45vh;   /* Full screen height */
        text-align: center;
    }
 
    .hero {
        max-width: 700px;
    }
 
    .hero-title span {
        color: #00c853;  /* Optional accent color */
    }
    </style>
 
    <div class="center-wrapper">
        <div class="hero">
            <div class="hero-tag">🐸 Powered by Scrapy + Advertools</div>
            <h1 class="hero-title">
                Crawl. Audit.<br><span>Dominate.</span>
            </h1>
            <p class="hero-desc">
                CREATED BY GBS MA 2<br>
                Pick a tool below and run it.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
 
    col1, col2, col3 = st.columns(3)
 
    with col1:
        st.markdown("""
        <div class="feat-card">
            <div class="card-icon">🔍</div>
            <div class="card-title">Keyword Finder</div>
            <div class="card-desc">Crawl your site to find pages containing a specific keyword or phrase — perfect for hunting "no results" pages or content audits.</div>
            <div class="card-tag">keyword · content audit</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Keyword Finder", key="btn_kw", use_container_width=True):
            go_to("keyword")
 
    with col2:
        st.markdown("""
        <div class="feat-card">
            <div class="card-icon">🔄</div>
            <div class="card-title">Redirect Loop Finder</div>
            <div class="card-desc">Trace every redirect chain on your site. Detects 301/302/307/308 hops, infinite loops, dead links, and maps missing XML entries.</div>
            <div class="card-tag">redirects · loops · 404s</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Redirect Finder", key="btn_rd", use_container_width=True):
            go_to("redirect")
 
    with col3:
        st.markdown("""
        <div class="feat-card">
            <div class="card-icon">🗺️</div>
            <div class="card-title">Sitemap Auditor</div>
            <div class="card-desc">Compare your live site against the XML sitemap. Expose orphan pages, missing entries, and get a full side-by-side URL report.</div>
            <div class="card-tag">sitemap · orphans · coverage</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Launch Sitemap Auditor", key="btn_sm", use_container_width=True):
            go_to("sitemap")
 
    st.markdown("""
    <div style="text-align:center;margin-top:3rem;padding-top:2rem;border-top:1px solid var(--border);">
        <span style="font-family:'Space Mono',monospace;font-size:0.7rem;color:#4a6a4a;">
            webaudit pro · built with scrapy + streamlit · 🐸
        </span>
    </div>
    """, unsafe_allow_html=True)
 
 
# ═══════════════════════════════════════════════════════════════════
# KEYWORD FINDER
# ═══════════════════════════════════════════════════════════════════
def page_keyword():
    top_bar()
    if st.button("← Back to Home", key="back_kw"):
        go_home()
 
    st.markdown("""
    <div class="tool-header">
        <div class="tool-icon">🔍</div>
        <div>
            <div class="tool-title">Keyword Finder</div>
            <div class="tool-sub">Scan every page for a text match · Exports 4-sheet Excel report</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
 
    with st.form("kw_form"):
        sitemap_url = st.text_input("Sitemap XML URL", placeholder="https://example.com/sitemap.xml")
        search_text = st.text_input("Keyword to search for", placeholder="e.g. no product results")
        path_filter = st.text_input("Sub-folder filter (optional)", placeholder="e.g. /mkt-category/ — leave blank for full site")
        submitted = st.form_submit_button("🚀 Start Crawl")
 
    if submitted:
        if not sitemap_url or not search_text:
            st.error("Please fill in Sitemap URL and Keyword fields.")
            return
 
        progress_bar = st.progress(0, text="Initialising crawler…")
        status_area = st.empty()
        log_area = st.empty()
 
        with tempfile.TemporaryDirectory() as tmp:
            out_json = os.path.join(tmp, "results.json")
            script = build_keyword_script(sitemap_url, search_text.lower(), path_filter, out_json)
 
            progress_bar.progress(10, text="Launching Scrapy spider…")
            status_area.info("🕷️ Spider is running. This may take a few minutes depending on site size.")
 
            stdout, stderr = run_scrapy_spider(script, tmp)
 
            progress_bar.progress(90, text="Processing results…")
 
            if not os.path.exists(out_json):
                st.error("Spider did not produce output. Check the URL and try again.")
                with st.expander("Debug output"):
                    st.code(stderr[-3000:] if stderr else "No stderr")
                return
 
            with open(out_json) as f:
                data = json.load(f)
 
        df_all = pd.DataFrame(data["results"]).drop_duplicates(subset=["URL"])
        df_official = pd.DataFrame(data["sitemap"], columns=["URL"]) if data["sitemap"] else pd.DataFrame(columns=["URL"])
 
        keyword_hits = df_all[df_all["Keyword_Found"] == True]
        missing_in_xml = df_all[(df_all["Status"] == 200) & (~df_all["URL"].isin(df_official["URL"]))]
        orphans = df_official[~df_official["URL"].isin(df_all["URL"])]
 
        progress_bar.progress(100, text="Done!")
        status_area.success("✅ Crawl complete!")
 
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Pages Scanned", len(df_all))
        c2.metric("🚩 Keyword Hits", len(keyword_hits))
        c3.metric("Missing from XML", len(missing_in_xml))
        c4.metric("Orphan Pages", len(orphans))
 
        if len(keyword_hits):
            st.markdown("### 🚩 Keyword Hits")
            st.dataframe(keyword_hits, use_container_width=True)
 
        with st.expander("📋 All Scanned Pages"):
            st.dataframe(df_all, use_container_width=True)
 
        sheets = {
            "1. KEYWORD HITS": keyword_hits,
            "2. Missing from Sitemap": missing_in_xml,
            "3. Orphans (XML Only)": orphans,
            "4. All Live Audit": df_all,
            "5. Official Sitemap List": df_official,
        }
        excel_bytes = df_to_excel_bytes(sheets)
        st.download_button(
            "⬇️ Download Full Excel Report",
            data=excel_bytes,
            file_name=f"Keyword_Audit_{urlparse(sitemap_url).netloc}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
 
 
# ═══════════════════════════════════════════════════════════════════
# REDIRECT FINDER
# ═══════════════════════════════════════════════════════════════════
def page_redirect():
    top_bar()
    if st.button("← Back to Home", key="back_rd"):
        go_home()
 
    st.markdown("""
    <div class="tool-header">
        <div class="tool-icon">🔄</div>
        <div>
            <div class="tool-title">Redirect Loop Finder</div>
            <div class="tool-sub">Trace full redirect chains · Detect loops · Expose dead links</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
 
    with st.form("rd_form"):
        sitemap_url = st.text_input("Sitemap XML URL", placeholder="https://example.com/sitemap.xml")
        path_filter = st.text_input("Sub-folder filter (optional)", placeholder="e.g. /mkt-category/")
        submitted = st.form_submit_button("🚀 Start Redirect Trace")
 
    if submitted:
        if not sitemap_url:
            st.error("Please provide a Sitemap URL.")
            return
 
        progress_bar = st.progress(0, text="Initialising…")
        status_area = st.empty()
 
        with tempfile.TemporaryDirectory() as tmp:
            out_json = os.path.join(tmp, "results.json")
            script = build_redirect_script(sitemap_url, path_filter, out_json)
 
            progress_bar.progress(10, text="Launching Scrapy spider…")
            status_area.info("🕷️ Tracing redirects. Running…")
 
            stdout, stderr = run_scrapy_spider(script, tmp)
            progress_bar.progress(90, text="Analysing chains…")
 
            if not os.path.exists(out_json):
                st.error("Spider produced no output.")
                with st.expander("Debug"):
                    st.code(stderr[-3000:])
                return
 
            with open(out_json) as f:
                data = json.load(f)
 
        df_all = pd.DataFrame(data["results"]).drop_duplicates(subset=["URL"]) if data["results"] else pd.DataFrame()
        sitemap_list = data.get("sitemap", [])
 
        if df_all.empty:
            st.warning("No data returned. Check your URL.")
            return
 
        redirects = df_all[df_all["Status"].isin([301, 302, 307, 308, "LOOP"])] if "Status" in df_all.columns else pd.DataFrame()
        loops = df_all[df_all["Status"] == "LOOP"] if "Status" in df_all.columns else pd.DataFrame()
        missing_in_xml = df_all[(df_all["Status"] == 200) & (~df_all["URL"].isin(sitemap_list))] if sitemap_list else pd.DataFrame()
        orphans_list = [u for u in sitemap_list if u not in df_all["URL"].values]
        orphans = pd.DataFrame(orphans_list, columns=["URL"])
        dead = df_all[df_all["Status"] == 404] if "Status" in df_all.columns else pd.DataFrame()
 
        progress_bar.progress(100, "Done!")
        status_area.success("✅ Redirect trace complete!")
 
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total URLs", len(df_all))
        c2.metric("🔄 Redirects", len(redirects))
        c3.metric("♾️ Loops", len(loops))
        c4.metric("💀 Dead Links", len(dead))
 
        if not redirects.empty:
            st.markdown("### 🔄 Redirects & Loops")
            st.dataframe(redirects, use_container_width=True)
 
        if not dead.empty:
            st.markdown("### 💀 Dead Links (404)")
            st.dataframe(dead, use_container_width=True)
 
        sheets = {
            "1. Redirects & Loops": redirects if not redirects.empty else pd.DataFrame(),
            "2. Not in Sitemap": missing_in_xml if not missing_in_xml.empty else pd.DataFrame(),
            "3. Orphans (XML Only)": orphans,
            "4. Dead Links (404)": dead if not dead.empty else pd.DataFrame(),
            "5. All Discovered Links": df_all,
        }
        excel_bytes = df_to_excel_bytes(sheets)
        st.download_button(
            "⬇️ Download Redirect Report",
            data=excel_bytes,
            file_name=f"Redirect_Audit_{urlparse(sitemap_url).netloc}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
 
 
# ═══════════════════════════════════════════════════════════════════
# SITEMAP AUDITOR
# ═══════════════════════════════════════════════════════════════════
def page_sitemap():
    top_bar()
    if st.button("← Back to Home", key="back_sm"):
        go_home()
 
    st.markdown("""
    <div class="tool-header">
        <div class="tool-icon">🗺️</div>
        <div>
            <div class="tool-title">Sitemap Auditor</div>
            <div class="tool-sub">Compare live pages vs XML sitemap · Find orphans & coverage gaps</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
 
    with st.form("sm_form"):
        sitemap_url = st.text_input("Sitemap XML URL", placeholder="https://example.com/sitemap.xml")
        submitted = st.form_submit_button("🚀 Start Sitemap Audit")
 
    if submitted:
        if not sitemap_url:
            st.error("Please provide a Sitemap URL.")
            return
 
        progress_bar = st.progress(0, text="Initialising…")
        status_area = st.empty()
 
        with tempfile.TemporaryDirectory() as tmp:
            out_json = os.path.join(tmp, "results.json")
            script = build_sitemap_script(sitemap_url, out_json)
 
            progress_bar.progress(10, text="Launching sitemap spider…")
            status_area.info("🕷️ Crawling live pages and loading XML sitemap…")
 
            stdout, stderr = run_scrapy_spider(script, tmp)
            progress_bar.progress(90, text="Comparing…")
 
            if not os.path.exists(out_json):
                st.error("Spider produced no output.")
                with st.expander("Debug"):
                    st.code(stderr[-3000:])
                return
 
            with open(out_json) as f:
                data = json.load(f)
 
        df_live = pd.DataFrame(list(set(data.get("live", []))), columns=["URL"])
        df_official = pd.DataFrame(data.get("sitemap", []), columns=["URL"]).drop_duplicates()
 
        missing_in_xml = df_live[~df_live["URL"].isin(df_official["URL"])]
        orphans = df_official[~df_official["URL"].isin(df_live["URL"])]
 
        progress_bar.progress(100, "Done!")
        status_area.success("✅ Sitemap audit complete!")
 
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Live Pages Found", len(df_live))
        c2.metric("XML Sitemap Entries", len(df_official))
        c3.metric("Missing from XML", len(missing_in_xml))
        c4.metric("Orphan Pages", len(orphans))
 
        tab1, tab2, tab3, tab4 = st.tabs(["🌐 All Live", "📋 Official XML", "⚠️ Missing from XML", "👻 Orphans"])
        with tab1:
            st.dataframe(df_live, use_container_width=True)
        with tab2:
            st.dataframe(df_official, use_container_width=True)
        with tab3:
            if missing_in_xml.empty:
                st.success("All live pages are in the XML sitemap 🎉")
            else:
                st.dataframe(missing_in_xml, use_container_width=True)
        with tab4:
            if orphans.empty:
                st.success("No orphan pages found 🎉")
            else:
                st.dataframe(orphans, use_container_width=True)
 
        sheets = {
            "All Live Links": df_live,
            "Official Sitemap": df_official,
            "Missing From XML": missing_in_xml,
            "Orphans (In XML only)": orphans,
        }
        excel_bytes = df_to_excel_bytes(sheets)
        domain = urlparse(sitemap_url).netloc
        st.download_button(
            "⬇️ Download Sitemap Report",
            data=excel_bytes,
            file_name=f"Sitemap_Audit_{domain}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
 
 
# ─── Router ────────────────────────────────────────────────────────────────────
page = st.session_state.page
if page == "home":
    page_home()
elif page == "keyword":
    page_keyword()
elif page == "redirect":
    page_redirect()
elif page == "sitemap":
    page_sitemap()
