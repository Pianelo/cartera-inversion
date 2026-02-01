import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from playwright.sync_api import sync_playwright

st.set_page_config(page_title="Rastreador de Cartera", layout="wide")
st.title("💰 Rastreador de Cartera")

# --- Datos de la cartera ---
cartera = [
    {"activo": "BTC-EUR", "cantidad": 0.03546, "precio_compra": 3050, "nombre": "Bitcoin"},
    {"activo": "XRP-EUR", "cantidad": 32.26705, "precio_compra": 104.5, "nombre": "XRP"},
    {"activo": None, "cantidad": 822.822, "precio_compra": 9000.20, "nombre": "Fondo Indexado",
     "investing_url": "https://www.investing.com/funds/fund-0P0001CLDK"}
]

# --- Función para obtener precio yfinance ---
def obtener_precio_yf(ticker):
    try:
        data = yf.Ticker(ticker)
        precio_actual = data.history(period="1d")["Close"][-1]
        return float(precio_actual)
    except:
        return None

# --- Función para obtener NAV desde Investing.com usando Playwright ---
def obtener_nav_investing(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            # Esperamos a que cargue el precio
            page.wait_for_selector("span[data-test='instrument-price-last']", timeout=5000)
            nav_text = page.query_selector("span[data-test='instrument-price-last']").inner_text()
            nav = float(nav_text.replace(",", "").strip())
            browser.close()
            return nav
    except Exception as e:
        st.warning(f"No se pudo obtener el NAV: {e}")
        return None

# --- Botón para actualizar precios ---
if st.button("🔄 Actualizar precios"):
    st.experimental_rerun()

# --- Calcular valores y ganancias ---
valores = []
for item in cartera:
    if item.get("activo"):
        precio_actual = obtener_precio_yf(item["activo"])
        if precio_actual is None:
            st.warning(f"No se pudo obtener el precio de {item['nombre']}")
            precio_actual = 0
    else:
        precio_actual = obtener_nav_investing(item["investing_url"])
        if precio_actual is None:
            precio_actual = 0

    valor_actual = precio_actual * item["cantidad"]
    ganancia = valor_actual - item["precio_compra"]
    ganancia_pct = (ganancia / item["precio_compra"]) * 100 if item["precio_compra"] != 0 else 0

    valores.append({
        "Activo": item["nombre"],
        "Cantidad": item["cantidad"],
        "Precio Compra (€)": item["precio_compra"],
        "Precio Actual (€)": round(precio_actual, 4),
        "Valor Actual (€)": round(valor_actual, 2),
        "Ganancia (€)": round(ganancia, 2),
        "Ganancia (%)": round(ganancia_pct, 2)
    })

df = pd.DataFrame(valores)

# --- Mostrar tabla ---
st.subheader("📊 Resumen de la cartera")
st.dataframe(df)

# --- Gráficos ---
st.subheader("💵 Valor Actual por Activo")
fig, ax = plt.subplots()
ax.bar(df["Activo"], df["Valor Actual (€)"], color=["orange","blue","green"])
st.pyplot(fig)

st.subheader("📈 Distribución de la cartera")
fig2, ax2 = plt.subplots()
ax2.pie(df["Valor Actual (€)"], labels=df["Activo"], autopct='%1.1f%%', colors=["orange","blue","green"])
st.pyplot(fig2)