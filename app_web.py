import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Expense Tracker v2", layout="centered")
st.title("💰 บันทึกรายจ่าย (Google Sheets)")

# 1. เชื่อมต่อ Google Sheets
# หมายเหตุ: นำลิงก์จากหน้า Google Sheets ของคุณมาใส่ที่นี่
url = "https://docs.google.com/spreadsheets/d/1RdQOVOD8jNgiGEJ3aSzS-mYyiv40V3YG_GP-InxpFtM/edit?usp=drivesdk"

conn = st.connection("gsheets", type=GSheetsConnection)

# ฟังก์ชันอ่านข้อมูล
def load_data():
    return conn.read(spreadsheet=url, usecols=[0, 1, 2, 3])

df = load_data()

# --- ส่วนของการกรอกข้อมูล ---
with st.expander("➕ เพิ่มรายการใหม่"):
    date = st.date_input("วันที่", datetime.now())
    desc = st.text_input("รายการ")
    t_type = st.selectbox("ประเภท", ["รายรับ", "รายจ่าย"])
    amount = st.number_input("จำนวนเงิน (บาท)", min_value=0.0)
    
    if st.button("บันทึกข้อมูล"):
        if desc:
            # เตรียมข้อมูลใหม่
            new_row = pd.DataFrame([[date.strftime("%d/%m/%Y"), desc, t_type, amount]], 
                                   columns=['Date', 'Description', 'Type', 'Amount'])
            # รวมข้อมูลเก่าและใหม่
            updated_df = pd.concat([df, new_row], ignore_index=True)
            # อัปเดตกลับไปยัง Google Sheets
            conn.update(spreadsheet=url, data=updated_df)
            st.success("บันทึกลง Google Sheets เรียบร้อย!")
            st.rerun()

# --- ส่วนของการแสดงผล ---
if not df.empty:
    # สรุปยอด
    income = df[df['Type'] == "รายรับ"]['Amount'].sum()
    expense = df[df['Type'] == "รายจ่าย"]['Amount'].sum()
    
    col1, col2 = st.columns(2)
    col1.metric("รายรับรวม", f"{income:,.2f}")
    col2.metric("รายจ่ายรวม", f"{expense:,.2f}")

    st.write("### รายการทั้งหมด")
    st.dataframe(df, use_container_width=True)
else:
    st.info("ยังไม่มีข้อมูล")