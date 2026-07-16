import streamlit as st
import c_rate_plots, charging_statistics

st.set_page_config(
    page_title="Cell Balancing Dashboard",
    layout='wide',
    initial_sidebar_state='auto'
)

with st.sidebar:
    st.markdown("<h1 style='text-align: left; color: white;'>Pages</h1>",
                unsafe_allow_html=True)

    page_choice = st.radio(
        f"_"*40,

        ("Cell Deviation", "c-rate analysis")

    )



if page_choice == "Cell Deviation":

    charging_statistics.run()

elif page_choice == "c-rate analysis":
    
    c_rate_plots.run()