import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- จัดการฐานข้อมูล ---
DB_NAME = 'finance_v3.db'

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
    c.execute("INSERT INTO finance (date, description, type, amount, month_year) VALUES (?,?,?,?,?)",
              (date_obj.strftime("%Y-%m-%d"), desc, t_type, amount, date_obj.strftime("%m/%Y")))
    conn.commit()
    conn.close()

def update_data(id, date_obj, desc, t_type, amount):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE finance SET date=?, description=?, type=?, amount=?, month_year=? WHERE id=?",
              (date_obj.strftime("%Y-%m-%d"), desc, t_type, amount, date_obj.strftime("%m/%Y"), id))
    conn.commit()
    conn.close()

def delete_data(id):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM finance WHERE id=?", (id,))
    conn.commit()
    conn.close()

def load_all_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM finance ORDER BY date DESC", conn)
    conn.close()
    return df

# --- UI ---
st.set_page_config(page_title="Finance Manager", layout="wide")
init_db()
all_df = load_all_data()

st.title("💰 จัดการรายรับ-รายจ่าย (แก้ไขข้อมูลได้)")

# --- ส่วนที่ 1: เพิ่มข้อมูลใหม่ (เลือกวันที่แบบปฏิทิน) ---
with st.expander("➕ เพิ่มรายการใหม่"):
    with st.form("add_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        new_date = c1.date_input("วันที่", datetime.now()) # เลือกจากปฏิทิน
        new_desc = c2.text_input("รายการ")
        new_type = c3.selectbox("ประเภท", ["รายรับ", "รายจ่าย"])
        new_amount = c4.number_input("จำนวนเงิน", min_value=0.0)
        if st.form_submit_button("บันทึก"):
            if new_desc:
                add_data(new_date, new_desc, new_type, new_amount)
                st.rerun()

st.divider()

# --- ส่วนที่ 2: ตารางข้อมูลและการแก้ไข ---
if not all_df.empty:
    # เลือกเดือนที่จะดู
    months = sorted(all_df['month_year'].unique(), reverse=True)
    sel_month = st.sidebar.selectbox("📅 เลือกเดือนที่ต้องการ", months)
    
    st.subheader(f"รายการประจำเดือน {sel_month}")
    view_df = all_df[all_df['month_year'] == sel_month]

    for index, row in view_df.iterrows():
        with st.container():
            col_d, col_desc, col_t, col_a, col_edit, col_del = st.columns([1.5, 3, 1.5, 1.5, 1, 1])
            
            col_d.write(row['date'])
            col_desc.write(row['description'])
            col_t.write(row['type'])
            col_a.write(f"{row['amount']:,.2f}")
            
            # ปุ่มแก้ไข
            if col_edit.button("📝 แก้ไข", key=f"edit_{row['id']}"):
                st.session_state[f"editing_{row['id']}"] = True

            # ปุ่มลบ
            if col_del.button("🗑️ ลบ", key=f"del_{row['id']}"):
                delete_data(row['id'])
                st.rerun()

            # ฟอร์มแก้ไข (จะปรากฏขึ้นเมื่อกดปุ่มแก้ไข)
            if st.session_state.get(f"editing_{row['id']}", False):
                with st.form(key=f"form_{row['id']}"):
                    st.write("--- แก้ไขข้อมูล ---")
                    u_date = st.date_input("วันที่", datetime.strptime(row['date'], "%Y-%m-%d"))
                    u_desc = st.text_input("รายการ", value=row['description'])
                    u_type = st.selectbox("ประเภท", ["รายรับ", "รายจ่าย"], index=0 if row['type']=="รายรับ" else 1)
                    u_amount = st.number_input("จำนวนเงิน", value=row['amount'])
                    
                    c_save, c_cancel = st.columns(2)
                    if c_save.form_submit_button("บันทึกการแก้ไข"):
                        update_data(row['id'], u_date, u_desc, u_type, u_amount)
                        st.session_state[f"editing_{row['id']}"] = False
                        st.rerun()
                    if c_cancel.form_submit_button("ยกเลิก"):
                        st.session_state[f"editing_{row['id']}"] = False
                        st.rerun()
        st.write("---")
else:
    st.info("ยังไม่มีข้อมูล กรุณาเพิ่มรายการใหม่")