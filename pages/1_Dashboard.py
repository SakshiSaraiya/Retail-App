import streamlit as st
import pandas as pd
import plotly.express as px

# Page setup
st.set_page_config(page_title="📊 Dashboard", layout="wide")

# Global CSS styling
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #0F172A;
    }

    [data-testid="stSidebar"] .css-1d391kg,
    [data-testid="stSidebar"] .css-1v3fvcr,
    [data-testid="stSidebar"] .css-qri22k {
        color: #F1F5F9 !important;
    }

    .block-container {
        background-color: #F8FAFC;
        padding-top: 2rem;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #0F172A;
    }

    .metric-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.05);
        text-align: center;
    }

    .metric-card h3 {
        margin: 0.5rem 0 0;
        color: #0F172A;
        font-size: 1.5rem;
    }

    .metric-card p {
        margin: 0;
        font-size: 0.9rem;
        color: #475569;
    }

    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Dummy data (replace with actual SQL data or other sources)
data = {
    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    'Spending': [1200, 1100, 1350, 1250, 1400, 1320]
}
df = pd.DataFrame(data)

pie_data = pd.DataFrame({
    'Category': ['Groceries', 'Transport', 'Entertainment', 'Utilities', 'Savings'],
    'Amount': [3100, 1200, 1500, 1900, 2300]
})

# Title
st.title("📊 Financial Dashboard")

# KPI cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="metric-card">
            <h3>₹12,470</h3>
            <p>Total Spending (Monthly)</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="metric-card">
            <h3>₹2,800</h3>
            <p>Total Savings</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="metric-card">
            <h3>₹4,150</h3>
            <p>Utilities & Essentials</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Layout for charts
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("Spending by Category (Monthly)")
    fig_pie = px.pie(
        pie_data,
        names='Category',
        values='Amount',
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#0F172A')
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with right_col:
    st.subheader("Spending Trend (Last 6 Months)")
    fig_bar = px.bar(
        df,
        x='Month',
        y='Spending',
        title="",
        color_discrete_sequence=['#3B82F6']
    )
    fig_bar.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='#0F172A'),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
