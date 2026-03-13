import streamlit as st
from snowflake.snowpark.session import Session
import pandas as pd

def create_session():
    try:
        connection_params = {
            "account": st.secrets["snowflake"]["account"],
            "user": st.secrets["snowflake"]["user"],
            "password": st.secrets["snowflake"]["password"],
            "warehouse": st.secrets["snowflake"]["warehouse"],
            "database": st.secrets["snowflake"]["database"],
            "schema": st.secrets["snowflake"]["schema"],
            "role": st.secrets["snowflake"]["role"],
        }
        return Session.builder.configs(connection_params).create()
    except Exception as e:
        st.error(f"Connection failed: {e}")
        st.stop()

session = create_session()

def ask_cortex(prompt):
    clean = prompt.replace("'", "").replace("\\", "")[:2000]
    result = session.sql(f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large2', '{clean}') AS R
    """).collect()[0]["R"]
    return result

st.set_page_config(page_title="DPDP Shield", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
.hero {
    background: linear-gradient(135deg, #0b1f3a 0%, #1a3a6a 100%);
    padding: 40px; border-radius: 16px;
    border: 1px solid #1e3d6e;
    text-align: center; margin-bottom: 24px;
}
.hero h1 { font-size: 2.5rem; color: #d4e9ff; margin-bottom: 8px; }
.hero p { color: #6b8fc7; font-size: 1rem; }
.metric-card {
    background: #0b1f3a; border: 1px solid #1e3d6e;
    border-radius: 12px; padding: 20px; text-align: center;
}
.metric-num { font-size: 2rem; font-weight: 700; color: #7ab3ff; }
.metric-label { font-size: 0.8rem; color: #4a7bc7; margin-top: 4px; }
.section-card {
    background: #0b1f3a; border: 1px solid #1e3d6e;
    border-radius: 12px; padding: 20px; margin-bottom: 16px;
}
.chat-user {
    background: #1a3a6a; padding: 12px 16px;
    border-radius: 12px; margin: 8px 0; color: #d4e9ff;
}
.chat-ai {
    background: #0b1f3a; padding: 12px 16px;
    border-radius: 12px; margin: 8px 0;
    border: 1px solid #1e3d6e; color: #c4d8f0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🛡️ DPDP Shield</h1>
    <p>Agentic AI Platform · India Digital Personal Data Protection Act 2023 · Powered by Snowflake Cortex</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🏠 Dashboard", "🤖 AI Chatbot", "⚖️ Risk Auditor",
    "📄 Doc Studio", "🚨 Breaches", "📋 Grievances", "👤 My Rights"
])

with tab1:
    st.subheader("📊 National Compliance Overview")
    try:
        total_orgs = session.sql("SELECT COUNT(*) AS C FROM DPDP_DB.ENTITIES.DATA_FIDUCIARIES").collect()[0]["C"]
        total_consents = session.sql("SELECT COUNT(*) AS C FROM DPDP_DB.COMPLIANCE.CONSENT_RECORDS").collect()[0]["C"]
        active_breaches = session.sql("SELECT COUNT(*) AS C FROM DPDP_DB.INCIDENTS.BREACH_INCIDENTS WHERE STATUS != 'RESOLVED'").collect()[0]["C"]
        open_grievances = session.sql("SELECT COUNT(*) AS C FROM DPDP_DB.INCIDENTS.GRIEVANCES WHERE STATUS != 'RESOLVED'").collect()[0]["C"]
        avg_score = session.sql("SELECT ROUND(AVG(COMPLIANCE_SCORE),1) AS C FROM DPDP_DB.ENTITIES.DATA_FIDUCIARIES").collect()[0]["C"]

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-num">{total_orgs}</div><div class="metric-label">Registered Fiduciaries</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card"><div class="metric-num">{total_consents}</div><div class="metric-label">Consent Records</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card"><div class="metric-num" style="color:#e74c3c">{active_breaches}</div><div class="metric-label">Active Breaches</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><div class="metric-num" style="color:#f39c12">{open_grievances}</div><div class="metric-label">Open Grievances</div></div>', unsafe_allow_html=True)
        with col5:
            st.markdown(f'<div class="metric-card"><div class="metric-num" style="color:#2ecc71">{avg_score}%</div><div class="metric-label">Avg Compliance Score</div></div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Dashboard error: {e}")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🏢 Organisation Compliance")
        try:
            df_orgs = session.sql("""
                SELECT ORGANISATION_NAME AS Organisation, INDUSTRY,
                USER_COUNT AS Users,
                CASE WHEN IS_SDF THEN 'Yes' ELSE 'No' END AS SDF,
                COMPLIANCE_SCORE AS Score
                FROM DPDP_DB.ENTITIES.DATA_FIDUCIARIES
                ORDER BY COMPLIANCE_SCORE DESC
            """).to_pandas()
            st.dataframe(df_orgs, use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")
    with col2:
        st.subheader("🚨 Recent Breaches")
        try:
            df_breaches = session.sql("""
                SELECT ORGANISATION_NAME AS Organisation,
                BREACH_TYPE AS Type, SEVERITY,
                AFFECTED_COUNT AS Affected, STATUS
                FROM DPDP_DB.INCIDENTS.BREACH_INCIDENTS
                ORDER BY BREACH_DATE DESC
            """).to_pandas()
            st.dataframe(df_breaches, use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown("---")
    st.subheader("📈 Consent Analytics")
    col1, col2 = st.columns(2)
    with col1:
        try:
            df_consent = session.sql("""
                SELECT CONSENT_STATUS AS STATUS, COUNT(*) AS Count
                FROM DPDP_DB.COMPLIANCE.CONSENT_RECORDS
                GROUP BY CONSENT_STATUS
            """).to_pandas()
            st.bar_chart(df_consent.set_index("STATUS"))
        except Exception as e:
            st.error(f"Error: {e}")
    with col2:
        try:
            df_risk = session.sql("""
                SELECT RISK_LEVEL AS RISK, COUNT(*) AS Count
                FROM DPDP_DB.COMPLIANCE.DATA_PROCESSING_LOG
                GROUP BY RISK_LEVEL
            """).to_pandas()
            st.bar_chart(df_risk.set_index("RISK"))
        except Exception as e:
            st.error(f"Error: {e}")

with tab2:
    st.subheader("🤖 DPDP Cortex AI Assistant")
    st.caption("Powered by Snowflake Cortex Mistral")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-ai">🛡️ {msg["content"]}</div>', unsafe_allow_html=True)

    user_input = st.chat_input("Ask anything about DPDP compliance...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("🤖 Cortex AI thinking..."):
            try:
                live = session.sql("""
                    SELECT
                        (SELECT COUNT(*) FROM DPDP_DB.INCIDENTS.BREACH_INCIDENTS WHERE STATUS != 'RESOLVED') AS B,
                        (SELECT COUNT(*) FROM DPDP_DB.INCIDENTS.GRIEVANCES WHERE STATUS != 'RESOLVED') AS G,
                        (SELECT ROUND(AVG(COMPLIANCE_SCORE),1) FROM DPDP_DB.ENTITIES.DATA_FIDUCIARIES) AS S
                """).collect()[0]
                data_ctx = f"Live data: {live['B']} active breaches, {live['G']} open grievances, {live['S']}% avg compliance score."
            except:
                data_ctx = ""
            prompt = f"You are DPDP Shield AI expert on India DPDP Act 2023. {data_ctx} Question: {user_input} Give structured answer citing DPDP sections. Guidance only not legal advice."
            response = ask_cortex(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

with tab3:
    st.subheader("⚖️ Compliance Risk Auditor")
    col1, col2 = st.columns(2)
    with col1:
        practice = st.text_area("Describe your data practice", placeholder="e.g. We collect Aadhaar PAN for loan processing...", height=150, key="audit_practice")
        org_name = st.text_input("Organisation Name", key="audit_org")
        industry = st.selectbox("Industry", ["Technology", "Financial Services", "Healthcare", "E-Commerce", "Education", "Other"], key="audit_industry")
        if st.button("🔍 Audit Now", use_container_width=True):
            if practice:
                with st.spinner("Auditing..."):
                    prompt = f"DPDP Act 2023 compliance audit. Organisation: {org_name} Industry: {industry} Practice: {practice} Provide: 1. RISK LEVEL HIGH/MEDIUM/LOW with emoji 2. APPLICABLE DPDP SECTIONS 3. COMPLIANCE GAPS 4. REQUIRED ACTIONS 5. PENALTY EXPOSURE. Cite section numbers."
                    st.session_state["audit_result"] = ask_cortex(prompt)
    with col2:
        if "audit_result" in st.session_state:
            st.markdown("### 📋 Audit Report")
            st.markdown(f'<div class="section-card">{st.session_state["audit_result"]}</div>', unsafe_allow_html=True)

with tab4:
    st.subheader("📄 Document Drafting Studio")
    col1, col2 = st.columns(2)
    with col1:
        doc_type = st.selectbox("Document Type", [
            "Privacy Notice", "Consent Form",
            "Grievance Redressal Policy", "Data Retention Policy",
            "Breach Notification Letter", "DPO Appointment Letter",
            "Data Processing Agreement"
        ], key="doc_type_select")
        biz_name = st.text_input("Organisation Name", key="doc_org")
        biz_desc = st.text_area("Describe your business and data practices", height=120, key="doc_desc")
        if st.button("📝 Generate Document", use_container_width=True):
            if biz_desc:
                with st.spinner("Generating..."):
                    prompt = f"Generate complete DPDP Act 2023 compliant {doc_type} for Organisation: {biz_name} Business: {biz_desc}. Make it professional complete with clear headings cite DPDP sections ready to use."
                    st.session_state["doc"] = ask_cortex(prompt)
                    st.session_state["doc_type"] = doc_type
    with col2:
        if "doc" in st.session_state:
            st.markdown(f"### 📋 {st.session_state['doc_type']}")
            st.markdown(f'<div class="section-card" style="max-height:500px;overflow-y:auto">{st.session_state["doc"]}</div>', unsafe_allow_html=True)
            st.download_button("⬇️ Download", st.session_state["doc"],
                file_name=f"{st.session_state['doc_type'].replace(' ','_')}.txt",
                use_container_width=True)

with tab5:
    st.subheader("🚨 Breach Incident Tracker")
    try:
        df_b = session.sql("""
            SELECT BREACH_ID AS ID, ORGANISATION_NAME AS Organisation,
            BREACH_TYPE AS Type, SEVERITY, AFFECTED_COUNT AS Affected,
            DATEDIFF('hour', BREACH_DATE, NOTIFICATION_DATE) AS Hours_To_Notify,
            STATUS, FINE_IMPOSED AS Fine_INR
            FROM DPDP_DB.INCIDENTS.BREACH_INCIDENTS
            ORDER BY BREACH_DATE DESC
        """).to_pandas()
        st.dataframe(df_b, use_container_width=True)
    except Exception as e:
        st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("#### ⚡ 72-Hour Rule Check")
    try:
        df_72 = session.sql("""
            SELECT ORGANISATION_NAME AS Organisation,
            DATEDIFF('hour', BREACH_DATE, NOTIFICATION_DATE) AS Hours_Taken,
            CASE WHEN DATEDIFF('hour', BREACH_DATE, NOTIFICATION_DATE) <= 72
            THEN 'Compliant' ELSE 'VIOLATED' END AS Status
            FROM DPDP_DB.INCIDENTS.BREACH_INCIDENTS
            WHERE NOTIFICATION_DATE IS NOT NULL
        """).to_pandas()
        st.dataframe(df_72, use_container_width=True)
    except Exception as e:
        st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("#### 🤖 AI Breach Response Playbook")
    breach_desc = st.text_area("Describe your breach", placeholder="e.g. Unauthorised access exposed 10000 user emails...", key="breach_desc")
    if st.button("🚨 Generate Response Plan"):
        if breach_desc:
            with st.spinner("Generating playbook..."):
                prompt = f"DPDP Act 2023 breach response playbook for: {breach_desc}. Include: 1. IMMEDIATE ACTIONS first 6 hours 2. 72-HOUR NOTIFICATION CHECKLIST Section 8 3. DATA PROTECTION BOARD NOTIFICATION steps 4. AFFECTED USERS NOTIFICATION template 5. CONTAINMENT STEPS 6. PENALTY EXPOSURE."
                st.markdown(f'<div class="section-card">{ask_cortex(prompt)}</div>', unsafe_allow_html=True)

with tab6:
    st.subheader("📋 Grievance Management")
    col1, col2 = st.columns([2, 1])
    with col1:
        try:
            df_g = session.sql("""
                SELECT GRIEVANCE_ID AS ID, DATA_PRINCIPAL_ID AS User,
                ORGANISATION_NAME AS Organisation, GRIEVANCE_TYPE AS Type,
                STATUS, SLA_DAYS_REMAINING AS SLA_Days,
                CASE WHEN ESCALATED_TO_DPB THEN 'Yes' ELSE 'No' END AS Escalated
                FROM DPDP_DB.INCIDENTS.GRIEVANCES
                ORDER BY FILED_DATE DESC
            """).to_pandas()
            st.dataframe(df_g, use_container_width=True)
        except Exception as e:
            st.error(f"Error: {e}")
    with col2:
        st.markdown("#### ➕ File New Grievance")
        g_user = st.text_input("Your User ID", key="grv_user")
        g_org = st.text_input("Organisation", key="grv_org")
        g_type = st.selectbox("Type", ["ACCESS_REQUEST", "ERASURE_REQUEST", "CORRECTION_REQUEST", "CONSENT_WITHDRAWAL", "DATA_SHARING"], key="grv_type")
        g_desc = st.text_area("Description", height=80, key="grv_desc")
        if st.button("📨 Submit", use_container_width=True):
            if g_user and g_org and g_desc:
                try:
                    gid = f"GRV{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}"
                    session.sql(f"""
                        INSERT INTO DPDP_DB.INCIDENTS.GRIEVANCES
                        SELECT '{gid}','{g_user}','{g_org}','{g_type}',
                        '{g_desc[:200]}','OPEN',CURRENT_TIMESTAMP(),
                        NULL,NULL,30,FALSE,CURRENT_TIMESTAMP()
                    """).collect()
                    st.success(f"✅ Grievance {gid} filed!")
                except Exception as e:
                    st.error(f"Error: {e}")

with tab7:
    st.subheader("👤 Citizen Rights Portal")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🔍 Check My Consents")
        user_id = st.text_input("Your User ID", placeholder="Try USR001, USR002, USR003", key="rights_user")
        if st.button("🔎 Find My Data") and user_id:
            try:
                df_my = session.sql(f"""
                    SELECT ORGANISATION_NAME AS Organisation,
                    PURPOSE, CONSENT_STATUS AS Status, CONSENT_DATE AS Date
                    FROM DPDP_DB.COMPLIANCE.CONSENT_RECORDS
                    WHERE DATA_PRINCIPAL_ID = '{user_id}'
                """).to_pandas()
                if len(df_my) > 0:
                    st.dataframe(df_my, use_container_width=True)
                else:
                    st.info("No records found. Try USR001, USR002 or USR003")
            except Exception as e:
                st.error(f"Error: {e}")

        st.markdown("---")
        st.markdown("#### 📜 Your Rights")
        rights = {
            "🔍 Right to Access (Section 11)": "Get summary of all your data being processed",
            "✏️ Right to Correction (Section 12)": "Fix inaccurate or incomplete data",
            "🗑️ Right to Erasure (Section 12)": "Delete data no longer needed",
            "📢 Right to Grievance (Section 13)": "Complain and get resolution in 30 days",
            "👥 Right to Nominate (Section 14)": "Appoint someone to act on your behalf"
        }
        for right, desc in rights.items():
            st.markdown(f"**{right}**")
            st.caption(desc)
            st.markdown("---")

    with col2:
        st.markdown("#### 🤖 Ask About Your Rights")
        rights_q = st.text_area("Describe your situation",
            placeholder="e.g. Company still sending emails after I withdrew consent. What can I do?",
            height=150, key="rights_q")
        if st.button("💬 Get Guidance", use_container_width=True):
            if rights_q:
                with st.spinner("Getting guidance..."):
                    prompt = f"Citizen rights advisor India DPDP Act 2023. Situation: {rights_q}. Explain rights that apply with sections, step by step actions, how to complain, escalation to Data Protection Board, timeline. Simple plain language."
                    st.markdown(f'<div class="section-card">{ask_cortex(prompt)}</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div style="text-align:center;color:#4a6a9a;font-size:0.75rem;padding:16px">🛡️ DPDP Shield · Snowflake Cortex AI · DPDP Act 2023 · Not legal advice</div>', unsafe_allow_html=True)
