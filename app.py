import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Tiệm Ăn Hạnh Phúc", page_icon="💃", layout="centered")

# Tùy chỉnh CSS cho lãng mạn và dễ dùng trên điện thoại
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #fffafb; }
    .stButton>button {
        width: 100%; border-radius: 25px; height: 3.5em;
        background: linear-gradient(45deg, #ff758c 0%, #ff7eb3 100%);
        color: white; border: none; font-weight: bold; font-size: 18px;
    }
    .order-box {
        padding: 20px; border-radius: 20px; border: 1px solid #ffcad4;
        background-color: white; margin-bottom: 15px;
        box-shadow: 5px 5px 15px rgba(255, 182, 193, 0.3);
    }
    .status-badge {
        padding: 5px 15px; border-radius: 50px; font-size: 14px; font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- KẾT NỐI DỮ LIỆU ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_foods():
    return conn.read(worksheet="Foods", ttl=0)

def get_orders():
    return conn.read(worksheet="Orders", ttl=0)

# --- GIAO DIỆN CHÍNH ---
st.title("👸 Chào Công chúa!")
st.write("Hôm nay em muốn người yêu mình nấu món gì nào?")

tab1, tab2 = st.tabs(["✨ Đặt món ngay", "📅 Lịch sử thực đơn"])

# --- TAB 1: ĐẶT MÓN ---
with tab1:
    with st.container():
        df_foods = get_foods()
        food_options = df_foods['FoodName'].tolist()
        
        chosen_food = st.selectbox("Chọn món em thèm:", food_options)
        
        col1, col2 = st.columns(2)
        with col1:
            date_val = st.date_input("Ngày hẹn")
        with col2:
            time_val = st.time_input("Giờ ăn")
            
        note_val = st.text_placeholder = st.text_area("Lời nhắn cho đầu bếp (VD: Ít cay, nhiều hành...)", height=100)
        
        if st.button("GỬI YÊU CẦU CHO ANH ❤️"):
            # Chuẩn bị dữ liệu mới
            new_row = pd.DataFrame([{
                "Time": datetime.now().strftime("%d/%m %H:%M"),
                "FoodName": chosen_food,
                "Appointment": f"{date_val} {time_val}",
                "Note": note_val,
                "Status": "Đang chờ" # Bạn sẽ sửa chữ này trên Google Sheet
            }])
            
            # Ghi vào Sheet
            df_existing = get_orders()
            updated_df = pd.concat([df_existing, new_row], ignore_index=True)
            conn.update(worksheet="Orders", data=updated_df)
            
            st.balloons()
            st.success("Yêu cầu đã được gửi! Đợi anh chuẩn bị nhé 👨‍🍳")

# --- TAB 2: THEO DÕI TRẠNG THÁI ---
with tab2:
    st.subheader("Trạng thái bếp nấu")
    df_orders = get_orders()
    
    if df_orders.empty:
        st.write("Em chưa đặt món nào cả 🌸")
    else:
        # Đảo ngược để hiện đơn mới nhất lên đầu
        for _, row in df_orders.iloc[::-1].iterrows():
            # Quyết định màu sắc dựa trên status bạn nhập ở Sheet
            status = str(row['Status'])
            color = "#f39c12" # Cam cho "Đang chờ"
            if "nhận" in status.lower() or "nấu" in status.lower():
                color = "#3498db" # Xanh dương
            elif "xong" in status.lower() or "thành" in status.lower():
                color = "#27ae60" # Xanh lá
            
            st.markdown(f"""
                <div class="order-box">
                    <div style="display: flex; justify-content: space-between;">
                        <b style="font-size: 18px; color: #d63384;">🍴 {row['FoodName']}</b>
                        <span class="status-badge" style="background-color: {color}; color: white;">{status}</span>
                    </div>
                    <p style="margin: 10px 0 0 0; color: #555;">
                        📅 Hẹn lúc: {row['Appointment']}<br>
                        💬 Ghi chú: {row['Note']}
                    </p>
                </div>
            """, unsafe_allow_html=True)

# Thêm nút làm mới thủ công
if st.button("🔄 Cập nhật tình hình bếp"):
    st.rerun()