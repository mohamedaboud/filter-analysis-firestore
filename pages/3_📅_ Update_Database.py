import pandas as pd
import streamlit as st
import datetime
from datetime import datetime, time
import plotly.express as px
from streamlit_extras.colored_header import colored_header
import sqlalchemy
from sqlalchemy import create_engine, text
from streamlit_extras.tags import tagger_component
from annotated_text import annotated_text, annotation
import random

st.set_page_config(page_title = "Update Database", layout="wide")
st.title(':watermelon: Update Database')

db_name='filtersdb'
database_table='sitesdatabase'
engine = create_engine(f"mysql+pymysql://root@localhost/{db_name}?charset=utf8mb4")
colors= ['lightblue', 'orange', 'bluegreen', 'blue', 'violet', 'red', 'green', 'yellow']

#======= Retrieve Current Data ========#

database_query= f'SELECT `UploadTime` FROM {database_table}'
database_uploade_time = pd.read_sql(database_query, engine)
database_last_update_datetime = pd.to_datetime(database_uploade_time['UploadTime'].unique(), format='%m/%d/%y %H:%M:%S')
tagger_component(
    "",
    [f'Database last update: {database_last_update_datetime[0]}'],
    color_name= random.sample(colors, 1)
)

annotated_text(annotation("Database last update", f'{database_last_update_datetime[0]}', background_color="red"))

#======= Database Input Form ========#
with st.form("database_form"):
   st.write("Update Database")
   uploaded_file=st.file_uploader('Upload The File')
   submitted = st.form_submit_button("Submit")
   if uploaded_file is not None:
    if submitted:
        db_df=pd.read_excel(io=uploaded_file, engine= 'openpyxl', skiprows=0, usecols='A:K')

        #======= Change columns names ========#
        db_df.columns = ['SiteId', 'Office', 'PowerSource', 'OnAir', 'Vendor', '2G_Cells', '3G_Cells', '4G_Cells', 'All_Cells', 'Cascaded', 'CascadedSites']

        #======= Create UploadTime column ========#
        db_df['UploadTime'] = pd.Timestamp.now()

        #======= Update Database ========#
        db_df.to_sql(database_table, engine, if_exists='replace', index=False)
        