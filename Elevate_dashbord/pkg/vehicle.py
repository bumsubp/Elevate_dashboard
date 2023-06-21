"""
Dependencies
"""
import streamlit as st
from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
import pkg.support.funcs as funcs
import datetime
import math
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np

def main():
  set_css_style()

  veh_raw_df = funcs.get_vehicles_data()

  ###############
  ### Filter  ###
  ###############
  """
  Sidebar
  """

  ### sidebar title
  st.sidebar.header('Filter:')  

  ### Date selector
  st.sidebar.subheader('Date Range')
  with st.sidebar.expander("Expand"):
    side_col = st.sidebar.columns(3)
    init_date = datetime.datetime(2023, 2, 1)
    today = datetime.date.today()
    with side_col[0]:
      start_date = st.date_input('Start date', init_date)
    with side_col[1]:
      end_date = st.date_input('End date', today)
  
  pre_start_date = (start_date - datetime.timedelta(days=(end_date - start_date).days))
  pre_end_date = (end_date - datetime.timedelta(days=(end_date - start_date).days))
  
  if start_date < end_date:
    st.sidebar.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
  else:
    st.sidebar.error('Error: End date must fall after start date.')

  ### Model selector
  st.sidebar.subheader('Vehicle Model')
  option_list_model = list(veh_raw_df['vehicle-model'].unique())
  selected_model = st.sidebar.multiselect('Select Model', option_list_model, default=option_list_model)

  ### Model year selector
  st.sidebar.subheader('Vehicle Year')
  option_list_year = sorted(list(veh_raw_df['vehicle-year'].unique()))
  selected_year = st.sidebar.multiselect('Select Year', option_list_year, default=option_list_year)
  
  ### Vehicle Price range selector
  veh_price_min, veh_price_max = st.sidebar.slider('Select Price Range ($)', 
                                                   math.floor(veh_raw_df['vehicle-purchase-price'].min()), 
                                                   math.ceil(veh_raw_df['vehicle-purchase-price'].max()), 
                                                   (math.floor(veh_raw_df['vehicle-purchase-price'].min()), math.ceil(veh_raw_df['vehicle-purchase-price'].max())))

  veh_df = veh_raw_df.loc[(veh_raw_df['vehicle-purchase-date'] >= np.datetime64(start_date)) &
                          (veh_raw_df['vehicle-purchase-date'] <= np.datetime64(end_date)) &
                          (veh_raw_df['vehicle-model'].isin(selected_model)) &
                          (veh_raw_df['vehicle-year'].isin(selected_year)) &
                          (veh_raw_df['vehicle-purchase-price'] >= veh_price_min) &
                          (veh_raw_df['vehicle-purchase-price'] <= veh_price_max) 
                         ] 

  ################
  ### Purchase ###
  ################

  veh_count = len(veh_df['vin'].unique())
  veh_df['week_num'] = veh_df['vehicle-purchase-date'].dt.isocalendar().week
  veh_df['Week Start Date'] = veh_df['vehicle-purchase-date'].map(lambda x:funcs.get_first_day_of_week(x.year, x.week))

  ## For the chart of the fleet size
  # count the number of vehicles by week number
  veh_chart_df = veh_df.groupby('Week Start Date').size().reset_index().rename(columns={0:'fleet_size'}).sort_values(by='Week Start Date')
  veh_chart_df['Week Start Date'] = veh_chart_df['Week Start Date'].astype('str')
  # Define the start and end dates
  start_date = veh_df['vehicle-purchase-date'].min() - datetime.timedelta(days=7)
  end_date = veh_df['vehicle-purchase-date'].max()
  # Create a range of dates
  date_range = pd.date_range(start=start_date, end=end_date, freq='W-MON')
  # Get the week start dates
  week_start_dates = date_range.strftime('%Y-%m-%d').tolist()
  # create a dataframe including all weeks in the date range
  veh_chart_wk_df = pd.DataFrame([[w] for w in week_start_dates], columns=['Week Start Date'])
  veh_chart_wk_df = pd.merge(veh_chart_wk_df, veh_chart_df, on='Week Start Date', how='left').fillna(0)
  veh_chart_wk_df['cum_fleet_size'] = veh_chart_wk_df['fleet_size'].cumsum()

  #################
  ### Dashboard ###
  #################

  ## KPI
  col = st.columns(3)
  with col[0]:
    st.metric('Total Fleet Size', value=veh_count)
  
  with col[1]:
    active_contracts = 3
    st.metric('Active Contracts', value=3)
  
  with col[2]:
    st.metric('Utilization', value=f'{active_contracts/veh_count*100:.1f}%')

  ## Chart
  col = st.columns(2)
  
  with col[0]:
    st.markdown('#### Fleet Size by Week Start')
    ## Fleet size and cumulative fleet size by week start
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    fig.add_trace(
        go.Bar(x=veh_chart_wk_df['Week Start Date'], y=veh_chart_wk_df['fleet_size'], name='Fleet Size'),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=veh_chart_wk_df['Week Start Date'], y=veh_chart_wk_df['cum_fleet_size'], name='Cum. Fleet Size'),
        secondary_y=True,
    )
    fig.update_yaxes(range=[0, veh_chart_wk_df['fleet_size'].max()+1], row=1, col=1,
                     secondary_y=False)
    fig.update_yaxes(range=[0, veh_chart_wk_df['cum_fleet_size'].max()+1], row=1, col=1,
                     secondary_y=True)
    fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), dragmode='pan',
                      yaxis1_title='Fleet Size', yaxis2_title='Cumulative Fleet Size')
    st.plotly_chart(fig, use_container_width=True)
    
  with col[1]:
    st.markdown('#### Vehicle Utilization')
    ## Fleet size and cumulative fleet size by week start
    # Create figure with secondary y-axis
    fig = make_subplots()
    # Add traces
    fig.add_trace(
        go.Scatter(x=veh_chart_wk_df['Week Start Date'], y=[70, 100], name='Vehicle Utilization'),
    )
    fig.add_trace(
        go.Scatter(x=veh_chart_wk_df['Week Start Date'], y=[80]*len(veh_chart_wk_df['Week Start Date']), name='Utilization Target', mode='lines', marker=dict(color='black')),
    )
    fig.update_yaxes(range=[0, 101],)
    
    fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), dragmode='pan',
                      yaxis_title='Utilization (%)')
    st.plotly_chart(fig, use_container_width=True)

  ## Table
  st.table(veh_df)
  

def set_css_style():
  st.markdown(
    """
    <style>
    [data-testid="stImage"] {
      overflow-x: scroll; 
      width: 100%;
      height: 250px;
    }
    </style>
    """,
    unsafe_allow_html=True
  )

