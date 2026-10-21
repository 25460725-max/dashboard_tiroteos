import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración básica de la página
st.set_page_config(page_title="Dashboard de Tiroteos Escolares", layout="wide")

# 2. Implementar capa de backend con caché
@st.cache_data
def cargar_y_limpiar_datos():
    url = "https://raw.githubusercontent.com/washingtonpost/data-school-shootings/master/school-shootings-data.csv"
    df = pd.read_csv(url)
    
    # Manejar la columna de edad correctamente (el dataset usa age_shooter1)
    if 'age_shooter1' in df.columns:
        df['age_shooter'] = pd.to_numeric(df['age_shooter1'], errors='coerce')
    else:
        df['age_shooter'] = 0 # Valor por defecto seguro si no existe
        
    # Limpiar enrollment
    if "enrollment" in df.columns and df["enrollment"].dtype == object:
        df["enrollment"] = df["enrollment"].astype(str).str.replace(",", "").astype(float)
        
    # Filtrar columnas esenciales
    columnas_posibles = ["year", "killed", "injured", "enrollment", "age_shooter"]
    variables_clave = [col for col in columnas_posibles if col in df.columns]
    
    df_limpio = df.dropna(subset=variables_clave).copy()
    return df_limpio

# Cargar los datos
df = cargar_y_limpiar_datos()

# Título del Dashboard
st.title("📊 Dashboard: Análisis de Tiroteos Escolares en EE. UU.")
st.markdown("Explora los datos históricos de tiroteos escolares.")

# 3. Implementar capa de frontend: Widgets de filtrado
st.sidebar.header("⚙️ Filtros de Análisis")

# Filtro 1: Año
min_year = int(df['year'].min())
max_year = int(df['year'].max())
rango_anios = st.sidebar.slider("Selecciona el rango de años:", min_value=min_year, max_value=max_year, value=(min_year, max_year))

# Filtro 2: Edad del tirador
min_age = int(df['age_shooter'].min())
max_age = int(df['age_shooter'].max())
rango_edad = st.sidebar.slider("Edad del tirador:", min_value=min_age, max_value=max_age, value=(min_age, max_age))

# Aplicar los filtros al dataframe
df_filtrado = df[
    (df['year'] >= rango_anios[0]) & 
    (df['year'] <= rango_anios[1]) &
    (df['age_shooter'] >= rango_edad[0]) & 
    (df['age_shooter'] <= rango_edad[1])
]

# KPI's (Indicadores Clave conectados a los filtros)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Fallecidos", int(df_filtrado['killed'].sum()))
with col2:
    st.metric("Total Heridos", int(df_filtrado['injured'].sum()))
with col3:
    st.metric("Edad Promedio del Tirador", f"{df_filtrado['age_shooter'].mean():.1f} años" if not df_filtrado.empty else "N/A")

# 4. Gráficos interactivos
st.markdown("---")
st.subheader("Evolución de Víctimas por Año")
if not df_filtrado.empty:
    # Agrupar datos por año para el gráfico de líneas
    df_agrupado = df_filtrado.groupby('year')[['killed', 'injured']].sum().reset_index()
    
    # Gráfico 1: Líneas (Plotly)
    fig1 = px.line(df_agrupado, x='year', y=['killed', 'injured'], 
                   labels={'value': 'Cantidad de Víctimas', 'year': 'Año', 'variable': 'Tipo'},
                   title="Tendencia de víctimas fatales y heridos a lo largo del tiempo")
    st.plotly_chart(fig1, use_container_width=True)

    # Gráfico 2: Histograma (Plotly)
    st.subheader("Distribución de la Edad de los Tiradores")
    fig2 = px.histogram(df_filtrado, x='age_shooter', nbins=15, 
                        labels={'age_shooter': 'Edad del Tirador'},
                        title="Frecuencia de edades de los tiradores")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("No hay datos disponibles para los filtros seleccionados.")
