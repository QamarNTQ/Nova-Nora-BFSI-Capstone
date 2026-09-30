import os

import requests
import streamlit as st

claim_types =     [
        "Accidental Damage & Crash Collision (Vehicles, Rail, Hangar)",
        "Theft, Burglary, and Housebreaking (Property, Fleet, Contents)",
        "Fire, Thermal Explosion, and Wiring Short-Circuit (Data Center, Substation)",
        "Natural Calamities & Environmental Acts of God (AOG, Floods, Tidal Surge)",
        "Third-Party Liability (Property Damage, Bodily Injury, Transit Hazards)",
        "Cargo Asset Loss & Emergency Roadside Towing Breakdown",
        "Inpatient Hospitalization & Day Care Procedures (Health, Geriatric Care)",
        "Critical Illness, Cancer Oncological Care, and Radiation Benefits",
        "Structural Building Failure & Foundation Collapse (Masonry, Scour Rock)",
        "Electrical Grid Surge, Overvoltage, and Electromagnetic Failure (PDU, Avionics)",
        "Mechanical Pipe Rupture, Vacuum Collapse, and Liquid Leaks (Cryogenic, UPW)",
        "Kinetic Asset Impact & Aerodynamic Delamination (Micrometeorite, Blade, Rail)"
    ]


BACKEND_URL = "http://127.0.0.1:8000"
if not BACKEND_URL.endswith("/"):
    BACKEND_URL = BACKEND_URL + "/"

st.set_page_config(page_title="Claims Processing Assistant", page_icon="BFSI", layout="wide")
st.title("Claims Processing Assistant")

if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "submitted_claim" not in st.session_state:
    st.session_state.submitted_claim = None

with st.form("claim_form"):
    st.subheader("Claim Form")

    col1, col2 = st.columns(2)
    with col1:
        customer_id = st.text_input("Customer ID", value="C014")
        policy_id = st.text_input("Policy ID", value="P014")
        claim_type = st.selectbox("Claim Type", claim_types)

    with col2:
        claim_amount = st.number_input("Claim Amount", min_value=0.0, step=1000.0, value=180000.0)
        claim_description = st.text_area("Claim Description", value="Vehicle damage due to accident on highway")

    submitted = st.form_submit_button("Submit Claim")

if submitted:
    payload = {
        "customer_id": customer_id,
        "policy_id": policy_id,
        "claim_type": claim_type,
        "claim_amount": float(claim_amount),
        "claim_description": claim_description,
    }

    try:
        response = requests.post(f"{BACKEND_URL}claim-processor/check-claim", json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        st.session_state.submitted_claim = payload
        st.session_state.last_result = data
        st.session_state.chat_history = []
        st.success("Claim submitted successfully.")
    except Exception as exc:
        st.error(f"Claim submission failed: {exc}")
        st.session_state.last_result = None
        st.session_state.submitted_claim = None

if st.session_state.last_result:
    result = st.session_state.last_result
    st.subheader("Claim Evaluation Result")

    cleaned_result = result.copy()
    cleaned_result.pop("session_id", None)
    st.json(cleaned_result)

    st.subheader("Follow-up Chat")

    for item in st.session_state.chat_history:
        with st.chat_message(item["role"]):
            st.write(item["content"])

    question = st.chat_input("Ask a follow-up question about this claim...")

    if question:
        try:
            claim_context = {
                "session_id": result["session_id"],
                "question": question,
                "customer_id": st.session_state.submitted_claim['customer_id']
            }

            response = requests.post(f"{BACKEND_URL}chat/follow-up-question", json=claim_context, timeout=120)
            response.raise_for_status()
            answer = response.json().get("answer", "No answer returned.")

            st.session_state.chat_history.append({"role": "user", "content": question})
            st.session_state.chat_history.append({"role": "assistant", "content": answer})

            for item in st.session_state.chat_history:
                with st.chat_message(item["role"]):
                    st.write(item["content"])
        except Exception as exc:
            st.error(f"Chat failed: {exc}")

else:
    st.info("Submit a claim to begin the evaluation and chat flow.")
