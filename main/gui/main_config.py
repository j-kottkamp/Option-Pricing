from imports import st

def main_config_page():
    st.set_page_config(layout="wide")

    st.sidebar.markdown("<h1 style='font-size:40px; color:white;'>🛠 Settings</h1>", unsafe_allow_html=True)

    st.sidebar.markdown("---")

    application = st.sidebar.selectbox(
        "Select App",
        ("Option Pricing Module", "Option Data Analysis", "Stock Data Analysis", "GBM Generator")
    )
    return application