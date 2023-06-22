import pandas as pd
import geopandas as gpd
import os
import streamlit as st
import numpy as np
from scipy.ndimage import gaussian_filter
import requests
import json

import plotly
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import plotly.graph_objects as go

import shapefile
import datetime

HOME = '..\\'

def return_center():
  lat = 42.3827
  long=-83.49458
  zoom = 9
  return lat,long,zoom

def get_vehicles_data():
  """
  example:
    vin	vehicle-make	vehicle-model	vehicle-year	vehicle-purchase-source	vehicle-purchase-date	vehicle-purchase-price	vehicle-notes
    1FADP3F28DL247123	Ford	Focus	2013	SFG AUTO LLC	2/2/2023	6500	
    1FADP3K26GL284844	Ford	Focus	2016	Roger Beasley Mazda	2/3/2023	7307.27	
    1FADP3K25EL156818	Ford	Focus	2014	BBB Industries	2/9/2023	5900	
  """
  return pd.read_excel(f'{HOME}src\\data\\excel\\vehicles.xlsx', sheet_name='vehicles')

def get_people_data():
  """
  example:
    emp-id	emp-name	emp-email	emp-status	emp-role
    1	Craig Powers	cpower@ford.com	full-time	flexible
  """
  return pd.read_excel(f'{HOME}src\\data\\excel\\people.xlsx', sheet_name='people')

def get_parts_data():
  """
  example:
    part-id	repair-task-id	part-source	part-shipment	part-description	part-condition	part-price	part-quantity	part-price-overhead-percent	part-total-cost
    ACPZ 1012 H	1001	FCSD	10423317		new	0.64	16	20	12.288
    BM5Z 13008 F	1001				new	47.1	1	20	56.52
  """
  return pd.read_excel(f'{HOME}src\\data\\excel\\parts.xlsx', sheet_name='parts')

def get_repair_tasks_data():
  """
  example:
    repair-task-id	vin	repair-task-date-in	repair-task-time-in	repair-task-date-out	repair-task-time-out	claim-id	repair-task-time-elapsed-minutes	repair-task-notes
    1001	1FADP3F28DL247123	2/2/2023	8:00:00 AM					re-conditioning
    1002	1FADP3K26GL284844	2/3/2023	8:00:00 AM	3/29/2023	5:00:00 PM			re-conditioning
    1003	1FADP3K25EL156818	2/16/2023	8:00:00 AM	3/27/2023	5:00:00 PM			re-conditioning
  """
  return pd.read_excel(f'{HOME}src\\data\\excel\\repair-tasks.xlsx', sheet_name='repair-tasks')

def get_repair_steps_data():
  """
  example:
    repair-step-labor-minutes	repair-step-labor-cost	emp-id	notes	repair-step-sign-off-emp-id
    90	33.75	1		1
    90	33.75	1		1
    430	161.25	1		1
  """
  return pd.read_excel(f'{HOME}src\\data\\excel\\repair-steps.xlsx', sheet_name='repair-steps')

def get_checks_data():
  """
  example:
    check-id	vin	check-mechanical-score	check-cosmetic-score	check-cleanness-score	check-inspection-details-file	emp-id	check-mileage	check-notes	check-date-in	check-time-in	check-date-out	check-time-out	check-time-elapsed-minutes
  """
  return pd.read_excel(f'{HOME}src\\data\\excel\\checks.xlsx', sheet_name='checks')

def get_claim_data():
  """
  example:
    claim-id	claim-date	claim-description	claim-status	claim-cost-covered-by-insurance	claim-cost-not-covered-by-insurance
  """
  return pd.read_excel(f'{HOME}src\\data\\excel\\claims.xlsx', sheet_name='claims')

def get_trip_summary_data():
  return pd.read_csv(f'{HOME}src\\data\\scav\\ncvdvqaa_trip_sum_4g_na_usa_msi_vw_2023_04_12.csv')

def get_trip_sum_line_data():
  return shapefile.Reader(f'{HOME}src\\data\\scav\\test.shp')
  # return gpd.read_file(f'{HOME}src\\data\\scav\\test.shp')

def get_first_day_of_week(year, week_number):
  first_day = datetime.date.fromisocalendar(year, week_number, 1)
  return first_day


#################
### Dashboard ###
### Components ##
#################

def format_kpi_metric_1(label, value, target, delta, delta_dir=1):
  # data = [
  #  {'label':label,
  #  'sublabel':'',
  #  'range':[0, int(target*0.9), int(target)],
  #  'measures':[int(value*0.5), int(value)],
  #  'point':[int(target)]} 
  # ]
  # fig = ff.create_bullet(
  #   data, titles='label', subtitles='sublabel', markers='point',
  #   measures='measures', ranges='range', orientation='h',)
  # chart_html = fig.to_html(full_html=False)
  
  return f'''
      <div class="kpi_metric_1">
        <span style="font-size: 20px;color:black;">{label}</span><br>
        <span style="font-size: 16px;">(Target: {target})</span><br>
        <span style="font-size: 40px;">{value}</span><br>
        <span style="font-size: 30px; color: {'red' if delta_dir < 0 else 'blue' if delta_dir > 0 else 'black'}; font-weight: bold">{'&#8595' if delta_dir < 0 else '&#8593' if delta_dir > 0 else '-'}</span>
        <span style="font-size: 20px; color: {'red' if delta_dir < 0 else 'blue' if delta_dir > 0 else 'black'};">{delta}</span>
      </div>
  '''