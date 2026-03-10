import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- จัดการฐานข้อมูล ---
DB_NAME = 'monthly_finance.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # เพิ่มคอลัมน์ month_year เพื่อใช้สำหรับกรองข้อมูลโดยเฉพาะ
    c.execute('''CREATE TABLE IF NOT EXISTS finance 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, description TEXT, type TEXT, amount REAL, month_year TEXT)''')
    conn.commit()
    conn.close()

def add_data(date_obj, desc, t_type, amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    date_str = date_obj.strftime("%d/%m/%Y")
    month_year = date_obj.strftime("%m/%Y") # เก็บค่า เช่น 03/2026
    c.execute("INSERT INTO finance (date, description, type, amount, month_year) VALUES (?,?,?,?,?)",
              (date_str, desc, t_type, amount, month_year))
    conn.commit()
    conn.close()

def load_filtered_data(month_year):
    conn = sqlite3.connect(DB_NAME)
    query = f"SELECT * FROM finance WHERE month_year = '{month_year}'"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# --- ส่วนหน้าตาแอป (UI) ---
st.set_page_config(page_title="Monthly Tracker", layout="centered")
st.title("📅 บันทึกรายจ่ายแยกรายเดือน")

init_db()

# 1. ส่วนบันทึกข้อมูล (ปุ่มกดเพื่อขยาย)
with st.expander("➕ เพิ่มรายการใหม่"):
    date = st.date_input("เลือกวันที่", datetime.now())
    desc = st.text_input("ชื่อรายการ")
    t_type = st.selectbox("ประเภท", ["รายรับ", "รายจ่าย"])
    amount = st.number_input("จำนวนเงิน (บาท)", min_value=0.0, step=10.0)
    
    if st.button("บันทึก"):
        if desc:
            add_data(date, desc, t_type, amount)
            st.success(f"บันทึก '{desc}' เรียบร้อยแล้ว!")
            st.rerun()
        else:
            st.warning("กรุณากรอกชื่อรายการ")

st.divider()

# 2. ส่วนเลือกเดือนเพื่อดูข้อมูล
st.subheader("🔍 เลือกเดือนที่ต้องการดู")
current_month_year = datetime.now().strftime("%m/%Y")
selected_month = st.text_input("ระบุเดือน/ปี (เช่น 03/2026)", value=current_month_year)

# ดึงข้อมูลเฉพาะเดือนที่เลือก
df = load_filtered_data(selected_month)

if not df.empty:
    # 3. สรุปยอดเฉพาะเดือนนั้นๆ
    income = df[df['type'] == "รายรับ"]['amount'].sum()
    expense = df[df['type'] == "รายจ่าย"]['amount'].sum()
    balance = income - expense

    # แสดง Card สรุปผล
    c1, c2, c3 = st.columns(3)
    c1.metric("รายรับเดือนนี้", f"{income:,.2f} ฿")
    c2.metric("รายจ่ายเดือนนี้", f"-{expense:,.2f} ฿")
    c3.metric("คงเหลือ", f"{balance:,.2f} ฿")

    # แสดงตารางข้อมูลของเดือนนั้น
    st.write(f"### รายละเอียดของเดือน {selected_month}")
    # ปรับปรุงตารางให้ดูง่ายขึ้น
    display_df = df[['date', 'description', 'type', 'amount']]
    st.dataframe(display_df, use_container_width=True)
else:
    st.info(f"ยังไม่มีข้อมูลของเดือน {selected_month}")