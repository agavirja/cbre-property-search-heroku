import streamlit as st
import pandas as pd
import mysql.connector as sql
from sqlalchemy import create_engine 

@st.cache_data
def point2POT(latitud,longitud):
    
    user        = st.secrets["user_bigdata"]
    password    = st.secrets["password_bigdata"]
    host        = st.secrets["host_bigdata_lectura"]
    schema      = 'pot'
    result      = {}
    
    if latitud is not None and longitud is not None: 
        db_connection = sql.connect(user=user, password=password, host=host, database=schema)
        cursor        = db_connection.cursor()
        cursor.execute("SHOW TABLES FROM pot;")
        tables = cursor.fetchall()
        cursor.close()
        db_connection.close()
        engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{schema}')
        for table in tables:
            try:
                table = table[0]
                datapaso = pd.read_sql_query(f"SELECT * FROM {schema}.{table} WHERE ST_CONTAINS(geometry, POINT({longitud},{latitud}))" , engine)
                if not datapaso.empty:
                    if 'geometry' in datapaso: del datapaso['geometry']
                    result.update({table:datapaso.to_dict(orient='records')})
            except: pass
        engine.dispose()
    return result
