"""
Dependencies
"""
import streamlit as st
import pkg.support.funcs as funcs
import datetime
import numpy as np
import math
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd 

def main():
  veh_raw_df = funcs.get_vehicles_data()
  scav_df = funcs.get_trip_summary_data()

  # Filter out 1) Null lat/lng, 2)Zero-distance trips, 3) trips with abnormal speed (300 kph)
  scav_df = scav_df.loc[(~scav_df['cvdcqa_trip_orig_lat_r_3'].isna()) & 
                        (scav_df['cvdcqa_trip_orig_lat_r_3'] > 0) & 
                        (scav_df['cvdcqa_odo_chng_km_r_3']>0) & 
                        (scav_df['cvdcqa_odo_chng_km_per_hr_r_3'] < 300)]
  # add Week start date
  scav_df['cvdcqa_partition_date'] = pd.to_datetime(scav_df['cvdcqa_partition_date'], format='%Y-%m-%d')
  scav_df['Week Start Date'] = scav_df['cvdcqa_partition_date'].map(lambda x:funcs.get_first_day_of_week(x.year, x.week))
  scav_df['mileage'] = scav_df['cvdcqa_odo_chng_km_r_3']*0.621371
  scav_df['hour'] = scav_df['cvdcqa_trip_durn_in_secs_r_3']/3600

  scav_count_df = pd.DataFrame(scav_df.groupby(['Week Start Date']).size()).rename(columns={0:'trip_count'})
  scav_mile_df = scav_df[['Week Start Date', 'mileage', 'hour']].groupby(['Week Start Date']).sum()

  # scav_line_gdf = funcs.get_trip_sum_line_data()

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
                          (veh_raw_df['vehicle-purchase-price'] <= veh_price_max)]

  #################
  ### Dashboard ###
  #################
  col = st.columns(4)
  with col[0]:
    # Total miles driven
    value = scav_mile_df['mileage'].sum()
    st.metric(label='Total Miles Driven', value=f'{value:,.1f}mi')
  with col[1]:
    # Average weekly miles
    value = scav_mile_df['mileage'].mean()
    st.metric(label='Avg. Weekly Miles Driven', value=f'{value:,.1f}mi')
    
  with col[2]:
    # Total hours driven
    value = scav_mile_df['hour'].sum()
    st.metric(label='Total Hours Driven', value=f'{value:,.1f}hr')
    
  with col[3]:
    # Average weekly hours driven
    value = scav_mile_df['hour'].mean()
    st.metric(label='Total Weekly Hours Driven', value=f'{value:,.1f}hr')

  col = st.columns(2)
  with col[0]:
    # Bar chart for mileage  
    st.markdown('#### Mileage by Week')
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    fig.add_trace(
        go.Bar(x=scav_count_df.index, y=scav_count_df['trip_count'], name='Trip Count'),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=scav_mile_df.index, y=scav_mile_df['mileage'], name='Mileage'),
        secondary_y=True,
    )
    fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                      yaxis1_title='Trip Count', yaxis2_title='Mileage', xaxis_title='Week Start Date',
                      dragmode='pan',
    )
    st.plotly_chart(fig, use_container_width=True)

  with col[1]:
    st.markdown('#### Range of Miles Driven')
    fig = px.box(scav_df, x='Week Start Date', y='mileage')
    fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                      yaxis_title='Mileage', xaxis_title='Week Start Date',
                      dragmode='pan',
    )
    st.plotly_chart(fig, use_container_width=True)

  # Heatmap of trip origins
  st.markdown('#### Trip Origins')
  fig = px.density_mapbox(scav_df, lat='cvdcqa_trip_orig_lat_r_3', lon='cvdcqa_trip_orig_long_r_3', radius=10,
                        center=dict(lat=scav_df['cvdcqa_trip_orig_lat_r_3'].mean(), lon=scav_df['cvdcqa_trip_orig_long_r_3'].mean()), zoom=6,
                        mapbox_style="open-street-map",)
  st.plotly_chart(fig, use_container_width=True)

  # Data table
  st.markdown('#### Data Table')
  st.table(scav_df.head())
  
  