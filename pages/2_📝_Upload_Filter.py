import pandas as pd
import streamlit as st
import datetime
from datetime import datetime, time
from streamlit_extras.colored_header import colored_header
import sqlalchemy
from sqlalchemy import create_engine, text
from streamlit_extras.tags import tagger_component
import random
from google.cloud import firestore

st.set_page_config(page_title = "Upload Filter", page_icon=':bar_chart:', layout="wide")
st.title(':watermelon: Upload Filter')


dbs = firestore.Client.from_service_account_json("pages/firestore-key.json")
doc_ref = dbs.collection("filters").document("t3irKcUZTJvVgrGkd22m")
doc = doc_ref.get()

doc.id
d= doc.to_dict()
d

db_name='filtersdb'
filter_table='filters'
engine = create_engine(f"mysql+pymysql://root@localhost/{db_name}?charset=utf8mb4")
colors= ['lightblue', 'orange', 'bluegreen', 'blue', 'violet', 'red', 'green', 'yellow']*10
violet_color= ['violet',]*60
#======= Retrieve Current Data ========#
if st.button("Show Current Filters", type="primary"):
    filters_query= f'SELECT * FROM {filter_table}'
    filters = pd.read_sql(filters_query, engine)
    tagger_component(
        "",
        filters['FilterIdentifier'].unique(),
        color_name= random.sample(colors, len(filters['FilterIdentifier'].unique()))
    )

#======= Filters Input Form ========#
with st.form("my_form"):
   st.write("New Filter Upload")
   d = st.date_input("Select Date of Filter")
   t = st.slider("Select Time of Filter", min_value=time(00, 00), max_value=time(23, 59))
   uploaded_file=st.file_uploader('Upload The File')



   submitted = st.form_submit_button("Submit")
   if uploaded_file is not None:
    # st.write('Date:', d)
    # st.write('Time:', t)
    if submitted:
        # st.write(uploaded_file.file_id)
        # st.write(uploaded_file.name)
        # st.write(uploaded_file.size)
        # st.write(uploaded_file.type)
        n_df=pd.read_excel(io=uploaded_file, engine= 'xlrd', skiprows=1, usecols='B:H')
        #======= Change columns names ========#
        n_df.columns = ['SiteName', 'Severity', 'AlarmName', 'AlarmTime', 'AlarmId', 'AlarmSn', 'AlarmInfo']
        #======= Delete NA values in SiteName ========#
        n_df=n_df.dropna(subset=['SiteName'])

        #======= Change SiteName type to String ========#
        n_df = n_df.astype({'SiteName':'string'})

        #======= Create SiteId column ========#
        def siteIdFunc(siteName):
            if 'UPP' in siteName:
                start= siteName.find('UPP')
                end= start+7
                return siteName[start:end]
            else: 
                return 'NA'

        n_df['SiteId'] = n_df.apply(lambda row : siteIdFunc(row['SiteName']), axis = 1)

        #======= Create FormattedDateTime column ========#
        n_df['FormattedDatetime'] = pd.to_datetime(n_df.AlarmTime.str[3:5]+'/'+n_df.AlarmTime.str[:2]+'/'+n_df.AlarmTime.str[6:8]+ ' '+ n_df.AlarmTime.str[9:20], format='%m/%d/%y %H:%M:%S')
        #n_df= n_df.sort_values(by=['FormattedDatetime'], ascending=False)
        n_df= n_df.sort_values(by=['FormattedDatetime'])

        #======= Create FilterIdentifier column ========#
        n_df['FilterIdentifier'] = f'FIL-{d}-{t}'

        #======= Create UploadTime column ========#
        n_df['UploadTime'] = pd.Timestamp.now()

        # #======= Create DownHours column ========#
        # n_df['DownHours'] = (n_df.CurrentTime - n_df.FormattedDatetime) / pd.Timedelta(hours=1)
        # n_df = pd.read_sql('select * from filter_1600', engine)
        # #======= Append to Database ========#
        

        #======= Validate Before Update Database ========#
        query= f'SELECT * FROM {filter_table} WHERE `FilterIdentifier` = "FIL-{d}-{t}"'
        result = pd.read_sql(query, engine)
        if result.empty:
            n_df.to_sql(filter_table, engine, if_exists='append', index=False)
            st.success('Data Added', icon="✅")
            st.cache_data.clear()
            # filters_query= f'SELECT * FROM {filter_table}'
            # filters = pd.read_sql(filters_query, engine)
            # tagger_component("",filters['FilterIdentifier'].unique(),color_name= random.sample(colors, len(filters['FilterIdentifier'].unique())))
            result.shape
        else:
            st.error('Data Exists', icon="🚨")
