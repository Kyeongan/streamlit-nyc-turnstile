import streamlit as st

st.markdown("""
<style>
html {
  font-size: 0.9rem;
}
[data-testid="stMarkdownContainer"]>p {
    font-size: 1.2rem;
}
[data-testid="stMetricValue"] {
    font-size: 6.0rem;
    font-weight: 200;
    color: #2980b9;
}
.big-font {
    font-size:1.8rem !important;
    font-weight: 600;
}
.mid-font {
    font-size: 2.5rem !important;
    font-weight: 600;
    color: #2d3436;
}
</style>
""", unsafe_allow_html=True)
