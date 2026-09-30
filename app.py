import streamlit as st
from datetime import datetime, timedelta

# Tetapan Tajuk Halaman & Layout
st.set_page_config(page_title="Sistem Pinjaman Alat Ukur - PUO", page_icon="📐", layout="wide")

# --- HEADER DENGAN LOGO POLI & TAJUK ---
col_logo, col_title = st.columns([1, 4])

with col_logo:
    try:
        st.image("Poli_Logo.png", width=160)
    except:
        st.write("📐 [Logo PUO]")

with col_title:
    st.title("Surveying Equipment Loan Management System")
    st.markdown("**Jabatan Kejuruteraan Awam | Politeknik Ungku Omar (PUO)**")

st.markdown("---")

# Inisialisasi 'session_state' dengan senarai lengkap peralatan
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        "Total Station": True,
        "Prism": True,
        "Pool": True,
        "Tripod": True,
        "GPS RTK": True,
        "Staff": True,
        "Bubble Level": True,
        "Kompas Berprisma": True,
        "Kaki Kompas": True,
        "Pita Ukur": True,
        "Pancang Jajar": True,
        "Tukul": True
    }

if 'loans' not in st.session_state:
    st.session_state.loans = {}

# Sidebar untuk Navigasi Menu
menu = st.sidebar.selectbox("Pilih Menu", ["Papar Inventori", "Mohon Pinjaman", "Pulangkan Alat", "Semak Rekod Pinjaman"])

# --- MENU 1: PAPAR INVENTORI ---
if menu == "Papar Inventori":
    st.header("📋 Status Inventori Alat Ukur")
    st.write("Senarai terkini peralatan ukur yang tersedia di stor jabatan:")
    
    col1, col2, col3, col4 = st.columns(4)
    items_list = list(st.session_state.inventory.items())
    
    for i, (item, available) in enumerate(items_list):
        status_text = "🟢 Tersedia" if available else "🔴 Dipinjam"
        col = [col1, col2, col3, col4][i % 4]
        with col:
            st.info(f"**{item}**\n\nStatus: {status_text}")

# --- MENU 2: MOHON PINJAMAN (SEMUA ALAT DIPAPARKAN) ---
elif menu == "Mohon Pinjaman":
    st.header("📝 Borang Permohonan Pinjaman Alat Ukur")
    
    with st.form("loan_form"):
        st.subheader("1. Maklumat Peminjam")
        col_a, col_b = st.columns(2)
        with col_a:
            borrower_name = st.text_input("Nama Penuh Pelajar / Ketua Kumpulan:")
            matric_no = st.text_input("Nombor Matrik:")
        with col_b:
            class_name = st.text_input("Kelas / Kursus (Contoh: DKA4A):")
            loan_date = st.date_input("Tarikh Mula Pinjam:", datetime.now())
            duration = st.slider("Tempoh Pinjaman (Hari):", 1, 14, 3)
        
        st.markdown("---")
        st.subheader("2. Pilih Alat Ukur (Tick pada kotak)")
        st.write("Alat yang bertanda 🔴 **Dipinjam** tidak boleh dipilih buat sementara waktu:")
        
        selected_items = []
        c1, c2, c3 = st.columns(3)
        items_list = list(st.session_state.inventory.items())
        
        for i, (item, available) in enumerate(items_list):
            col_target = [c1, c2, c3][i % 3]
            with col_target:
                if available:
                    # Jika ada, boleh tick seperti biasa
                    if st.checkbox(f"{item} (Tersedia)", key=f"chk_{item}"):
                        selected_items.append(item)
                else:
                    # Jika tiada / sedang dipinjam, checkbox dimatikan (disabled)
                    st.checkbox(f"{item} (Dipinjam)", key=f"chk_{item}", value=False, disabled=True)
        
        submit_button = st.form_submit_button(label="Hantar Permohonan Pinjaman")
        
        if submit_button:
            if not borrower_name.strip() or not matric_no.strip() or not class_name.strip():
                st.error("Sila lengkapkan semua maklumat nama, no matrik, dan kelas!")
            elif not selected_items:
                st.error("Sila pilih sekurang-kurangnya satu alat yang tersedia untuk dipinjam.")
            else:
                due_date = datetime.combine(loan_date, datetime.min.time()) + timedelta(days=duration)
                record_key = f"{borrower_name} ({matric_no})"
                
                for item in selected_items:
                    st.session_state.inventory[item] = False
                
                if record_key not in st.session_state.loans:
                    st.session_state.loans[record_key] = {
                        "kelas": class_name,
                        "alat": [],
                        "tarikh_pinjam": loan_date.strftime('%d-%m-%Y'),
                        "tarikh_pulang": due_date
                    }
                
                st.session_state.loans[record_key]["alat"].extend(selected_items)
                st.success(f"Berjaya! Permohonan untuk {borrower_name} bagi alat: **{', '.join(selected_items)}** telah direkodkan. Jangkaan pulang: {due_date.strftime('%d-%m-%Y')}")

# --- MENU 3: PULANGKAN ALAT ---
elif menu == "Pulangkan Alat":
    st.header("🔄 Borang Pemulangan Alat Ukur")
    
    if not st.session_state.loans:
        st.info("Tiada rekod pinjaman aktif buat masa ini.")
    else:
        with st.form("return_form"):
            borrower_list = list(st.session_state.loans.keys())
            selected_borrower = st.selectbox("Pilih Peminjam:", borrower_list)
            
            user_items = st.session_state.loans[selected_borrower]["alat"]
            selected_item_to_return = st.selectbox("Pilih Alat yang hendak dipulangkan:", user_items)
            
            return_button = st.form_submit_button(label="Sahkan Pemulangan Alat")
            
            if return_button:
                st.session_state.loans[selected_borrower]["alat"].remove(selected_item_to_return)
                st.session_state.inventory[selected_item_to_return] = True
                st.success(f"Berjaya! Alat **{selected_item_to_return}** telah dipulangkan oleh {selected_borrower}.")
                
                if not st.session_state.loans[selected_borrower]["alat"]:
                    del st.session_state.loans[selected_borrower]

# --- MENU 4: REKOD PINJAMAN ---
elif menu == "Semak Rekod Pinjaman":
    st.header("📊 Rekod & Status Pinjaman Aktif")
    
    if not st.session_state.loans:
        st.info("Tiada pinjaman aktif dalam sistem.")
    else:
        now = datetime.now()
        for name, details in st.session_state.loans.items():
            due_date = details["tarikh_pulang"]
            is_overdue = now > due_date
            
            with st.container():
                st.write(f"### Peminjam: {name}")
                st.write(f"- **Kelas:** {details['kelas']}")
                st.write(f"- **Tarikh Pinjam:** {details['tarikh_pinjam']}")
                st.write(f"- **Alat Dipinjam:** {', '.join(details['alat'])}")
                st.write(f"- **Tarikh Jangkaan Pulang:** {due_date.strftime('%d-%m-%Y')}")
                
                if is_overdue:
                    st.error("Status: ⚠️ LEWAT (OVERDUE)")
                else:
                    st.success("Status: ✅ Aktif dalam tempoh masa")
                st.markdown("---")