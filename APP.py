# Mini-app de cartera con Streamlit
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Rastreador de Inversiones", layout="wide")

st.title("💰 Rastreador de Cartera")

# --- Datos de tu cartera ---
cartera = [
    {"activo": "BTC-EUR", "cantidad": 0.03546, "precio_compra": 3050, "nombre": "Bitcoin"},
    {"activo": "XRP-EUR", "cantidad": 32.26705, "precio_compra": 104.5, "nombre": "XRP"},
    {"activo": "IE00BYX5NX33.FUND", "cantidad": 822.822, "precio_compra": 9000.20, "nombre": "Fondo Indexado"}
]

# --- Función para obtener precio ---
def obtener_precio_yf(ticker):
    try:
        data = yf.Ticker(ticker)
        precio_actual = data.history(period="1d")["Close"][-1]
        return float(precio_actual)
    except:
        return None

# --- Botón para actualizar precios ---
if st.button("🔄 Actualizar precios"):
    st.experimental_rerun()

# --- Calcular valores ---
valores = []
for item in cartera:
    precio_actual = obtener_precio_yf(item["activo"])
    valor_actual = precio_actual * item["cantidad"]
    ganancia = valor_actual - item["precio_compra"]
    ganancia_pct = (ganancia / item["precio_compra"]) * 100
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
