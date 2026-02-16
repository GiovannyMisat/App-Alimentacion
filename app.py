import streamlit as st
import pandas as pd
import random

# Configuración de la página
st.set_page_config(page_title="Menú Familiar Quitian", layout="wide", page_icon="🥑")

st.title("🥑 Planificador Semanal - Desayuno, Almuerzo y Cena")
st.markdown("Planificación balanceada para: **2 Adultos + Niño (2 años) + Bebé (6 meses)**")

# --- 1. CARGA DE DATOS ---
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("ALIMENTACION.xlsx")
        # Convertimos todo a mayúsculas para facilitar la búsqueda
        df = df.applymap(lambda s: s.upper() if type(s) == str else s)
        return df
    except FileNotFoundError:
        st.error("⚠️ No se encontró el archivo ALIMENTACION.xlsx. Súbelo al repositorio.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
        return pd.DataFrame()

df = load_data()

# --- 2. LÓGICA DE CLASIFICACIÓN (FILTROS) ---
def clasificar_ingredientes(dataframe):
    if dataframe.empty: return {}, {}, {}, {}, {}, {}

    # Listas crudas (eliminando vacíos)
    proteinas_all = dataframe['PREPARACIONES CON PROTEINA'].dropna().tolist()
    carbos_all = dataframe['CARBOHIDRATOS'].dropna().tolist()
    verduras = dataframe['VERDURA'].dropna().tolist()
    frutas = dataframe['FRUTA'].dropna().tolist()
    # Ajusta 'NIÑOS' según el nombre exacto de tu columna en el Excel
    ninos = dataframe['NIÑOS'].dropna().tolist() if 'NIÑOS' in dataframe.columns else []
    grasas = dataframe['GRASAS'].dropna().tolist() if 'GRASAS' in dataframe.columns else []

    # --- FILTROS INTELIGENTES ---
    # Palabras clave para identificar desayunos
    keywords_desayuno_prot = ['HUEVO', 'QUESO', 'JAMON', 'SALCHICHA', 'TORTILLA', 'OMELETTE']
    keywords_desayuno_carb = ['AREPA', 'PAN', 'TOSTADA', 'GALLETA', 'CEREAL', 'AVENA', 'CAYEYE', 'BOLLO', 'WAFFLE', 'PANCAKE', 'MUFFIN']

    # Separación de Proteínas
    prot_desayuno = [p for p in proteinas_all if any(k in p for k in keywords_desayuno_prot)]
    prot_fuerte = [p for p in proteinas_all if p not in prot_desayuno] # Lo que sobra es para almuerzo/cena

    # Separación de Carbohidratos
    carb_desayuno = [c for c in carbos_all if any(k in c for k in keywords_desayuno_carb)]
    carb_fuerte = [c for c in carbos_all if c not in carb_desayuno]

    # Si las listas filtradas quedan vacías, usamos las generales como respaldo
    if not prot_desayuno: prot_desayuno = proteinas_all
    if not prot_fuerte: prot_fuerte = proteinas_all
    if not carb_desayuno: carb_desayuno = carbos_all
    if not carb_fuerte: carb_fuerte = carbos_all

    return prot_desayuno, prot_fuerte, carb_desayuno, carb_fuerte, verduras, frutas, ninos, grasas

# --- 3. GENERADOR DE MENÚ ---
def generar_menu_completo(df):
    p_desayuno, p_fuerte, c_desayuno, c_fuerte, verduras, frutas, ninos, grasas = clasificar_ingredientes(df)
    
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    menu_data = []

    for dia in dias:
        # Selección aleatoria
        fruta_dia = random.choice(frutas) if frutas else "Fruta"
        verdura_dia = random.choice(verduras) if verduras else "Verdura"
        
        # --- ESTRUCTURA DEL DÍA ---
        # DESAYUNO: Proteína suave + Carbohidrato de desayuno + Fruta
        desayuno = f"{random.choice(p_desayuno)} + {random.choice(c_desayuno)} + {fruta_dia}"
        
        # ALMUERZO: Proteína fuerte + Carbohidrato fuerte + Verdura
        almuerzo = f"{random.choice(p_fuerte)} + {random.choice(c_fuerte)} + {verdura_dia}"
        
        # CENA: Proteína fuerte (puede ser diferente) + Verdura/Carbo ligero
        # A veces la cena es sin carbohidrato o más ligera
        cena = f"{random.choice(p_fuerte)} + {random.choice([random.choice(verduras), random.choice(c_fuerte)])}"
        
        # SNACK NIÑO
        snack = random.choice(ninos) if ninos else fruta_dia

        # BEBÉ (BLW / AC) - Sugerencia basada en el almuerzo (sin sal)
        tip_bebe = f"Ofrecer {verdura_dia} o trocito de proteína (sin sal)"

        menu_data.append({
            'Día': dia,
            '🍳 Desayuno': desayuno,
            '🍗 Almuerzo': almuerzo,
            '🥗 Cena': cena,
            '👶 Snack / Bebé': f"Niño: {snack} | Bebé: {
