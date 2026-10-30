
import streamlit as st
import json
from datetime import datetime
from google import genai

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="SalesPilot AI",
    page_icon="🎯",
    layout="wide"
)

st.markdown("""
<style>
.main {
    background-color: #f7f9fc;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}
.hero {
    padding: 25px;
    border-radius: 16px;
    background: linear-gradient(120deg, #10233f, #245b88);
    color: white;
    margin-bottom: 25px;
}
.hero h1 {
    color: white;
    font-size: 36px;
}
.hero p {
    color: #dce8f5;
}
div[data-testid="stMetric"] {
    background: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #e5eaf0;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# AI CONNECTION
# --------------------------------------------------

def get_ai_client():
    api_key = st.secrets.get("GEMINI_API_KEY", "")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)


# --------------------------------------------------
# SESSION STORAGE
# --------------------------------------------------

if "leads" not in st.session_state:
    st.session_state.leads = []

if "analysis" not in st.session_state:
    st.session_state.analysis = None


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown("""
<div class="hero">
    <h1>🎯 SalesPilot AI</h1>
    <p>Your AI-powered B2B sales intelligence
    and lead qualification assistant.</p>
    <p>Discover opportunities. Qualify prospects.
    Create smarter sales conversations.</p>
</div>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.title("SalesPilot")
    st.caption("AI Sales Agent | Version 1.0")

    page = st.radio(
        "Workspace",
        [
            "Lead Qualification",
            "Lead Pipeline",
            "About"
        ]
    )

    st.divider()

    st.metric(
        "Total Leads",
        len(st.session_state.leads)
    )

    st.caption("AI analysis requires a Gemini API key.")


# --------------------------------------------------
# AI ANALYSIS FUNCTION
# --------------------------------------------------

def analyze_lead(data):

    client = get_ai_client()

    if client is None:
        st.error(
            "Gemini API key missing. "
            "Please configure Streamlit Secrets."
        )
        return None

    prompt = f"""
You are SalesPilot, an experienced B2B sales strategist.

Your task is to evaluate a prospective customer.

OUR BUSINESS:
Product/service: {data['product']}
Ideal customer: {data['ideal_customer']}
Value proposition: {data['value_proposition']}

PROSPECT:
Company: {data['company']}
Industry: {data['industry']}
Location: {data['location']}
Website: {data['website']}
Contact role: {data['role']}
Additional information: {data['notes']}

IMPORTANT RULES:
1. Do not pretend you visited or researched the website.
2. Do not invent company revenue, employee numbers,
   buying intent or contact information.
3. Separate supplied facts from assumptions.
4. If information is insufficient, say so.
5. Score the lead based on available evidence.
6. Explain the reasons behind the score.
7. Be commercially realistic, not overly optimistic.
8. Do not recommend contacting people through
   deceptive or unsolicited bulk messaging.

Provide your response in these sections:

# LEAD QUALIFICATION

Lead score: X/100

Category: HOT / WARM / COLD / INSUFFICIENT DATA

# WHY THIS LEAD SCORES THIS WAY

Explain the score using:
- Industry relevance
- Customer profile fit
- Potential business need
- Available evidence
- Missing information

# POTENTIAL CUSTOMER PAIN POINTS

List up to five plausible problems.
Clearly mark assumptions.

# SALES STRATEGY

Explain how we should approach this company.

# PERSONALIZED INTRODUCTORY EMAIL

Write a professional, concise B2B email.

# WHATSAPP DRAFT

Write a short, respectful business introduction.
Do not imply prior consent or an existing relationship.

# NEXT BEST ACTION

Give the three most useful actions to take.

# INFORMATION GAPS

List what we need to verify before investing
more sales effort.
"""

    try:
        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents=prompt
        )

        return response.text

    except Exception as e:
        st.error(f"AI analysis failed: {str(e)}")
        return None


# --------------------------------------------------
# PAGE 1: LEAD QUALIFICATION
# --------------------------------------------------

