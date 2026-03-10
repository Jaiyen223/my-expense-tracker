import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- ส่วนจัดการฐานข้อมูล (SQLite) ---
DB_NAME = 'my_finance.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS finance 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, description TEXT, type TEXT, amount REAL)''')
    conn.commit()
    conn.close()

def add_data(date, desc, t_type, amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO finance (date, description, type, amount) VALUES (?,?,?,?)",
              (date, desc, t_type, amount))
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM finance", conn)
    conn.close()
    return df

# --- ส่วนหน้าตาแอป (UI) ---
st.set_page_config(page_title="Easy Expense Tracker", layout="centered")
st.title("💰 บันทึกรายรับ-รายจ่าย (Easy)")

init_db() # สร้างฐานข้อมูลตอนเริ่ม

# ส่วนกรอกข้อมูล
with st.form("my_form", clear_on_submit=True):
    date = st.date_input("วันที่", datetime.now())
    desc = st.text_input("รายการ")
    t_type = st.selectbox("ประเภท", ["รายรับ", "รายจ่าย"])
    amount = st.number_input("จำนวนเงิน (บาท)", min_value=0.0)
    submit = st.form_submit_button("บันทึก")

    if submit:
        if desc:
            add_data(date.strftime("%d/%m/%Y"), desc, t_type, amount)
            st.success("บันทึกข้อมูลแล้ว!")
            st.rerun()
        else:
            st.warning("กรุณากรอกรายการ")

# ส่วนแสดงผลสรุป
df = load_data()

if not df.empty:
    income = df[df['type'] == "รายรับ"]['amount'].sum()
    expense = df[df['type'] == "รายจ่าย"]['amount'].sum()
    balance = income - expense

    col1, col2, col3 = st.columns(3)
    col1.metric("รายรับ", f"{income:,.2f}")
    col2.metric("รายจ่าย", f"{expense:,.2f}")
    col3.metric("คงเหลือ", f"{balance:,.2f}")

    st.write("### รายการล่าสุด")
    st.dataframe(df.sort_values(by='id', ascending=False), use_container_width=True)
else:
    st.info("ยังไม่มีข้อมูลบันทึก")