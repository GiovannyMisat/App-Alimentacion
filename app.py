import streamlit as st
import pandas as pd
import random

# Configuración
st.set_page_config(page_title="Menú Familiar 2.0", layout="wide", page_icon="🥑")
st.title("🥑 Planificador Familiar 2.0")
st.markdown("Logica: **Tablas Independientes + BLW + Menú Matías**")

# --- 1. CARGA DE DATOS MULTI-TABLA ---
@st.cache_data
def load_data():
    file_name = "NUEVO_MENU_FAMILIAR.xlsx" 
    try:
        xls = pd.ExcelFile(file_name)
        # Cargamos cada pestaña en un DataFrame diferente
        d_desayuno = pd.read_excel(xls, 'DESAYUNO')
        d_almuerzo = pd.read_excel(xls, 'ALMUERZO')
        d_cena = pd.read_excel(xls, 'CENA')
        d_blw = pd.read_excel(xls, 'BLW_AGUSTIN')
        d_matias = pd.read_excel(xls, 'MATIAS_FRUTA')
        return d_desayuno, d_almuerzo, d_cena, d_blw, d_matias
    except FileNotFoundError:
        st.error(f"⚠️ Falta el archivo {file_name}. Súbelo a GitHub.")
        return None, None, None, None, None

d_des, d_alm, d_cen, d_blw, d_mat = load_data()

# --- 2. FUNCIONES DE SELECCIÓN ---
def get_random(df, col):
    """Obtiene un valor aleatorio de una columna, ignorando vacíos"""
    if df is None or col not in df.columns: return "N/A"
    items = df[col].dropna().tolist()
    return random.choice(items) if items else "Sin opciones"

def generar_menu_semanal():
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    menu = []

    for dia in dias:
        # --- LÓGICA ADULTOS ---
        des_prot = get_random(d_des, 'PROTEINA')
        des_carb = get_random(d_des, 'CARBOHIDRATOS')
        
        alm_prot = get_random(d_alm, 'PROTEINA')
        alm_carb = get_random(d_alm, 'CARBOHIDRATOS')
        alm_verd = get_random(d_alm, 'VERDURA')
        
        cen_prot = get_random(d_cen, 'PROTEINA_LIGERA')
        cen_acom = get_random(d_cen, 'ACOMPANANTE')

        # --- LÓGICA MATÍAS (2 AÑOS) ---
        # Come lo mismo + Fruta/Snack especial
        fruta_matias = get_random(d_mat, 'FRUTA_SNACK')
        menu_matias = f"Igual papás + 🍎 {fruta_matias}"

        # --- LÓGICA AGUSTÍN (6 MESES - BLW) ---
        # Seleccionamos 1 alimento seguro para explorar
        blw_item = d_blw.sample(1).iloc[0] if d_blw is not None else None
        if blw_item is not None:
            agustin_menu = f"👶 **{blw_item['ALIMENTO']}**\n(Corte: {blw_item['CORTE_SEGURO_BLW']})"
        else:
            agustin_menu = "Consultar pediatra"

        menu.append({
            'Día': dia,
            '🍳 Desayuno (Todos)': f"{des_prot} + {des_carb}",
            '🍗 Almuerzo (Todos)': f"{alm_prot} + {alm_carb} + {alm_verd}",
            '🥗 Cena (Ligera)': f"{cen_prot} + {cen_acom}",
            '👦 Matías (Extra)': f"Adicionar: {fruta_matias}",
            '👶 Agustín (BLW)': agustin_menu
        })
    
    return pd.DataFrame(menu)

# --- 3. INTERFAZ ---
if st.button('🔄 Generar Semana 2.0'):
    if d_des is not None:
        st.session_state['menu_v2'] = generar_menu_semanal()

if 'menu_v2' in st.session_state:
    # Mostramos tabla principal
    df_show = st.session_state['menu_v2']
    
    # CSS para hacer la tabla responsive en móviles
    st.markdown("""
    <style>
    .stDataFrame {font-size: 0.8rem;}
    </style>
    """, unsafe_allow_html=True)

    st.data_editor(
        df_show, 
        column_config={
            "👶 Agustín (BLW)": st.column_config.TextColumn(
                "👶 Agustín (BLW)",
                help="Cortes seguros para inicio de alimentación complementaria",
                width="medium"
            ),
            "👦 Matías (Extra)": st.column_config.TextColumn(
                "👦 Matías (Extra)",
                width="small"
            )
        },
        use_container_width=True,
        hide_index=True,
        disabled=True
    )
    
    st.info("💡 **Tip BLW:** Recuerda que para Agustín (6 meses) la prioridad es la textura y el agarre. Cero sal y cero azúcar.")

else:
    st.write("Presiona el botón para cargar la nueva estructura de tablas.")