if page == "Lead Qualification":

    st.title("AI Lead Qualification")
    st.write(
        "Evaluate a potential customer and generate "
        "a personalized sales strategy."
    )

    with st.form("lead_form"):

        st.subheader("A. Your business")

        product = st.text_input(
            "What are you selling?",
            placeholder="Example: B2B software for logistics companies"
        )

        ideal_customer = st.text_area(
            "Describe your ideal customer",
            placeholder="Example: Indian logistics companies with 50+ employees"
        )

        value_proposition = st.text_area(
            "Why should customers buy from you?",
            placeholder="Example: Reduce manual work and operational costs"
        )

        st.divider()

        st.subheader("B. Prospective customer")

        company = st.text_input(
            "Company name"
        )

        col1, col2 = st.columns(2)

        with col1:
            industry = st.text_input(
                "Industry"
            )

            location = st.text_input(
                "Location",
                placeholder="Bengaluru, India"
            )

        with col2:
            website = st.text_input(
                "Company website"
            )

            role = st.text_input(
                "Contact person's designation",
                placeholder="Founder / CEO / Procurement Manager"
            )

        notes = st.text_area(
            "Additional information",
            placeholder="Anything you know about this prospect..."
        )

        submitted = st.form_submit_button(
            "✨ Analyze Prospect with AI",
            use_container_width=True
        )

    if submitted:

        if not all([
            product,
            ideal_customer,
            company,
            industry
        ]):
            st.warning(
                "Please complete the product, "
                "ideal customer, company and industry fields."
            )

        else:

            lead_data = {
                "product": product,
                "ideal_customer": ideal_customer,
                "value_proposition": value_proposition,
                "company": company,
                "industry": industry,
                "location": location,
                "website": website,
                "role": role,
                "notes": notes
            }

            with st.spinner(
                "SalesPilot AI is evaluating your prospect..."
            ):

                result = analyze_lead(lead_data)

            if result:

                st.session_state.analysis = result

                st.session_state.leads.append({
                    "company": company,
                    "industry": industry,
                    "location": location,
                    "date": datetime.now().strftime(
                        "%d-%m-%Y %H:%M"
                    ),
                    "analysis": result
                })

                st.success(
                    "Lead qualification completed!"
                )

    if st.session_state.analysis:

        st.divider()

        st.subheader("AI Sales Intelligence Report")

        st.markdown(
            st.session_state.analysis
        )

        st.download_button(
            "Download Sales Report",
            data=st.session_state.analysis,
            file_name="salespilot_lead_report.txt",
            mime="text/plain"
        )


# --------------------------------------------------
# PAGE 2: LEAD PIPELINE
# --------------------------------------------------

elif page == "Lead Pipeline":

    st.title("Lead Pipeline")

    leads = st.session_state.leads

    if not leads:
        st.info(
            "No leads yet. Analyze your first prospect "
            "to populate this pipeline."
        )

    else:

        st.metric(
            "Prospects Analyzed",
            len(leads)
        )

        for index, lead in enumerate(reversed(leads)):

            with st.expander(
                f"{lead['company']} | {lead['industry']}"
            ):

                st.caption(
                    f"Location: {lead['location']} | "
                    f"Analyzed: {lead['date']}"
                )

                st.markdown(lead["analysis"])


# --------------------------------------------------
# PAGE 3: ABOUT
# --------------------------------------------------

elif page == "About":

    st.title("About SalesPilot AI")

    st.write("""
    SalesPilot is an AI-powered sales intelligence
    platform designed to help businesses:

    - Qualify prospective customers.
    - Understand potential customer needs.
    - Create personalized sales communication.
    - Prioritize sales opportunities.
    - Improve sales productivity.

    Current version: 1.0

    Current capability: AI lead qualification
    and sales strategy generation.

    This version does not independently discover,
    verify or contact prospects.
    """)

    st.info(
        "SalesPilot is an evolving software prototype. "
        "AI-generated assessments require human verification."
    )
