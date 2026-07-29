"""
Dashboard de Activaciones — Julio 2026
Fuente: 01 al 19 Julio 2026.xlsb (convertido a Parquet)
Ejecutar localmente:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import hashlib

# ── Contraseña (SHA-256 del texto plano) ──────────────────────────────────
# Para cambiarla, reemplaza el valor de APP_PASSWORD y recalcula el hash:
#   python3 -c "import hashlib; print(hashlib.sha256('TU_NUEVA_CLAVE'.encode()).hexdigest())"
APP_PASSWORD_HASH = "641509a066dd2fd700dbbef97eba0faad0cdcda9f4f398d33b29fbaf065f1376"

def check_password() -> bool:
    """Muestra pantalla de login y devuelve True si la contraseña es correcta."""
    if st.session_state.get("autenticado"):
        return True

    st.set_page_config(
        page_title="Acceso — Activaciones",
        page_icon="🔒",
        layout="centered",
    )
    st.markdown("## 🔒 Acceso restringido")
    st.markdown("Ingresa la contraseña para continuar.")

    pwd = st.text_input("Contraseña", type="password", key="pwd_input")

    if st.button("Entrar"):
        if hashlib.sha256(pwd.encode()).hexdigest() == APP_PASSWORD_HASH:
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta.")
    return False

if not check_password():
    st.stop()

# ── Página ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Activaciones Julio 2026",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Carga de datos ─────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent / "data"

@st.cache_data(show_spinner="Cargando base de datos…")
def load_data() -> pd.DataFrame:
    # Lee el archivo Parquet más reciente en /data
    archivos = sorted(DATA_DIR.glob("*.parquet"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not archivos:
        st.error("No se encontró ningún archivo .parquet en la carpeta /data")
        st.stop()
    df = pd.read_parquet(archivos[0])
    df["FABRICANTE"] = df["FABRICANTE"].str.strip().str.upper()
    df["REGION"]     = df["REGION"].str.strip().str.upper()
    df["AGRUPACION_CANAL"] = df["AGRUPACION_CANAL"].str.strip().str.upper()
    df["MOVIMIENTO"] = df["MOVIMIENTO"].str.strip().str.upper()
    return df, archivos[0].name

df, nombre_archivo = load_data()

# ── Sidebar — Filtros ──────────────────────────────────────────────────────
with st.sidebar:
    st.title("📡 Activaciones")
    st.caption(f"Archivo: `{nombre_archivo}`")
    st.divider()

    fabricantes = sorted(df["FABRICANTE"].dropna().unique())
    sel_fab = st.multiselect("Fabricante", fabricantes, default=fabricantes,
                             placeholder="Seleccionar…")

    regiones = sorted(df["REGION"].dropna().unique())
    sel_reg = st.multiselect("Región", regiones, default=regiones)

    canales = sorted(df["AGRUPACION_CANAL"].dropna().unique())
    sel_can = st.multiselect("Canal", canales, default=canales)

    movimientos = sorted(df["MOVIMIENTO"].dropna().unique())
    sel_mov = st.multiselect("Movimiento", movimientos, default=movimientos)

    fecha_min = df["FECHA"].min().date()
    fecha_max = df["FECHA"].max().date()
    sel_fechas = st.date_input("Rango de fechas",
                               value=(fecha_min, fecha_max),
                               min_value=fecha_min, max_value=fecha_max)
    st.divider()
    st.caption(f"Total registros: `{len(df):,}`")

# ── Filtrado ───────────────────────────────────────────────────────────────
if isinstance(sel_fechas, (list, tuple)) and len(sel_fechas) == 2:
    f_ini = pd.Timestamp(sel_fechas[0])
    f_fin = pd.Timestamp(sel_fechas[1])
else:
    f_ini, f_fin = pd.Timestamp(fecha_min), pd.Timestamp(fecha_max)

mask = (
    df["FABRICANTE"].isin(sel_fab) &
    df["REGION"].isin(sel_reg) &
    df["AGRUPACION_CANAL"].isin(sel_can) &
    df["MOVIMIENTO"].isin(sel_mov) &
    (df["FECHA"] >= f_ini) & (df["FECHA"] <= f_fin)
)
dff = df[mask].copy()

# ── Encabezado ─────────────────────────────────────────────────────────────
st.title("📡 Dashboard de Activaciones — Julio 2026")
periodo = f"{f_ini.strftime('%d %b')} – {f_fin.strftime('%d %b %Y')}"
st.caption(f"Periodo: **{periodo}** · `{len(dff):,}` registros filtrados")

# ── KPIs ───────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("📦 Activaciones",  f"{int(dff['UNIDADES'].sum()):,}")
c2.metric("🏷️ Fabricantes",   dff["FABRICANTE"].nunique())
c3.metric("📍 Regiones",      dff["REGION"].nunique())
c4.metric("🏪 Puntos de venta", f"{dff['NOMBRE_PDV_UNICO'].nunique():,}")
c5.metric("📅 Días cubiertos",  dff["FECHA"].nunique())

st.divider()

# ── Fila 1: Fabricante (barra) | Canal (dona) ─────────────────────────────
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Activaciones por Fabricante")
    fab_u = (dff.groupby("FABRICANTE", as_index=False)["UNIDADES"]
                .sum().sort_values("UNIDADES"))
    fig = px.bar(fab_u, x="UNIDADES", y="FABRICANTE", orientation="h",
                 color="UNIDADES", color_continuous_scale="Blues",
                 text_auto=True)
    fig.update_layout(showlegend=False, coloraxis_showscale=False,
                      margin=dict(l=0, r=10, t=5, b=0), height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Por Canal (Agrupación)")
    can_u = (dff.groupby("AGRUPACION_CANAL", as_index=False)["UNIDADES"]
                .sum().sort_values("UNIDADES", ascending=False))
    fig2 = px.pie(can_u, names="AGRUPACION_CANAL", values="UNIDADES",
                  hole=0.45,
                  color_discrete_sequence=px.colors.qualitative.Pastel)
    fig2.update_traces(textposition="outside", textinfo="label+percent")
    fig2.update_layout(margin=dict(l=10, r=10, t=5, b=0), height=400,
                       showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

# ── Fila 2: Tendencia diaria | Top 10 modelos ─────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("Tendencia de Activaciones — Diaria")
    daily = (dff.groupby("FECHA", as_index=False)["UNIDADES"]
                .sum().sort_values("FECHA"))
    fig3 = px.area(daily, x="FECHA", y="UNIDADES",
                   color_discrete_sequence=["#0068c9"],
                   markers=True)
    fig3.update_layout(margin=dict(l=0, r=10, t=5, b=0), height=320,
                       xaxis_title="", yaxis_title="Unidades")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Top 10 Modelos")
    top = (dff.groupby("MODELO_EQUIPO", as_index=False)["UNIDADES"]
              .sum().sort_values("UNIDADES", ascending=False).head(10))
    fig4 = px.bar(top, x="UNIDADES", y="MODELO_EQUIPO", orientation="h",
                  color="UNIDADES", color_continuous_scale="Teal",
                  text_auto=True)
    fig4.update_layout(showlegend=False, coloraxis_showscale=False,
                       margin=dict(l=0, r=10, t=5, b=0), height=320,
                       yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig4, use_container_width=True)

# ── Fila 3: Mapa de calor Fabricante × Región ─────────────────────────────
st.subheader("Activaciones por Fabricante × Región")
pivot = (dff.groupby(["FABRICANTE","REGION"])["UNIDADES"]
            .sum().unstack(fill_value=0))
if not pivot.empty:
    fig5 = px.imshow(pivot, text_auto=True, aspect="auto",
                     color_continuous_scale="Blues",
                     labels=dict(x="Región", y="Fabricante", color="Unidades"))
    fig5.update_layout(margin=dict(l=0,r=0,t=5,b=0), height=max(300, len(pivot)*35))
    st.plotly_chart(fig5, use_container_width=True)

# ── Fila 4: Por Empresa de Servicio | Por Semana ──────────────────────────
col5, col6 = st.columns(2)

with col5:
    st.subheader("Por Empresa de Servicio")
    emp_u = (dff.groupby("EMPRESA_SERVICIO", as_index=False)["UNIDADES"]
                .sum().sort_values("UNIDADES", ascending=False))
    fig6 = px.bar(emp_u, x="EMPRESA_SERVICIO", y="UNIDADES",
                  color="UNIDADES", color_continuous_scale="Purples",
                  text_auto=True)
    fig6.update_layout(showlegend=False, coloraxis_showscale=False,
                       margin=dict(l=0,r=10,t=5,b=0), height=320,
                       xaxis_title="")
    st.plotly_chart(fig6, use_container_width=True)

with col6:
    st.subheader("Por Semana y Fabricante (Top 6)")
    top6_fab = (dff.groupby("FABRICANTE")["UNIDADES"]
                   .sum().nlargest(6).index.tolist())
    sem = (dff[dff["FABRICANTE"].isin(top6_fab)]
              .groupby(["SEMANA","FABRICANTE"], as_index=False)["UNIDADES"].sum())
    fig7 = px.line(sem, x="SEMANA", y="UNIDADES", color="FABRICANTE",
                   markers=True,
                   color_discrete_sequence=px.colors.qualitative.Set1)
    fig7.update_layout(margin=dict(l=0,r=10,t=5,b=0), height=320,
                       xaxis_title="Semana", yaxis_title="Unidades")
    st.plotly_chart(fig7, use_container_width=True)

# ── Tabla de detalle ───────────────────────────────────────────────────────
st.divider()
with st.expander("🔎 Ver datos detallados (primeras 500 filas)"):
    cols = ["FECHA","REGION","AGRUPACION_CANAL","CANAL_VTA","FABRICANTE",
            "MODELO_EQUIPO","UNIDADES","MOVIMIENTO","EMPRESA_SERVICIO",
            "PLAN_TARIFARIO","MERCADO","ESTADO"]
    st.dataframe(dff[cols].head(500).reset_index(drop=True),
                 use_container_width=True, height=320)
    csv = dff[cols].to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar datos filtrados (CSV)", data=csv,
                       file_name="activaciones_filtradas.csv", mime="text/csv")

st.caption("Dashboard · Activaciones TELCEL · Streamlit + Plotly · 2026")
