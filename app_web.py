import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- จัดการฐานข้อมูล ---
DB_NAME = 'monthly_finance_v2.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS finance 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, description TEXT, type TEXT, amount REAL, month_year TEXT)''')
    conn.commit()
    conn.close()

def add_data(date_obj, desc, t_type, amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    date_str = date_obj.strftime("%d/%m/%Y")
    month_year = date_obj.strftime("%m/%Y")
    c.execute("INSERT INTO finance (date, description, type, amount, month_year) VALUES (?,?,?,?,?)",
              (date_str, desc, t_type, amount, month_year))
    conn.commit()
    conn.close()

def load_all_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM finance", conn)
    conn.close()
    return df

# --- UI ---
st.set_page_config(page_title="Finance Dashboard", layout="wide")
st.title("📊 สรุปและเปรียบเทียบรายรับ-รายจ่าย")

init_db()
all_df = load_all_data()

# --- ส่วนที่ 1: กราฟเปรียบเทียบรายเดือน (Dashboard) ---
if not all_df.empty:
    st.subheader("📈 กราฟเปรียบเทียบรายเดือน")
    
    # รวมข้อมูลตามเดือนและประเภท
    summary_df = all_df.groupby(['month_year', 'type'])['amount'].sum().reset_index()
    
    # สร้างกราฟแท่งเปรียบเทียบ
    fig = go.Figure()
    
    months = summary_df['month_year'].unique()
    for t in ["รายรับ", "รายจ่าย"]:
        data = summary_df[summary_df['type'] == t]
        fig.add_trace(go.Bar(
            x=data['month_year'],
            y=data['amount'],
            name=t,
            marker_color='#2ecc71' if t == "รายรับ" else '#e74c3c'
        ))

    fig.update_layout(barmode='group', xaxis_title="เดือน/ปี", yaxis_title="จำนวนเงิน (บาท)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("ยังไม่มีข้อมูลสำหรับแสดงกราฟ")

st.divider()

# --- ส่วนที่ 2: บันทึกและดูรายละเอียด ---
col_input, col_view = st.columns([1, 2])

with col_input:
    st.subheader("➕ เพิ่มรายการ")
    with st.form("input_form", clear_on_submit=True):
        date = st.date_input("วันที่", datetime.now())
        desc = st.text_input("รายการ")
        t_type = st.selectbox("ประเภท", ["รายรับ", "รายจ่าย"])
        amount = st.number_input("จำนวนเงิน", min_value=0.0)
        if st.form_submit_button("บันทึก"):
            if desc:
                add_data(date, desc, t_type, amount)
                st.success("บันทึกสำเร็จ!")
                st.rerun()

with col_view:
    st.subheader("🔍 ดูรายละเอียดรายเดือน")
    if not all_df.empty:
        available_months = all_df['month_year'].unique()
        sel_month = st.selectbox("เลือกเดือน", available_months[::-1])
        
        filtered_df = all_df[all_df['month_year'] == sel_month]
        
        inc = filtered_df[filtered_df['type'] == "รายรับ"]['amount'].sum()
        exp = filtered_df[filtered_df['type'] == "รายจ่าย"]['amount'].sum()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("รายรับ", f"{inc:,.2f}")
        m2.metric("รายจ่าย", f"{exp:,.2f}")
        m3.metric("คงเหลือ", f"{inc-exp:,.2f}")
        
        st.dataframe(filtered_df[['date', 'description', 'type', 'amount']], use_container_width=True)