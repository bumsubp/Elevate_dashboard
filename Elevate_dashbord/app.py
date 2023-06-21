import streamlit as st
st.set_page_config(page_title="Elevate Dashboard", layout="wide")

import pkg.key_metrics
import pkg.general_information
import pkg.vehicle
import pkg.repair
import pkg.mileage_insight

# read the CSS file into a string
with open('./src/style.css') as f:
  css = f.read()
  st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# page list
PAGES = {
    'Key Metrics':pkg.key_metrics,
    'General Information':pkg.general_information,
    'Vehicle':pkg.vehicle,
    'Repair':pkg.repair,
    'Mileage Insights':pkg.mileage_insight,
}

# main page
page = PAGES['Key Metrics']

# Create the header bar
st.markdown(
  """
  <div style="background-color:#f8f9fa;padding:0px;">
  <h1 style="color:#0071e3;text-align:center;">Elevate Dashboard</h1>
  </div>
  """,
  unsafe_allow_html=True
)

# # Add dashboard summary
# st.info(
#     """
#     This dashboard utilizes operational data of the Elevate project to show metrics to measure the success of the project,
#      vehicle repair/operation records, and customer information."""
# )

# Create side-by-side buttons

page_col = st.columns(5)
with page_col[0]:
  txt = 'Key Metrics'
  if st.button(txt):
    page=PAGES[txt]

with page_col[1]:
  txt = 'Vehicle'
  if st.button(txt):
    page=PAGES[txt]

with page_col[2]:
  txt = 'Repair'
  if st.button(txt):
    page=PAGES[txt]

with page_col[3]:
  if st.button("Customer"):
    st.write("This page is a work in progress.")

with page_col[4]:
  txt = 'Mileage Insights'
  if st.button(txt):
    page=PAGES[txt]

page_col = st.columns(5)
with page_col[0]:
  txt = 'General Information'
  if st.button(txt):
    page=PAGES[txt]

page.main()

st.info(
    """
    **Note:** 
    The recommended browser for this app is Chrome. It has not been evaluated with other browsers.  
    """
)
st.markdown(
    "If you have other suggestions, please email me at bpark17@ford.com"
)

st.markdown("----")

