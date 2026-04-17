"""
RetailGenius - AI-Powered Retail Assistant
Main Streamlit Application
Full implementation with all features
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys

# Local imports
from data_loader import load_sample_data, load_bq_data
from recommender import get_recommendations
from utils import (
    extract_preferences, detect_language, validate_input,
    format_currency, parse_price_range, get_alert_message,
    translate_text
)

# PAGE CONFIG
st.set_page_config(
    page_title="RetailGenius - AI Retail Assistant",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CUSTOM CSS
st.markdown("""
<style>
    .recommendation-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .header-style {
        color: #667eea;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []
if "prefs" not in st.session_state:
    st.session_state.prefs = {}
if "viewed_products" not in st.session_state:
    st.session_state.viewed_products = []
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "language" not in st.session_state:
    st.session_state.language = "English"

# SIDEBAR
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    api_key = st.text_input("🔑 Gemini API Key", type="password",
                            value=st.secrets.get("GEMINI_API_KEY", ""))
    if api_key:
        st.session_state.api_key = api_key
    
    language = st.selectbox("🌐 Language",
                           ["English", "Tamil", "Hindi"],
                           index=["English", "Tamil", "Hindi"].index(st.session_state.language))
    st.session_state.language = language
    
    st.divider()
    st.markdown("### 🔍 Filters")
    
    with st.expander("💰 Price Range"):
        col1, col2 = st.columns(2)
        with col1:
            min_price = st.number_input("Min Price (₹)", value=0, step=100)
        with col2:
            max_price = st.number_input("Max Price (₹)", value=5000, step=100)
        if min_price > 0 or max_price < 5000:
            st.session_state.prefs["min_price"] = min_price
            st.session_state.prefs["max_price"] = max_price
    
    with st.expander("🏷️ Category"):
        category = st.selectbox("Select Category",
                               ["All", "Electronics", "Fashion", "Home", "Sports", "Beauty", "Books"])
        if category != "All":
            st.session_state.prefs["category"] = category
    
    with st.expander("🎨 Color"):
        color = st.selectbox("Select Color",
                            ["Any", "Black", "White", "Blue", "Red", "Green", "Yellow"])
        if color != "Any":
            st.session_state.prefs["color"] = color
    
    st.divider()
    st.markdown("### 📊 Alerts")
    
    try:
        df = load_sample_data()
        low_stock = df[df['stock'] < 10]
        if len(low_stock) > 0:
            st.error(f"⚠️ {len(low_stock)} items low on stock")
    except:
        pass

# MAIN CONTENT
st.markdown('<div class="header-style">🛍️ RetailGenius</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Dashboard", "ℹ️ About"])

# TAB 1: CHAT
with tab1:
    st.markdown("### Ask me anything about products!")
    
    if st.session_state.messages:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    if prompt := st.chat_input("Type your question..."):
        if validate_input(prompt):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("🤔 Analyzing..."):
                    try:
                        df = load_sample_data()
                        extracted = extract_preferences(prompt)
                        if extracted:
                            st.session_state.prefs.update(extracted)
                        
                        recommendations = get_recommendations(
                            query=prompt,
                            user_prefs=st.session_state.prefs,
                            products_df=df,
                            api_key=st.session_state.api_key,
                            language=st.session_state.language
                        )
                        
                        if recommendations:
                            response = "✨ **Top Recommendations:**\n\n"
                            for i, rec in enumerate(recommendations[:3], 1):
                                response += f"**{i}. {rec.get('name', 'Product')}** - {format_currency(rec.get('price', 0))}\n"
                                response += f"📦 Stock: {rec.get('stock', 0)} | Sales: {rec.get('sales', 0)}\n"
                                for reason in rec.get('reasons', [])[:2]:
                                    response += f"   ✔ {reason}\n"
                                response += "\n"
                            st.markdown(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                        else:
                            response = "🔍 No products found"
                            st.warning(response)
                            st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    except Exception as e:
                        error_msg = f"⚠️ Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

# TAB 2: DASHBOARD
with tab2:
    st.markdown("### 📊 Analytics Dashboard")
    
    try:
        df = load_sample_data()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📦 Products", len(df))
        col2.metric("💰 Avg Price", f"₹{df['price'].mean():.0f}")
        col3.metric("📊 Sales", f"{df['sales'].sum():.0f}")
        col4.metric("📦 Stock", f"{df['stock'].sum():.0f}")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(df.nlargest(10, 'sales'), x='name', y='sales',
                        title='Top 10 Products by Sales')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.pie(df, names='category', title='Products by Category')
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

# TAB 3: ABOUT
with tab3:
    st.markdown("""
    ### About RetailGenius
    
    AI-powered retail assistant for:
    - 🤖 Personalized recommendations
    - 💬 Multi-turn chat
    - 📊 Real-time analytics
    - 🌐 Multi-language support
    - ⚡ Session memory
    
    Built with Streamlit & Google Gemini API
    """)

st.divider()
st.markdown("<p style='text-align: center;'>RetailGenius v1.0</p>", unsafe_allow_html=True)
