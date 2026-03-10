import streamlit as st
import pandas as pd
from datetime import datetime
import os

FILENAME = 'finance_data.csv'

# ตั้งค่าหน้าเว็บ
st.set_page_config(page_title="My Expense Tracker", layout="centered")
st.title("💰 บันทึกรายรับ-รายจ่าย")

# ฟังก์ชันโหลดข้อมูล
def load_data():
    if os.path.exists(FILENAME):
        return pd.read_csv(FILENAME)
    return pd.DataFrame(columns=['Date', 'Description', 'Type', 'Amount'])

# --- ส่วนของการกรอกข้อมูล (Sidebar หรือ Expander) ---
with st.expander("➕ เพิ่มรายการใหม่"):
    date = st.date_input("วันที่", datetime.now())
    desc = st.text_input("รายการ")
    t_type = st.selectbox("ประเภท", ["รายรับ", "รายจ่าย"])
    amount = st.number_input("จำนวนเงิน (บาท)", min_value=0.0, step=10.0)
    
    if st.button("บันทึกข้อมูล"):
        if desc:
            new_data = pd.DataFrame([[date.strftime("%d/%m/%Y"), desc, t_type, amount]], 
                                    columns=['Date', 'Description', 'Type', 'Amount'])
            if os.path.exists(FILENAME):
                new_data.to_csv(FILENAME, mode='a', header=False, index=False)
            else:
                new_data.to_csv(FILENAME, index=False)
            st.success("บันทึกสำเร็จ!")
            st.rerun()
        else:
            st.warning("กรุณากรอกชื่อรายการ")

# --- ส่วนของการแสดงผลและสรุป ---
df = load_data()

if not df.empty:
    # ตัวกรองรายเดือน
    all_months = df['Date'].str[-7:].unique() # ดึงค่า MM/YYYY
    selected_month = st.selectbox("📅 เลือกดูรายเดือน", all_months[::-1])
    
    # กรองข้อมูลตามเดือนที่เลือก
    filtered_df = df[df['Date'].str.contains(selected_month)]
    
    # คำนวณยอดรวม
    income = filtered_df[filtered_df['Type'] == "รายรับ"]['Amount'].sum()
    expense = filtered_df[filtered_df['Type'] == "รายจ่าย"]['Amount'].sum()
    balance = income - expense

    # แสดง Card สรุปผล
    col1, col2, col3 = st.columns(3)
    col1.metric("รายรับ", f"{income:,.2f} ฿")
    col2.metric("รายจ่าย", f"-{expense:,.2f} ฿", delta_color="inverse")
    col3.metric("คงเหลือ", f"{balance:,.2f} ฿")

    # แสดงตาราง
    st.dataframe(filtered_df, use_container_width=True)

    # ปุ่มลบข้อมูล (เลือกจาก Index)
    if st.checkbox("โหมดลบข้อมูล"):
        row_to_delete = st.number_input("ระบุลำดับ (Index) ที่ต้องการลบ", min_value=0, max_value=len(df)-1, step=1)
        if st.button("ยืนยันการลบ"):
            df = df.drop(df.index[row_to_delete])
            df.to_csv(FILENAME, index=False)
            st.error(f"ลบรายการที่ {row_to_delete} เรียบร้อย")
            st.rerun()
else:
    st.info("ยังไม่มีข้อมูลบันทึกในขณะนี้")