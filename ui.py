import streamlit as st
import httpx
import json
import time

API_URL = "http://localhost:8000"

st.set_page_config(page_title="VLM Document Extraction", page_icon="📄", layout="wide")

st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #1e1b4b, #312e81);
    border-radius: 12px; padding: 20px; color: white; text-align: center;
}
.metric-card .value { font-size: 2rem; font-weight: 800; }
.metric-card .label { font-size: 0.85rem; opacity: 0.8; }
.field-row { padding: 8px 12px; border-radius: 8px; margin: 4px 0; }
.field-ok { background: rgba(16,185,129,0.1); border-left: 3px solid #10b981; }
.field-miss { background: rgba(239,68,68,0.1); border-left: 3px solid #ef4444; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="background: linear-gradient(135deg, #4f46e5, #1e1b4b); padding: 40px 30px; border-radius: 16px; text-align: center; color: white; margin-bottom: 30px;">
    <h1 style="margin:0; font-size: 2.2rem;">📄 VLM Document Extraction API</h1>
    <p style="margin: 10px 0 0; color: #c7d2fe; font-size: 1.1rem;">
        Upload a document or paste text → Extract structured data with confidence scoring
    </p>
</div>
""", unsafe_allow_html=True)

# Check API health
try:
    health = httpx.get(f"{API_URL}/health", timeout=3).json()
    api_status = "🟢 API Online"
    provider_info = health.get("provider", "mock")
except Exception:
    api_status = "🔴 API Offline — run: uvicorn app.main:app --port 8000"
    provider_info = "N/A"

with st.sidebar:
    st.markdown("### About")
    st.markdown("Built by **Nguyen Minh Tri**")
    st.markdown("Senior AI Engineer")
    st.markdown(f"**Status:** {api_status}")
    st.markdown(f"**Provider:** `{provider_info}`")
    st.markdown("---")
    st.markdown("[GitHub](https://github.com/Boothill2001)")

tab1, tab2, tab3, tab4 = st.tabs(["📝 Extract from Text", "📁 Upload File", "📊 Evaluate", "🔍 API Health"])

with tab1:
    st.subheader("Extract Structured Data from Text")

    sample_text = """INVOICE

Invoice #: INV-2026-0847
Date: 2026-06-15

From: TechVision Solutions Ltd.
Bill To: GlobalTrade Corp.

Payment Terms: Net 30
Due Date: 2026-07-15

No.  Item                          Qty   Unit Price   Amount
1    Cloud Infrastructure Setup     1     $4,500.00    $4,500.00
2    API Integration Service        3     $1,200.00    $3,600.00
3    Data Pipeline Development      2     $2,800.00    $5,600.00
4    Technical Documentation        1     $800.00      $800.00

Subtotal: $14,500.00
Tax (10%): $1,450.00
Total Amount: $15,950.00"""

    col_input, col_config = st.columns([3, 1])
    with col_input:
        text_input = st.text_area("Paste document text:", value=sample_text, height=350)
    with col_config:
        doc_type = st.selectbox("Document type", ["invoice"])
        provider = st.selectbox("Provider", ["mock", "gpt4", "gemini", "deepseek", "claude"])
        strict = st.checkbox("Strict schema", value=True)

    if st.button("🚀 Extract", type="primary", use_container_width=True, key="extract_text"):
        if not text_input.strip():
            st.error("Please enter some text")
        else:
            with st.spinner("Extracting..."):
                try:
                    resp = httpx.post(f"{API_URL}/v1/extract/text", json={
                        "text": text_input,
                        "document_type": doc_type,
                        "provider": provider,
                        "require_strict_schema": strict,
                    }, timeout=30)
                    data = resp.json()

                    if resp.status_code != 200:
                        st.error(f"Error: {data.get('detail', resp.text)}")
                    else:
                        # Metrics row
                        m1, m2, m3, m4 = st.columns(4)
                        m1.metric("Confidence", f"{data['confidence_score']:.0%}")
                        m2.metric("Processing Time", f"{data['processing_time_ms']:.0f}ms")
                        m3.metric("Validation Errors", len(data['validation_errors']))
                        m4.metric("Human Review", "Yes" if data['requires_human_review'] else "No")

                        st.markdown("---")

                        col_fields, col_json = st.columns([1, 1])

                        with col_fields:
                            st.markdown("#### Extracted Fields")
                            fields = data["extracted_fields"]
                            confidences = data["field_confidences"]

                            for field, value in fields.items():
                                if field == "line_items":
                                    continue
                                conf = confidences.get(field, 0)
                                icon = "✅" if conf >= 1.0 else "⚠️" if conf > 0 else "❌"
                                css = "field-ok" if conf >= 1.0 else "field-miss"
                                display_val = value if value is not None else "—"
                                st.markdown(
                                    f'<div class="field-row {css}">{icon} <strong>{field}:</strong> {display_val}</div>',
                                    unsafe_allow_html=True
                                )

                            # Line items
                            items = fields.get("line_items", [])
                            if items:
                                st.markdown("#### Line Items")
                                st.dataframe(items, use_container_width=True)

                        with col_json:
                            st.markdown("#### Full JSON Response")
                            st.json(data)

                        if data["validation_errors"]:
                            st.warning("**Validation Errors:**\n" + "\n".join(f"- {e}" for e in data["validation_errors"]))

                        if data["warnings"]:
                            st.info("**Warnings:**\n" + "\n".join(f"- {w}" for w in data["warnings"]))

                except httpx.ConnectError:
                    st.error("Cannot connect to API. Run: `uvicorn app.main:app --port 8000`")

with tab2:
    st.subheader("Upload Document File")
    st.caption("Supported: PDF, PNG, JPG, TXT")

    uploaded = st.file_uploader("Choose a file", type=["pdf", "png", "jpg", "jpeg", "txt"])

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        doc_type2 = st.selectbox("Document type", ["invoice"], key="dt2")
    with col_c2:
        provider2 = st.selectbox("Provider", ["mock", "gpt4", "gemini", "deepseek", "claude"], key="pv2")

    if st.button("🚀 Extract from File", type="primary", use_container_width=True) and uploaded:
        with st.spinner("Uploading and extracting..."):
            try:
                files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type or "application/octet-stream")}
                resp = httpx.post(
                    f"{API_URL}/v1/extract",
                    files=files,
                    data={"document_type": doc_type2, "provider": provider2, "require_strict_schema": "true"},
                    timeout=30,
                )

                if resp.status_code != 200:
                    st.error(f"Error ({resp.status_code}): {resp.text}")
                else:
                    data = resp.json()
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Confidence", f"{data['confidence_score']:.0%}")
                    m2.metric("Processing Time", f"{data['processing_time_ms']:.0f}ms")
                    m3.metric("Validation Errors", len(data['validation_errors']))
                    m4.metric("Human Review", "Yes" if data['requires_human_review'] else "No")

                    st.markdown("---")
                    st.markdown("#### Extracted Fields")
                    fields = data["extracted_fields"]
                    confidences = data.get("field_confidences", {})
                    for field, value in fields.items():
                        if field == "line_items":
                            continue
                        conf = confidences.get(field, 0)
                        icon = "✅" if conf >= 1.0 else "⚠️" if conf > 0 else "❌"
                        css = "field-ok" if conf >= 1.0 else "field-miss"
                        display_val = value if value is not None else "—"
                        st.markdown(
                            f'<div class="field-row {css}">{icon} <strong>{field}:</strong> {display_val}</div>',
                            unsafe_allow_html=True
                        )
                    items = fields.get("line_items", [])
                    if items:
                        st.markdown("#### Line Items")
                        st.dataframe(items, use_container_width=True)

                    st.markdown("#### Full JSON Response")
                    st.json(data)

            except httpx.ConnectError:
                st.error("Cannot connect to API. Run: `uvicorn app.main:app --port 8000`")

with tab3:
    st.subheader("Evaluation — Mock Provider vs Ground Truth")
    st.caption("Compares mock extraction of sample_invoice.txt against ground truth")

    if st.button("🧪 Run Evaluation", type="primary", use_container_width=True):
        with st.spinner("Evaluating..."):
            try:
                resp = httpx.post(f"{API_URL}/v1/evaluate", timeout=30)
                data = resp.json()

                m1, m2, m3 = st.columns(3)
                m1.metric("Field Accuracy", f"{data['field_accuracy']:.0%}")
                m2.metric("Exact Match", "✅ YES" if data['exact_match'] else "❌ NO")
                m3.metric("Latency", f"{data['latency_ms']:.0f}ms")

                st.markdown("---")

                if data["missing_fields"]:
                    st.error(f"**Missing fields:** {', '.join(data['missing_fields'])}")
                if data["mismatched_fields"]:
                    st.warning("**Mismatched fields:**")
                    st.json(data["mismatched_fields"])
                if data["exact_match"] and not data["missing_fields"]:
                    st.success("🎉 All fields match ground truth perfectly!")

                st.markdown("#### Full Evaluation Result")
                st.json(data)

            except httpx.ConnectError:
                st.error("Cannot connect to API. Run: `uvicorn app.main:app --port 8000`")

with tab4:
    st.subheader("API Health Check")

    if st.button("🔄 Check Health", use_container_width=True):
        try:
            resp = httpx.get(f"{API_URL}/health", timeout=5)
            data = resp.json()
            st.success(f"**Status:** {data['status']}")
            st.json(data)
        except httpx.ConnectError:
            st.error("API is not running. Start with: `uvicorn app.main:app --port 8000`")
