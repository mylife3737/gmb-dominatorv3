import streamlit as st
import anthropic
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import io
import requests
import json
from datetime import datetime

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GMB Dominator",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0f;
    color: #e8e4dc;
}

/* ── Gradient background noise effect ── */
body::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 20% 10%, rgba(255,107,0,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 80%, rgba(0,200,120,0.06) 0%, transparent 60%);
    pointer-events: none;
    z-index: 0;
}

/* ── Headings ── */
h1, h2, h3, h4 {
    font-family: 'Syne', sans-serif !important;
    letter-spacing: -0.02em;
}

/* ── Hero Title ── */
.gmb-hero {
    text-align: center;
    padding: 2.5rem 0 1.5rem;
}
.gmb-hero h1 {
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ff6b00 0%, #ff9500 50%, #ffd000 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    line-height: 1.1;
}
.gmb-hero .tagline {
    font-size: 1.05rem;
    color: #8a8a9a;
    margin-top: 0.5rem;
    font-weight: 300;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* ── Gate card ── */
.gate-card {
    background: linear-gradient(135deg, #13131a 0%, #1a1a28 100%);
    border: 1px solid #2a2a3a;
    border-radius: 16px;
    padding: 2.5rem;
    max-width: 480px;
    margin: 2rem auto;
    box-shadow: 0 25px 60px rgba(0,0,0,0.5);
}

/* ── Section headers ── */
.section-badge {
    display: inline-block;
    background: rgba(255,107,0,0.12);
    border: 1px solid rgba(255,107,0,0.3);
    color: #ff6b00;
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 20px;
    margin-bottom: 0.5rem;
}
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    margin: 0 0 1.2rem;
}

/* ── Scan result boxes ── */
.scan-ready {
    background: rgba(0,200,100,0.08);
    border: 1px solid rgba(0,200,100,0.3);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    color: #00c864;
    font-weight: 500;
}
.scan-missing {
    background: rgba(255,60,60,0.08);
    border: 1px solid rgba(255,60,60,0.3);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    color: #ff4444;
    font-weight: 500;
}
.scan-neutral {
    background: rgba(255,200,0,0.08);
    border: 1px solid rgba(255,200,0,0.3);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    color: #ffc800;
    font-weight: 500;
}

/* ── Tier cards ── */
.tier-card {
    background: #13131a;
    border: 1px solid #242430;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}
.tier-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.tier-1::before { background: linear-gradient(90deg, #ff6b00, #ff9500); }
.tier-2::before { background: linear-gradient(90deg, #00b4d8, #0077b6); }
.tier-3::before { background: linear-gradient(90deg, #7b2fff, #c44fff); }

.tier-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    opacity: 0.5;
    margin-bottom: 0.3rem;
}
.tier-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    margin-bottom: 0.8rem;
}

/* ── Sidebar checklist ── */
.checklist-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.5rem 0;
    font-size: 0.88rem;
    border-bottom: 1px solid #1e1e2a;
}
.check-done { color: #00c864; }
.check-pending { color: #4a4a5a; }

/* ── Streamlit overrides ── */
.stTextInput > div > div > input,
.stTextArea textarea {
    background: #13131a !important;
    border: 1px solid #2a2a3a !important;
    color: #e8e4dc !important;
    border-radius: 8px !important;
}
.stSelectbox > div > div {
    background: #13131a !important;
    border: 1px solid #2a2a3a !important;
    border-radius: 8px !important;
    color: #e8e4dc !important;
}
.stButton > button {
    background: linear-gradient(135deg, #ff6b00, #ff9500) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 20px rgba(255,107,0,0.3) !important;
}
.stFileUploader {
    background: #13131a !important;
    border: 1px dashed #2a2a3a !important;
    border-radius: 10px !important;
}
[data-testid="stSidebar"] {
    background: #0e0e15 !important;
    border-right: 1px solid #1e1e2a !important;
}

/* ── Disclaimer ── */
.disclaimer {
    background: #0f0f18;
    border: 1px solid #1e1e28;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-size: 0.8rem;
    color: #555568;
    margin-top: 2rem;
}
.disclaimer strong { color: #8888aa; }

/* ── Lead magnet card ── */
.lead-card {
    background: linear-gradient(135deg, #13131a 0%, #1c1230 100%);
    border: 1px solid #2a2040;
    border-radius: 14px;
    padding: 1.5rem;
    margin-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
ACCESS_CODE = "GROW2026"

def extract_exif(image_bytes):
    """Extract GPS and timestamp from JPEG EXIF data."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        exif_data = img._getexif()
        if not exif_data:
            return None, None, None

        gps_info = {}
        timestamp = None

        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            if tag == "GPSInfo":
                for gps_tag_id, gps_value in value.items():
                    gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_info[gps_tag] = gps_value
            elif tag in ("DateTime", "DateTimeOriginal"):
                timestamp = value

        lat = lon = None
        if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
            def dms_to_dd(dms, ref):
                d, m, s = [float(x) for x in dms]
                dd = d + m / 60 + s / 3600
                if ref in ("S", "W"):
                    dd = -dd
                return round(dd, 6)
            lat = dms_to_dd(gps_info["GPSLatitude"], gps_info.get("GPSLatitudeRef", "N"))
            lon = dms_to_dd(gps_info["GPSLongitude"], gps_info.get("GPSLongitudeRef", "E"))

        return lat, lon, timestamp
    except Exception:
        return None, None, None


def call_claude(prompt: str, tone: str) -> str:
    """Call Claude claude-sonnet-4-20250514 with the given prompt."""
    tone_instructions = {
        "Professional": "Use formal, authoritative language. Be concise, data-driven, and business-focused.",
        "Hype": "Use bold, energetic language with power words. Be exciting and motivating. Use emphasis strategically.",
        "Friendly": "Use warm, conversational language. Be encouraging, use simple words, and feel like a helpful friend.",
    }
    system = f"""You are GMB Dominator, a Google Business Profile SEO expert helping small business owners rank higher on Google Maps.
Tone: {tone_instructions.get(tone, tone_instructions['Professional'])}
Format your response in clear sections using markdown. Be specific, actionable, and practical.
Always return structured advice with clear headings."""

    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1800,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text


def send_webhook(email, phone, business_name, report_text):
    """Send lead data to Make.com webhook."""
    webhook_url = st.secrets.get("MAKE_WEBHOOK_URL", "")
    if not webhook_url:
        return False
    payload = {
        "email": email,
        "phone": phone,
        "business_name": business_name,
        "report_preview": report_text[:500],
        "timestamp": datetime.now().isoformat(),
    }
    try:
        r = requests.post(webhook_url, json=payload, timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def sidebar_roadmap(steps_done):
    """Render the progress roadmap in the sidebar."""
    steps = [
        ("Access Unlocked", True),
        ("Business Info Entered", steps_done >= 1),
        ("Photo Scanned", steps_done >= 2),
        ("Strategy Generated", steps_done >= 3),
        ("Report Delivered", steps_done >= 4),
    ]
    st.sidebar.markdown("### 🗺️ Your SEO Roadmap")
    for label, done in steps:
        icon = "✅" if done else "⬜"
        color = "#00c864" if done else "#444458"
        st.sidebar.markdown(
            f'<div class="checklist-item"><span style="color:{color}">{icon}</span> <span style="color:{color}">{label}</span></div>',
            unsafe_allow_html=True,
        )
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        '<div style="font-size:0.75rem;color:#555568;margin-top:0.5rem;">Complete each step to maximize your GMB ranking.</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "steps_done" not in st.session_state:
    st.session_state.steps_done = 0
if "report" not in st.session_state:
    st.session_state.report = {}
if "scan_result" not in st.session_state:
    st.session_state.scan_result = None

# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="gmb-hero">
    <h1>GMB DOMINATOR</h1>
    <div class="tagline">Rank #1 on Google Maps — No Agency Required</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# GATE: PASSWORD SCREEN
# ─────────────────────────────────────────────
if not st.session_state.authenticated:
    sidebar_roadmap(0)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="gate-card">', unsafe_allow_html=True)
        st.markdown("### 🔐 Enter Your Access Code")
        st.markdown('<div style="color:#6a6a7a;font-size:0.9rem;margin-bottom:1rem;">Purchased your access? Enter the code from your receipt below.</div>', unsafe_allow_html=True)
        code_input = st.text_input("Access Code", type="password", placeholder="e.g. GROW2026")
        if st.button("Unlock GMB Dominator →"):
            if code_input.strip().upper() == ACCESS_CODE:
                st.session_state.authenticated = True
                st.session_state.steps_done = 1
                st.rerun()
            else:
                st.error("❌ Invalid code. Purchase access to get your code.")
        st.markdown("---")
        st.markdown('<div style="font-size:0.8rem;color:#4a4a5a;">Don\'t have a code? <a href="#" style="color:#ff6b00;">Purchase Access →</a></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────
# MAIN APP (Authenticated)
# ─────────────────────────────────────────────
sidebar_roadmap(st.session_state.steps_done)

st.sidebar.markdown("---")
st.sidebar.markdown("### ❓ FAQ")
with st.sidebar.expander("Why do I need GPS in photos?"):
    st.write("Google uses photo metadata to verify your location. Photos taken with Location Services ON signal authenticity and boost your local ranking.")
with st.sidebar.expander("How do I turn on Location Services?"):
    st.write("**iPhone:** Settings → Privacy → Location Services → Camera → 'While Using'\n\n**Android:** Camera app → Settings → Location tags → ON")
with st.sidebar.expander("Is this a monthly subscription?"):
    st.write("No! You paid for lifetime access to this self-serve tool. No retainers, no ongoing fees.")
with st.sidebar.expander("Do you manage my GMB profile?"):
    st.write("No. This is a self-serve advisory tool. You implement the recommendations yourself.")

# ── COLUMNS LAYOUT ──
left, right = st.columns([3, 2], gap="large")

# ─────────────────────────────────────────────
# LEFT COLUMN: INPUTS
# ─────────────────────────────────────────────
with left:
    # ── Section 1: Business Info ──
    st.markdown('<div class="section-badge">Step 1</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Your Business Info</div>', unsafe_allow_html=True)

    biz_name = st.text_input("Business Name", placeholder="e.g. Mike's Auto Repair")
    biz_category = st.text_input("Primary Category", placeholder="e.g. Auto Repair Shop")
    biz_city = st.text_input("City / Service Area", placeholder="e.g. Austin, TX")
    competitor = st.text_input("Top Competitor Name (for Gap Analysis)", placeholder="e.g. Joe's Garage")

    tone = st.selectbox(
        "Brand Vibe 🎭",
        ["Professional", "Hype", "Friendly"],
        help="Choose how you want the advice to sound."
    )

    st.markdown("---")
    # ── Section 2: Photo Scanner ──
    st.markdown('<div class="section-badge">Step 2</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📸 EXIF Metadata Scanner</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#7a7a8a;font-size:0.88rem;margin-bottom:1rem;">Upload a JPEG photo you plan to post on your Google Business Profile.</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload JPEG Photo", type=["jpg", "jpeg"])

    if uploaded:
        img_bytes = uploaded.read()
        lat, lon, timestamp = extract_exif(img_bytes)

        if lat and lon:
            st.markdown(f'<div class="scan-ready">✅ <strong>SEO-Ready!</strong> GPS coordinates detected: {lat}, {lon}<br><small style="opacity:0.7;">Timestamp: {timestamp or "Not found"}</small></div>', unsafe_allow_html=True)
            st.session_state.scan_result = {"status": "ready", "lat": lat, "lon": lon, "ts": timestamp}
        elif timestamp:
            st.markdown(f'<div class="scan-neutral">⚠️ <strong>Partial Data.</strong> Timestamp found ({timestamp}) but GPS is missing.<br><small>Take a new photo with Location Services ON for full SEO credit.</small></div>', unsafe_allow_html=True)
            st.session_state.scan_result = {"status": "partial", "ts": timestamp}
        else:
            st.markdown('<div class="scan-missing">❌ <strong>Missing Tags.</strong> No GPS or timestamp detected.<br><small>Take a new photo with Location Services ON on your smartphone.</small></div>', unsafe_allow_html=True)
            st.session_state.scan_result = {"status": "missing"}

        st.session_state.steps_done = max(st.session_state.steps_done, 2)

    st.markdown("---")
    # ── Section 3: Generate ──
    st.markdown('<div class="section-badge">Step 3</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚀 Generate Your Strategy</div>', unsafe_allow_html=True)

    if st.button("⚡ Generate 3-Tier GMB Strategy"):
        if not biz_name or not biz_category:
            st.warning("Please fill in your Business Name and Category first.")
        else:
            scan = st.session_state.scan_result
            photo_context = "No photo was uploaded."
            if scan:
                if scan["status"] == "ready":
                    photo_context = f"Photo scan: ✅ GPS found at {scan.get('lat')}, {scan.get('lon')}. Timestamp: {scan.get('ts')}. Photo is SEO-ready."
                elif scan["status"] == "partial":
                    photo_context = f"Photo scan: ⚠️ Timestamp found ({scan.get('ts')}) but GPS is missing. User needs to retake with Location Services ON."
                else:
                    photo_context = "Photo scan: ❌ No GPS or timestamp. User needs to retake photos with Location Services ON."

            prompt = f"""
Business: {biz_name}
Category: {biz_category}
Location: {biz_city or 'Not specified'}
Competitor to beat: {competitor or 'None specified'}
Photo scan result: {photo_context}

Generate a 3-Tier GMB Dominator Strategy Report:

## TIER 1 — FOUNDATION
- Recommend 1 primary + 3 secondary Google Business Profile categories
- Write a 750-character keyword-rich business description/bio
- List 5 must-have attributes to enable on their profile

## TIER 2 — VISUAL STRATEGY
- Based on the photo scan result above, give specific advice on photo optimization
- Recommend photo types (interior, exterior, team, product) with posting cadence
- Tips for geotagging and naming convention for image files

## TIER 3 — COMPETITIVE GAP ANALYSIS
- {"Compare against competitor: " + competitor if competitor else "Provide general competitive positioning advice since no competitor was named"}
- Identify 3 specific gaps to exploit
- Give 3 quick wins the user can implement this week to outrank the competition

End with a "Priority Action List" — the top 5 tasks to complete in the next 7 days.
"""
            with st.spinner("Analyzing your profile and building your strategy..."):
                try:
                    report = call_claude(prompt, tone)
                    st.session_state.report["strategy"] = report
                    st.session_state.steps_done = max(st.session_state.steps_done, 3)
                    st.success("✅ Strategy generated! See results on the right →")
                except Exception as e:
                    st.error(f"API error: {e}")

    # ── Lead Magnet ──
    st.markdown('<div class="lead-card">', unsafe_allow_html=True)
    st.markdown("### 📬 Get Your Report via Email & SMS")
    st.markdown('<div style="color:#7a7a8a;font-size:0.88rem;margin-bottom:1rem;">Enter your details to receive a link to your personalized report.</div>', unsafe_allow_html=True)
    lead_email = st.text_input("Email Address", placeholder="you@yourbusiness.com")
    lead_phone = st.text_input("Mobile Number (for SMS)", placeholder="+1 555-000-0000")
    if st.button("📨 Send Report to My Inbox"):
        if not lead_email:
            st.warning("Please enter your email address.")
        elif not st.session_state.report.get("strategy"):
            st.warning("Generate your strategy first (Step 3)!")
        else:
            success = send_webhook(lead_email, lead_phone, biz_name, st.session_state.report.get("strategy", ""))
            if success:
                st.success("✅ Sent! Check your email shortly.")
                st.session_state.steps_done = max(st.session_state.steps_done, 4)
            else:
                st.info("Webhook not configured. Copy your report from the right panel.")
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# RIGHT COLUMN: RESULTS
# ─────────────────────────────────────────────
with right:
    st.markdown('<div class="section-badge">Your Report</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">3-Tier Strategy Engine</div>', unsafe_allow_html=True)

    if st.session_state.report.get("strategy"):
        report_text = st.session_state.report["strategy"]

        # Split into tiers for styled display
        tier_configs = [
            ("tier-1", "TIER 1", "🏗️ Foundation", "#ff6b00"),
            ("tier-2", "TIER 2", "📸 Visual Strategy", "#00b4d8"),
            ("tier-3", "TIER 3", "⚔️ Competitive Gap Analysis", "#7b2fff"),
        ]

        # Display raw report in an expander, styled tiers as summary
        with st.expander("📋 Full Strategy Report (Copy & Save)", expanded=True):
            st.markdown(report_text)

        st.download_button(
            label="⬇️ Download Report as .txt",
            data=report_text,
            file_name=f"GMB_Strategy_{biz_name.replace(' ','_')}.txt",
            mime="text/plain",
        )
    else:
        # Empty state
        st.markdown("""
<div style="
    background:#13131a;
    border:1px dashed #2a2a3a;
    border-radius:14px;
    padding:3rem 2rem;
    text-align:center;
    color:#3a3a4a;
">
    <div style="font-size:3rem;margin-bottom:1rem;">🗺️</div>
    <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;color:#4a4a5a;">Your strategy will appear here</div>
    <div style="font-size:0.85rem;margin-top:0.5rem;">Fill in your business info and click Generate →</div>
</div>
""", unsafe_allow_html=True)

    # ── Tier Preview Cards (always visible as template) ──
    st.markdown("<br>", unsafe_allow_html=True)
    for cls, tier_label, tier_title, color in [
        ("tier-1", "TIER 1", "🏗️ Foundation: Categories & Bio", "#ff6b00"),
        ("tier-2", "TIER 2", "📸 Visual: Photo Strategy", "#00b4d8"),
        ("tier-3", "TIER 3", "⚔️ Competitive: Gap Analysis", "#7b2fff"),
    ]:
        st.markdown(f"""
<div class="tier-card {cls}">
    <div class="tier-label" style="color:{color}">{tier_label}</div>
    <div class="tier-title">{tier_title}</div>
    <div style="color:#5a5a6a;font-size:0.85rem;">{"Generated content will appear in the report above." if not st.session_state.report.get("strategy") else "✓ Included in your report above."}</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DISCLAIMER
# ─────────────────────────────────────────────
st.markdown("""
<div class="disclaimer">
    <strong>⚖️ Disclaimer & Terms of Use</strong><br>
    GMB Dominator is an <strong>informational, self-serve advisory tool</strong>. All recommendations are generated by AI and are for educational purposes only. This tool does not access, manage, or modify your Google Business Profile. Results may vary. We are not affiliated with Google LLC. By using this tool, you agree that all implementation is your sole responsibility. This is not a substitute for professional marketing consultation.
</div>
""", unsafe_allow_html=True)
