"""
Dependencies
"""
import streamlit as st
import pkg.support.funcs as funcs
import datetime
import numpy as np
import math


def main():
  veh_df = funcs.get_vehicles_data()
  part_df = funcs.get_parts_data()
  rep_step_df = funcs.get_repair_steps_data()
  rep_task_df = funcs.get_repair_tasks_data()
  
  task_vin_dict = {task:vin for task, vin in zip(rep_task_df['repair-task-id'], rep_task_df['vin'])}
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
  option_list_model = list(veh_df['vehicle-model'].unique())
  selected_model = st.sidebar.multiselect('Select Model', option_list_model, default=option_list_model)

  ### Model year selector
  st.sidebar.subheader('Vehicle Year')
  option_list_year = sorted(list(veh_df['vehicle-year'].unique()))
  selected_year = st.sidebar.multiselect('Select Year', option_list_year, default=option_list_year)
  
  ### Vehicle Price range selector
  veh_price_min, veh_price_max = st.sidebar.slider('Select Price Range ($)', 
                                                   math.floor(veh_df['vehicle-purchase-price'].min()), 
                                                   math.ceil(veh_df['vehicle-purchase-price'].max()), 
                                                   (math.floor(veh_df['vehicle-purchase-price'].min()), math.ceil(veh_df['vehicle-purchase-price'].max())))
  ###############
  ### Revenue ###
  ###############
  """
  Subscription
  """
  """
  Sold/Salvaged Vehicle/Part
  """
  """
  Additional Revenue
  """
  """
  Dashboard
  """
  st.subheader('Revenue')

  col = st.columns(4)
  with col[0]:
    # Total Revenue
    label = 'Total Revenue'
    value = 8000
    target = 20000
    delta = 0.1
    st.markdown(funcs.format_kpi_metric_1(label, value, target, f'{delta:.1%}', delta), unsafe_allow_html=True)

  with col[1]:
    value = 5000
    target = 7000
    delta = 1000
    st.metric(label='Subscription', value=f'${value:,.0f}', delta=delta)

  with col[2]:
    value = 1200
    delta = 1000
    st.metric(label='Sold/Salvaged Vehicle/Part', value=f'${value:,.0f}', delta=delta)
  
  with col[3]:
    value = 800
    delta = -200
    st.metric(label='Additional Revenue', value=f'${value:,.0f}', delta=delta)
  
  ###############
  ###  Cost   ###
  ###############

  """
  Vehicle Count
  """
  if start_date < end_date:
    veh_count = len(veh_df.loc[(veh_df['vehicle-purchase-date'] >= np.datetime64(start_date)) &
                              (veh_df['vehicle-purchase-date'] <= np.datetime64(end_date)) &
                              (veh_df['vehicle-model'].isin(selected_model)) &
                              (veh_df['vehicle-year'].isin(selected_year)) &
                              (veh_df['vehicle-purchase-price'] >= veh_price_min) &
                              (veh_df['vehicle-purchase-price'] <= veh_price_max) 
                              ])
    pre_veh_count = len(veh_df.loc[(veh_df['vehicle-purchase-date'] >= np.datetime64(pre_start_date)) & 
                                  (veh_df['vehicle-purchase-date'] <= np.datetime64(pre_end_date)) &
                                  (veh_df['vehicle-model'].isin(selected_model)) &
                                  (veh_df['vehicle-year'].isin(selected_year)) &
                                  (veh_df['vehicle-purchase-price'] >= veh_price_min) &
                                  (veh_df['vehicle-purchase-price'] <= veh_price_max) 
                                  ])

    if pre_veh_count == 0:
      veh_count_percent = '-'  
    else:
      veh_count_percent = f'{(veh_count-pre_veh_count)/pre_veh_count*100:.0f}'
  
  """
  Vehicle purchase cost
  """
  if start_date < end_date:
    veh_price = veh_df.loc[(veh_df['vehicle-purchase-date'] >= np.datetime64(start_date)) &
                            (veh_df['vehicle-purchase-date'] <= np.datetime64(end_date)) &
                            (veh_df['vehicle-model'].isin(selected_model)) &
                            (veh_df['vehicle-year'].isin(selected_year)) &
                            (veh_df['vehicle-purchase-price'] >= veh_price_min) &
                            (veh_df['vehicle-purchase-price'] <= veh_price_max) 
                          ]['vehicle-purchase-price'].sum()
    pre_veh_price = veh_df.loc[(veh_df['vehicle-purchase-date'] >= np.datetime64(pre_start_date)) & 
                                (veh_df['vehicle-purchase-date'] <= np.datetime64(pre_end_date)) &
                                (veh_df['vehicle-model'].isin(selected_model)) &
                                (veh_df['vehicle-year'].isin(selected_year)) &
                                (veh_df['vehicle-purchase-price'] >= veh_price_min) &
                                (veh_df['vehicle-purchase-price'] <= veh_price_max) 
                              ]['vehicle-purchase-price'].sum()

    if pre_veh_price == 0:
      veh_price_percent = '-'  
    else:
      veh_price_percent = f'{(veh_price-pre_veh_price)/pre_veh_price*100:.0f}'

  # Selected VINs
  selected_vin = veh_df.loc[(veh_df['vehicle-purchase-date'] >= np.datetime64(start_date)) &
                            (veh_df['vehicle-purchase-date'] <= np.datetime64(end_date)) &
                            (veh_df['vehicle-model'].isin(selected_model)) &
                            (veh_df['vehicle-year'].isin(selected_year)) &
                            (veh_df['vehicle-purchase-price'] >= veh_price_min) &
                            (veh_df['vehicle-purchase-price'] <= veh_price_max) 
                           ]['vin']
  # Selected Repair Tasks
  selected_rep_task = rep_task_df.loc[(rep_task_df['repair-task-date-in'] >= np.datetime64(start_date)) &
                                      (rep_task_df['repair-task-date-in'] <= np.datetime64(end_date)) &
                                      (rep_task_df['repair-task-id'].isin([vin_task_dict[v] for v in selected_vin]))
                                     ]['repair-task-id']

  """
  Labor Cost
  """
  # This part has to be improved when we getting repair-task-id and datetime information
  labor_cost = rep_step_df.loc[rep_step_df['repair-task-id'].isin(selected_rep_task)]['repair-step-labor-cost'].sum()
  # labor_hr = rep_step_df.loc[rep_step_df['repair-task-id'].isin(selected_rep_task)]['repair-step-labor-minutes'].sum()/60
  
  """
  Part Cost
  """
  part_cost = part_df.loc[(part_df['repair-task-id'].isin(selected_rep_task))]['part-total-cost'].sum()

  """
  Dashboard
  """
  st.subheader('Cost')
  col = st.columns(4)

  ### Vehicle purchase cost
  with col[0]:
    pass
    st.markdown(funcs.format_kpi_metric_1(label='Total Cost', value=f'${veh_price+labor_cost+part_cost:,.0f}', target=f'{30000:,.0f}', delta=0, delta_dir=0), unsafe_allow_html=True)
  with col[1]:
    if start_date < end_date:
      st.metric(label='Vehicle Purchase', value=f'${veh_price:,.0f}')
    else:
      st.metric(label='Vehicle Purchase', value='-')

  ### Labor cost
  with col[2]:
    st.metric(label='Labor Cost', value=f'${labor_cost:,.0f}')

  ### Part cost
  with col[3]:
    st.metric(label='Part Cost', value=f'${part_cost:,.0f}')
    
  ##########################
  ### Vehicles/Customers ###
  ##########################
  """
  Vehicle Mileage
  """
  """
  Vehicle Uptime
  """
  """
  Avg Tenure
  """
  """
  Payment
  """
  """
  Dashboard
  """
  st.subheader('Vehicles/Customers')

  col = st.columns(4)
  ### vehicle count
  with col[0]:
    if start_date < end_date:
      st.metric(label='Vehicle Count', value=veh_count)
    else:
      st.metric(label='Vehicle Count', value='-')

  with col[1]:
    value = 200
    delta = 30
    st.metric(label='Vehicle Mileage', value=f'{value:,.0f}mi')

  with col[2]:
    value = 70
    delta = 10
    st.metric(label='Vehicle Uptime', value=f'{value:,.0f}hrs')

  with col[3]:
    value = 96
    delta = -2
    st.metric(label='Payment', value=f'{value:,.1f}%')


  