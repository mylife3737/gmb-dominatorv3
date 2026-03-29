import streamlit as st
import anthropic
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import io
import requests
from datetime import datetime

st.set_page_config(page_title="GMB Dominator", page_icon="🗺️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; background-color: #f8f7f4; color: #1a1a2e; }
h1, h2, h3, h4 { font-family: 'Syne', sans-serif !important; color: #1a1a2e !important; }
.gmb-hero { text-align: center; padding: 2rem 0 1.5rem; }
.gmb-hero h1 { font-size: 3rem; font-weight: 800; background: linear-gradient(135deg, #ff6b00, #ff9500); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 0; }
.gmb-hero .tagline { font-size: 0.95rem; color: #888; margin-top: 0.4rem; letter-spacing: 0.08em; text-transform: uppercase; }
.gate-card { background: #fff; border: 1px solid #ffe0c8; border-radius: 16px; padding: 2.5rem; max-width: 480px; margin: 2rem auto; box-shadow: 0 8px 30px rgba(255,107,0,0.1); }
.section-badge { display: inline-block; background: rgba(255,107,0,0.1); border: 1px solid rgba(255,107,0,0.3); color: #ff6b00; font-family: 'Syne', sans-serif; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; padding: 4px 12px; border-radius: 20px; margin-bottom: 0.5rem; }
.section-title { font-family: 'Syne', sans-serif; font-size: 1.5rem; font-weight: 700; margin: 0 0 1rem; color: #1a1a2e; }
.scan-ready { background: #f0fff8; border: 1px solid #00c864; border-radius: 10px; padding: 1rem 1.2rem; color: #007a3d; font-weight: 500; }
.scan-missing { background: #fff5f5; border: 1px solid #ff4444; border-radius: 10px; padding: 1rem 1.2rem; color: #cc0000; font-weight: 500; }
.scan-neutral { background: #fffbf0; border: 1px solid #ffc800; border-radius: 10px; padding: 1rem 1.2rem; color: #996600; font-weight: 500; }
.tier-card { background: #fff; border: 1px solid #eee; border-radius: 14px; padding: 1.5rem; margin-bottom: 1rem; position: relative; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.tier-card::before { content: ''; position: absolute; top:0; left:0; right:0; height:3px; }
.tier-1::before { background: linear-gradient(90deg, #ff6b00, #ff9500); }
.tier-2::before { background: linear-gradient(90deg, #00b4d8, #0077b6); }
.tier-3::before { background: linear-gradient(90deg, #7b2fff, #c44fff); }
.tier-label { font-size: 0.65rem; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; opacity: 0.5; margin-bottom: 0.3rem; }
.tier-title { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; margin-bottom: 0.5rem; color: #1a1a2e; }
.lead-card { background: #fff8f2; border: 1px solid #ffe0c8; border-radius: 14px; padding: 1.5rem; margin-top: 1.5rem; }
.disclaimer { background: #f5f5f5; border: 1px solid #ddd; border-radius: 10px; padding: 1rem 1.2rem; font-size: 0.8rem; color: #888; margin-top: 2rem; }
.stTextInput > div > div > input, .stTextArea textarea { background: #fff !important; border: 1px solid #ddd !important; color: #1a1a2e !important; border-radius: 8px !important; }
.stSelectbox > div > div { background: #fff !important; border: 1px solid #ddd !important; border-radius: 8px !important; color: #1a1a2e !important; }
.stButton > button { background: linear-gradient(135deg, #ff6b00, #ff9500) !important; color: white !important; border: none !important; border-radius: 8px !important; font-family: 'Syne', sans-serif !important; font-weight: 700 !important; padding: 0.6rem 1.5rem !important; }
[data-testid="stSidebar"] { background: #fff !important; border-right: 1px solid #eee !important; }
</style>
""", unsafe_allow_html=True)

ACCESS_CODE = "GROW2026"

def extract_exif(image_bytes):
    try:
        img = Image.open(io.BytesIO(image_bytes))
        exif_data = img._getexif()
        if not exif_data: return None, None, None
        gps_info = {}; timestamp = None
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                for gps_tag_id, gps_value in value.items():
                    gps_info[GPSTAGS.get(gps_tag_id, gps_tag_id)] = gps_value
            elif tag in ("DateTime","DateTimeOriginal"): timestamp = value
        lat = lon = None
        if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
            def dms(d,r):
                v = float(d[0])+float(d[1])/60+float(d[2])/3600
                return -v if r in ("S","W") else v
            lat = round(dms(gps_info["GPSLatitude"],gps_info.get("GPSLatitudeRef","N")),6)
            lon = round(dms(gps_info["GPSLongitude"],gps_info.get("GPSLongitudeRef","E")),6)
        return lat, lon, timestamp
    except: return None, None, None

def call_claude(prompt, tone):
    tones = {"Professional":"Formal, authoritative, data-driven.","Hype":"Bold, energetic, motivating.","Friendly":"Warm, conversational, encouraging."}
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    msg = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=1800,
        system=f"You are GMB Dominator, a Google Business Profile SEO expert. Tone: {tones.get(tone,tones['Professional'])} Use markdown headers.",
        messages=[{"role":"user","content":prompt}])
    return msg.content[0].text

def send_webhook(email, phone, biz, report):
    url = st.secrets.get("MAKE_WEBHOOK_URL","")
    if not url: return False
    try: return requests.post(url,json={"email":email,"phone":phone,"business_name":biz,"report_preview":report[:500],"timestamp":datetime.now().isoformat()},timeout=5).status_code==200
    except: return False

def sidebar_roadmap(n):
    steps = [("Access Unlocked",True),("Business Info Entered",n>=1),("Photo Scanned",n>=2),("Strategy Generated",n>=3),("Report Delivered",n>=4)]
    st.sidebar.markdown("### 🗺️ Your SEO Roadmap")
    for label,done in steps:
        icon="✅" if done else "⬜"; color="#ff6b00" if done else "#aaa"
        st.sidebar.markdown(f'<div style="padding:6px 0;border-bottom:1px solid #eee;font-size:0.88rem;color:{color}">{icon} {label}</div>',unsafe_allow_html=True)

for k,v in [("authenticated",False),("steps_done",0),("report",{}),("scan_result",None)]:
    if k not in st.session_state: st.session_state[k]=v

st.markdown('<div class="gmb-hero"><h1>GMB DOMINATOR</h1><div class="tagline">Rank #1 on Google Maps — No Agency Required</div></div>',unsafe_allow_html=True)

if not st.session_state.authenticated:
    sidebar_roadmap(0)
    _,col,_ = st.columns([1,2,1])
    with col:
        st.markdown('<div class="gate-card">',unsafe_allow_html=True)
        st.markdown("### 🔐 Enter Your Access Code")
        st.markdown('<div style="color:#888;font-size:0.9rem;margin-bottom:1rem;">Purchased your access? Enter the code from your receipt below.</div>',unsafe_allow_html=True)
        code = st.text_input("Access Code",type="password",placeholder="e.g. GROW2026")
        if st.button("Unlock GMB Dominator →"):
            if code.strip().upper()==ACCESS_CODE:
                st.session_state.authenticated=True; st.session_state.steps_done=1; st.rerun()
            else: st.error("❌ Invalid code. Purchase access to get your code.")
        st.markdown("---")
        st.markdown('<div style="font-size:0.8rem;color:#aaa;">Don\'t have a code? <a href="#" style="color:#ff6b00;">Purchase Access →</a></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    st.stop()

sidebar_roadmap(st.session_state.steps_done)
st.sidebar.markdown("---")
st.sidebar.markdown("### ❓ FAQ")
with st.sidebar.expander("Why GPS in photos?"): st.write("Google uses photo metadata to verify location. GPS photos boost local ranking.")
with st.sidebar.expander("How to turn on Location Services?"): st.write("**iPhone:** Settings → Privacy → Location Services → Camera → While Using\n\n**Android:** Camera → Settings → Location tags → ON")
with st.sidebar.expander("Monthly subscription?"): st.write("No! Lifetime access. No retainers.")
with st.sidebar.expander("Do you manage my profile?"): st.write("No. Self-serve tool. You implement the advice.")

left,right = st.columns([3,2],gap="large")

with left:
    st.markdown('<div class="section-badge">Step 1</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-title">Your Business Info</div>',unsafe_allow_html=True)
    biz_name = st.text_input("Business Name",placeholder="e.g. Mike's Auto Repair")
    biz_category = st.text_input("Primary Category",placeholder="e.g. Auto Repair Shop")
    biz_city = st.text_input("City / Service Area",placeholder="e.g. Austin, TX")
    competitor = st.text_input("Top Competitor (for Gap Analysis)",placeholder="e.g. Joe's Garage")
    tone = st.selectbox("Brand Vibe 🎭",["Professional","Hype","Friendly"])
    st.markdown("---")

    st.markdown('<div class="section-badge">Step 2</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-title">📸 EXIF Metadata Scanner</div>',unsafe_allow_html=True)
    st.markdown('<div style="color:#888;font-size:0.88rem;margin-bottom:1rem;">Upload a JPEG photo you plan to post on your Google Business Profile.</div>',unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload JPEG Photo",type=["jpg","jpeg"])
    if uploaded:
        lat,lon,ts = extract_exif(uploaded.read())
        if lat and lon:
            st.markdown(f'<div class="scan-ready">✅ <strong>SEO-Ready!</strong> GPS detected: {lat}, {lon}<br><small>Timestamp: {ts or "Not found"}</small></div>',unsafe_allow_html=True)
            st.session_state.scan_result={"status":"ready","lat":lat,"lon":lon,"ts":ts}
        elif ts:
            st.markdown(f'<div class="scan-neutral">⚠️ <strong>Partial.</strong> Timestamp found but GPS missing.<br><small>Retake with Location Services ON.</small></div>',unsafe_allow_html=True)
            st.session_state.scan_result={"status":"partial","ts":ts}
        else:
            st.markdown('<div class="scan-missing">❌ <strong>Missing Tags.</strong> No GPS or timestamp.<br><small>Retake with Location Services ON.</small></div>',unsafe_allow_html=True)
            st.session_state.scan_result={"status":"missing"}
        st.session_state.steps_done=max(st.session_state.steps_done,2)
    st.markdown("---")

    st.markdown('<div class="section-badge">Step 3</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚀 Generate Your Strategy</div>',unsafe_allow_html=True)
    if st.button("⚡ Generate 3-Tier GMB Strategy"):
        if not biz_name or not biz_category: st.warning("Please fill in Business Name and Category first.")
        else:
            scan=st.session_state.scan_result
            pc="No photo uploaded."
            if scan:
                if scan["status"]=="ready": pc=f"GPS found at {scan.get('lat')},{scan.get('lon')}. Timestamp:{scan.get('ts')}."
                elif scan["status"]=="partial": pc=f"Timestamp found ({scan.get('ts')}) but GPS missing."
                else: pc="No GPS or timestamp found."
            prompt=f"""Business: {biz_name}\nCategory: {biz_category}\nLocation: {biz_city or 'Not specified'}\nCompetitor: {competitor or 'None'}\nPhoto: {pc}\n\nGenerate a 3-Tier GMB Strategy:\n\n## TIER 1 — FOUNDATION\n- 1 primary + 3 secondary GMB categories\n- 750-char keyword-rich business description\n- 5 must-have profile attributes\n\n## TIER 2 — VISUAL STRATEGY\n- Photo advice based on scan result\n- Photo types and posting cadence\n- Geotagging and file naming tips\n\n## TIER 3 — COMPETITIVE GAP ANALYSIS\n- {"Compare vs: "+competitor if competitor else "General competitive positioning"}\n- 3 gaps to exploit\n- 3 quick wins this week\n\nEnd with Priority Action List — top 5 tasks for next 7 days."""
            with st.spinner("Building your strategy..."):
                try:
                    report=call_claude(prompt,tone)
                    st.session_state.report["strategy"]=report
                    st.session_state.steps_done=max(st.session_state.steps_done,3)
                    st.success("✅ Strategy ready! See results on the right →")
                except Exception as e: st.error(f"API error: {e}")

    st.markdown('<div class="lead-card">',unsafe_allow_html=True)
    st.markdown("### 📬 Get Your Report via Email & SMS")
    lead_email=st.text_input("Email Address",placeholder="you@yourbusiness.com")
    lead_phone=st.text_input("Mobile Number",placeholder="+1 555-000-0000")
    if st.button("📨 Send Report to My Inbox"):
        if not lead_email: st.warning("Please enter your email.")
        elif not st.session_state.report.get("strategy"): st.warning("Generate your strategy first!")
        else:
            if send_webhook(lead_email,lead_phone,biz_name,st.session_state.report.get("strategy","")):
                st.success("✅ Sent!"); st.session_state.steps_done=max(st.session_state.steps_done,4)
            else: st.info("Webhook not configured. Copy your report from the right panel.")
    st.markdown('</div>',unsafe_allow_html=True)

with right:
    st.markdown('<div class="section-badge">Your Report</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-title">3-Tier Strategy Engine</div>',unsafe_allow_html=True)
    if st.session_state.report.get("strategy"):
        rt=st.session_state.report["strategy"]
        with st.expander("📋 Full Strategy Report",expanded=True): st.markdown(rt)
        st.download_button("⬇️ Download Report",data=rt,file_name=f"GMB_{biz_name.replace(' ','_')}.txt",mime="text/plain")
    else:
        st.markdown('<div style="background:#fff;border:1px dashed #ddd;border-radius:14px;padding:3rem 2rem;text-align:center;"><div style="font-size:3rem">🗺️</div><div style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;color:#ccc">Your strategy will appear here</div><div style="font-size:0.85rem;color:#ddd;margin-top:0.5rem">Fill in your business info and click Generate</div></div>',unsafe_allow_html=True)
    st.markdown("<br>",unsafe_allow_html=True)
    done=bool(st.session_state.report.get("strategy"))
    for cls,lbl,title,color in [("tier-1","TIER 1","🏗️ Foundation: Categories & Bio","#ff6b00"),("tier-2","TIER 2","📸 Visual: Photo Strategy","#00b4d8"),("tier-3","TIER 3","⚔️ Competitive: Gap Analysis","#7b2fff")]:
        st.markdown(f'<div class="tier-card {cls}"><div class="tier-label" style="color:{color}">{lbl}</div><div class="tier-title">{title}</div><div style="color:#aaa;font-size:0.85rem">{"✓ Included in your report above." if done else "Generated content will appear in the report above."}</div></div>',unsafe_allow_html=True)

st.markdown('<div class="disclaimer"><strong>⚖️ Disclaimer:</strong> GMB Dominator is an informational, self-serve advisory tool. AI-generated recommendations for educational purposes only. Not affiliated with Google LLC. All implementation is your sole responsibility.</div>',unsafe_allow_html=True)
