import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
 
st.set_page_config(page_title="Expense Tracker v2", layout="centered")
st.title("💰 บันทึกรายจ่ายออนไลน์")
 
# สร้างการเชื่อมต่อ (มันจะไปดึงค่าจาก Secrets ที่เราตั้งไว้)
conn = st.connection("gsheets", type=GSheetsConnection)
 
# อ่านข้อมูลล่าสุด
df = conn.read(ttl=0) # ttl=0 คือให้ดึงใหม่ทุกครั้ง ไม่ใช้แคช
 
with st.expander("➕ เพิ่มรายการใหม่"):
    date = st.date_input("วันที่", datetime.now())
    desc = st.text_input("รายการ")
    t_type = st.selectbox("ประเภท", ["รายรับ", "รายจ่าย"])
    amount = st.number_input("จำนวนเงิน (บาท)", min_value=0.0)
    
    if st.button("บันทึกข้อมูล"):
        if desc and amount > 0:
            # สร้าง Dataframe ใหม่จากข้อมูลที่กรอก
            new_data = pd.DataFrame([{
                "Date": date.strftime("%d/%m/%Y"),
                "Description": desc,
                "Type": t_type,
                "Amount": amount
            }])
            
            # รวมข้อมูลเดิมเข้ากับข้อมูลใหม่
            updated_df = pd.concat([df, new_data], ignore_index=True)
            
            # สั่ง Update กลับไปที่ Sheets
            conn.update(data=updated_df)
            st.success("บันทึกสำเร็จ!")
            st.rerun()
        else:
            st.warning("กรุณากรอกข้อมูลให้ครบถ้วน")
 
# แสดงผลสรุป
if not df.empty:
    income = df[df['Type'] == "รายรับ"]['Amount'].sum()
    expense = df[df['Type'] == "รายจ่าย"]['Amount'].sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("รายรับ", f"{income:,.2f}")
    c2.metric("รายจ่าย", f"{expense:,.2f}")
    c3.metric("คงเหลือ", f"{income-expense:,.2f}")
    
    st.dataframe(df, use_container_width=True)