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
  rep_step_df = funcs.get_repair_steps_data()
  rep_task_df = funcs.get_repair_tasks_data()
  part_df = funcs.get_parts_data()
  vin_task_dict = {vin:task for task, vin in zip(rep_task_df['repair-task-id'], rep_task_df['vin'])}

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
  # Selected Repair Tasks
  selected_rep_task = rep_task_df.loc[(rep_task_df['repair-task-date-in'] >= np.datetime64(start_date)) &
                                      (rep_task_df['repair-task-date-in'] <= np.datetime64(end_date)) &
                                      (rep_task_df['repair-task-id'].isin([vin_task_dict[v] for v in veh_df['vin']]))
                                     ]['repair-task-id']
  #############
  ### Labor ###
  #############
  labor_by_task_df = rep_step_df[['repair-task-id', 'repair-step-labor-minutes', 'repair-step-labor-cost']].groupby('repair-task-id').sum().reset_index()
  labor_by_task_df = pd.merge(labor_by_task_df, rep_task_df, on='repair-task-id')
  labor_by_emp_df = rep_step_df[['emp-id', 'repair-step-labor-minutes', 'repair-step-labor-cost']].groupby('emp-id').sum().reset_index()

  #############
  ### Parts ###
  #############
  part_cost = part_df.loc[(part_df['repair-task-id'].isin(selected_rep_task))]['part-total-cost'].sum()

  #################
  ### Dashboard ###
  #################
  
  ## KPIs
  ## Labor Cost
  col = st.columns(3)
  
  with col[0]:
    # Total Labor Cost
    st.metric('Total Labor Cost', value=f"${labor_by_task_df['repair-step-labor-cost'].sum():,.0f}")
  with col[1]:
    # Total Labor Hour
    st.metric('Total Labor Hour', value=f"{labor_by_task_df['repair-step-labor-minutes'].sum() / 60:,.1f}hr")
  with col[2]:
    # Total Part Cost
    st.metric('Total Part Cost', value=f'${part_cost:,.0f}')

  ## Charts
  # Repair in and out date range chart
  st.markdown('#### Repair Task In/Out Date')
  fig = go.Figure()
  for _, row in rep_task_df.iterrows():
    date_in = row['repair-task-date-in']
    # check if out date is available
    if type(row['repair-task-date-out']) != pd._libs.tslibs.timestamps.Timestamp:
      date_out = datetime.date.today()
    else:
      date_out = row['repair-task-date-out']
      
    fig.add_trace(go.Scatter(
      x=[date_in, date_out],
      y=[str(row['repair-task-id']), str(row['repair-task-id'])],
      mode='lines',
      name=row['repair-task-id']
    ))
  fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), dragmode='pan',
                    xaxis_title='Date', yaxis_title='Task ID')
  st.plotly_chart(fig, use_container_width=True)
  
  # Labor cost graph
  col = st.columns(2)
  with col[0]:
    # by Task id
    st.markdown('#### Labor Cost by Task')
  
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    fig.add_trace(
        go.Bar(x=labor_by_task_df['repair-task-id'], y=labor_by_task_df['repair-step-labor-cost'], name='Labor Cost'),
        secondary_y=False,
    )
    fig.update_traces(text=[f'${v:,.0f}' for v in fig.data[0].y])
    fig.add_trace(
        go.Scatter(x=labor_by_task_df['repair-task-id'], y=labor_by_task_df['repair-step-labor-minutes'], name='Labor Time'),
        secondary_y=True,
    )
    # fig.update_traces(text=[f'{v:,.0f}min' for v in fig.data[0].y])
    fig.update_yaxes(range=[0, labor_by_task_df['repair-step-labor-cost'].max()+1], row=1, col=1,
                     secondary_y=False)
    fig.update_yaxes(range=[0, labor_by_task_df['repair-step-labor-minutes'].max()+1], row=1, col=1,
                     secondary_y=True)
    fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), dragmode='pan',
                      yaxis1_title='Labor Cost ($)', yaxis2_title='Labor Time (min)')
    st.plotly_chart(fig, use_container_width=True)
  
  with col[1]:
    # by Employee
    st.markdown('#### Labor Cost by Employee')

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    fig.add_trace(
        go.Bar(x=labor_by_emp_df['emp-id'].astype(str), y=labor_by_emp_df['repair-step-labor-cost'], name='Labor Cost'),
        secondary_y=False,
    )
    fig.update_traces(text=[f'${v:,.0f}' for v in fig.data[0].y])
    fig.add_trace(
        go.Scatter(x=labor_by_emp_df['emp-id'].astype(str), y=labor_by_emp_df['repair-step-labor-minutes'], name='Labor Time'),
        secondary_y=True,
    )
    # fig.update_traces(text=[f'{v:,.0f}min' for v in fig.data[0].y])
    fig.update_yaxes(range=[0, labor_by_emp_df['repair-step-labor-cost'].max()+1], row=1, col=1,
                     secondary_y=False)
    fig.update_yaxes(range=[0, labor_by_emp_df['repair-step-labor-minutes'].max()+1], row=1, col=1,
                     secondary_y=True)
    fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1), dragmode='pan',
                      yaxis1_title='Labor Cost ($)', yaxis2_title='Labor Time (min)')
    st.plotly_chart(fig, use_container_width=True)

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
