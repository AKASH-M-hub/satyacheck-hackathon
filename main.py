import streamlit as st
import os
import json
import requests
from bs4 import BeautifulSoup
from PIL import Image
import plotly.graph_objects as go
import google.generativeai as genai
from dotenv import load_dotenv

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SatyaCheck AI | Holographic Command Center",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- "HOLOGRAPHIC AI COMMAND CENTER" THEME ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    /* --- Keyframe Animations --- */
    @keyframes animated-gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes pulse-glow {
        0% { box-shadow: 0 0 25px 0 rgba(0, 212, 255, 0.2); }
        50% { box-shadow: 0 0 40px 10px rgba(0, 212, 255, 0.3); }
        100% { box-shadow: 0 0 25px 0 rgba(0, 212, 255, 0.2); }
    }
    @keyframes typing {
        from { width: 0 }
        to { width: 100% }
    }
    @keyframes blink-caret {
        from, to { border-color: transparent }
        50% { border-color: #00d4ff; }
    }

    /* --- Core Body & Animated Background --- */
    .stApp {
        background: linear-gradient(135deg, #020024, #04044b, #00d4ff, #04044b);
        background-size: 400% 400%;
        animation: animated-gradient 15s ease infinite;
        font-family: 'Poppins', sans-serif;
    }

    /* --- Holographic Panels with 3D Tilt --- */
    .block-container, [data-testid="stSidebar"] > div:first-child {
        background: rgba(10, 25, 47, 0.85);
        border-radius: 15px;
        border: 1px solid rgba(0, 212, 255, 0.3);
        backdrop-filter: blur(8px);
        animation: pulse-glow 5s infinite ease-in-out;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .block-container:hover, [data-testid="stSidebar"] > div:first-child:hover {
        transform: perspective(1000px) rotateX(2deg) rotateY(-2deg) scale(1.01);
        box-shadow: 0 0 50px 15px rgba(0, 212, 255, 0.4);
    }
    
    /* --- Interactive Elements Styling --- */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
        background: rgba(10, 25, 47, 1) !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important; color: white !important;
        border-radius: 8px !important;
    }
    
    /* --- AI Typewriter Effect for Summary --- */
    .typewriter-container {
        overflow: hidden; /* Ensures the text is not visible until the animation plays */
        border-right: .15em solid #00d4ff; /* The typewriter cursor */
        white-space: nowrap; /* Keeps the content on a single line */
        margin: 0 auto; /* Gives that scrolling effect as the typing happens */
        letter-spacing: .05em;
        animation: typing 3.5s steps(40, end), blink-caret .75s step-end infinite;
    }

    /* --- General Typography & Colors --- */
    h1, h2, h3, p, label, .stMarkdown { color: white !important; }
    .stAlert { color: #31333F !important; }
</style>
""", unsafe_allow_html=True)


# --- SETUP THE AI BRAIN & UTILITIES ---
try:
    load_dotenv()
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"🚨 AI Model Error: {e}. Check your API key.", icon="⚠️")
    st.stop()


# --- HELPER FUNCTIONS ---

def get_text_from_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        return ' '.join([p.get_text() for p in paragraphs])
    except Exception as e:
        return f"Error fetching URL: {e}"

# -----------------------------------------------------------------
# --- THIS IS THE CORRECTED AI FUNCTION ---
# -----------------------------------------------------------------
def get_ai_analysis(text_prompt, image=None):
    """
    Analyzes content (text or text+image) using the Gemini model.
    """
    prompt_template = f"""
    As an expert misinformation analyst specializing in the Indian context, analyze the provided content. If the content is an image, describe it, extract any text, and then analyze. Your goal is to identify red flags and educate the user. Do not give a simple true/false verdict.
    Content to analyze: --- {text_prompt} ---
    Provide your analysis ONLY in a structured JSON format with keys: "credibility_score", "summary", "red_flags", "educational_insight". The "red_flags" key must be a list of JSON objects, where each object has a "flag_type" and a "description".
    """
    try:
        # Combine the detailed prompt template with the image if it exists
        request_content = [prompt_template, image] if image else [prompt_template]
        
        response = model.generate_content(request_content)
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        return json.loads(json_text)
    except Exception as e:
        # This will now catch the JSON parsing error if the response is not valid JSON
        return {"error": f"AI analysis failed. The model response was not valid JSON. Details: {str(e)}"}
# -----------------------------------------------------------------
# --- END OF CORRECTED FUNCTION ---
# -----------------------------------------------------------------

def create_gauge_chart(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Trust Score", 'font': {'size': 24, 'color': 'white'}},
        gauge={
            'axis': {'range': [0, 10], 'tickcolor': "white"},
            'bar': {'color': "#00d4ff"}, 'bgcolor': "rgba(0,0,0,0.2)",
            'steps': [
                {'range': [0, 4], 'color': 'rgba(255, 0, 0, 0.5)'},
                {'range': [4, 7], 'color': 'rgba(255, 255, 0, 0.5)'},
                {'range': [7, 10], 'color': 'rgba(0, 255, 0, 0.5)'}
            ],
        }, number={'font': {'color': 'white'}}
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "white"})
    return fig

def display_analysis_report(analysis_result):
    if "error" in analysis_result:
        st.error(f"⚠️ Analysis Error: {analysis_result['error']}", icon="🚫")
        return

    st.balloons()
    st.header("Analysis Report", divider="rainbow")
    col1, col2 = st.columns([1, 2])

    with col1:
        score = analysis_result.get("credibility_score", 0)
        st.plotly_chart(create_gauge_chart(score), use_container_width=True)

    with col2:
        st.subheader("Quick Summary")
        summary_text = analysis_result.get("summary", "No summary available.")
        st.markdown(f'<div class="typewriter-container">{summary_text}</div>', unsafe_allow_html=True)
        st.info("", icon="ℹ️")

    st.subheader("🚨 Detected Red Flags")
    red_flags = analysis_result.get("red_flags", [])
    if red_flags:
        for flag in red_flags:
            if isinstance(flag, dict):
                flag_type = flag.get('flag_type', 'General Flag')
                description = flag.get('description', 'No description provided.')
                st.error(f"**{flag_type}:** {description}", icon="🔥")
            elif isinstance(flag, str):
                st.error(f"**General Flag:** {flag}", icon="🔥")
    else:
        st.success("🎉 No significant red flags were detected.", icon="👍")

    with st.expander("📚 **Click here for the full educational insight**", expanded=True):
        st.success(analysis_result.get("educational_insight", "No educational insight available."))


# --- SIDEBAR & MAIN PAGE ---
with st.sidebar:
    st.title("SatyaCheck AI 🧠")
    st.header("The Digital Truth Sentinel")
    st.info("Welcome to the next generation of misinformation analysis. Our multi-modal AI platform analyzes text, URLs, and images to illuminate the truth.")
    st.success("**Hackathon Champion Edition**")
    st.warning("**Disclaimer:** AI is a powerful tool, not a replacement for critical thinking. Always verify.")

st.title("SatyaCheck AI: The Digital Truth Sentinel")
tab1, tab2, tab3 = st.tabs(["🔎 Analyze Text", "🔗 Analyze URL", "📸 Analyze Image"])

with tab1:
    st.header("Text Analysis Module")
    EXAMPLES = {
        "✨ Select a Pre-loaded Example": "",
        "💰 Lottery Scam Message": "CONGRATS! Your mobile number has won a ₹50,00,000 prize in the KBC Lottery! To claim, transfer ₹5,000 processing fee immediately to UPI ID: kbcwinner@bank. Limited time offer! Call +919876543210 for details. SHARE THIS WITH 5 GROUPS!",
        "🌿 Viral Health 'Cure'": "BREAKING! Doctors HIDING this! Ayurvedic miracle herb 'Velvet Leaf' found in India can CURE ALL types of cancer in 30 days! Research banned by big pharma. Share before they delete this truth!",
    }
    selected_example = st.selectbox("Choose a pre-loaded example:", options=list(EXAMPLES.keys()), key="example_selector")
    text_input = st.text_area("Or, paste your text content here:", value=EXAMPLES[selected_example], height=200, key="text_area")
    if st.button("Initiate Text Scan", use_container_width=True, key="text_btn"):
        if text_input:
            with st.spinner("Analyzing linguistic patterns..."):
                analysis = get_ai_analysis(text_input)
                display_analysis_report(analysis)
        else:
            st.warning("Please provide text for analysis.")

with tab2:
    st.header("URL Analysis Module")
    url_input = st.text_input("Enter webpage URL for deep content scan:", key="url_input")
    if st.button("Initiate URL Scan", use_container_width=True, key="url_btn"):
        if url_input:
            with st.spinner("Deploying web crawler and analyzing content..."):
                scraped_text = get_text_from_url(url_input)
                if "Error" in scraped_text:
                    st.error(scraped_text)
                else:
                    analysis = get_ai_analysis(scraped_text)
                    display_analysis_report(analysis)
        else:
            st.warning("Please provide a URL for analysis.")

with tab3:
    st.header("Image Analysis Module")
    uploaded_image = st.file_uploader("Upload image for optical character and context recognition:", type=["jpg", "jpeg", "png"], key="img_uploader")
    if uploaded_image is not None:
        st.image(uploaded_image, caption="Image awaiting analysis", use_column_width=True)
        if st.button("Initiate Image Scan", use_container_width=True, key="img_btn"):
            with st.spinner("Processing visual data and extracting text..."):
                image = Image.open(uploaded_image)
                # --- THIS IS THE CORRECTED CALL FOR IMAGES ---
                analysis = get_ai_analysis("Analyze the text and context in this image.", image=image)
                display_analysis_report(analysis)
