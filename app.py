import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import sqlalchemy
from sqlalchemy import create_engine
import pyodbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import folium
from folium import plugins
from streamlit_folium import folium_static

# Configuración de la página
st.set_page_config(
    page_title="Airbnb Análisis",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

colors_airbnb = {
    "Rausch": "#FF5A5F",
    "Babu": "#00A699",
    "Arches": "#FC642D",
    "Hof": "#484848",
    "Foggy": "#767676",
    'background': '#F7F7F7',
    'white': '#FFFFFF'
}

# CSS personalizado con colores de Airbnb
st.markdown(f"""
<style>
    /* Estilo del header principal */
    .main-header {{
        background: linear-gradient(90deg, {colors_airbnb['Rausch']} 0%, {colors_airbnb['Arches']} 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }}
    
    /* Sidebar personalizada */
    .css-1d391kg {{
        background-color: {colors_airbnb['background']};
    }}
    
    /* Botones personalizados */
    .stButton > button {{
        background-color: {colors_airbnb['Rausch']};
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        background-color: {colors_airbnb['Arches']};
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }}
    
    /* Pestañas personalizadas */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: {colors_airbnb['background']};
        border-radius: 8px;
        color: {colors_airbnb['Hof']};
        font-weight: 600;
    }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {colors_airbnb['Rausch']};
        color: white;
    }}
    
    /* Sliders */
    .stSlider > div > div > div > div {{
        background-color: {colors_airbnb['Rausch']};
    }}
</style>
""", unsafe_allow_html=True)

# Título principal con estilo Airbnb
st.markdown(f"""
<div class="main-header">
    <h1>🏠 Análisis de Airbnb</h1>
    <h3>Ocupación, Ingresos y Satisfacción de Usuarios</h3>
    <p>Plataforma integral de análisis de datos de alojamientos</p>
</div>
""", unsafe_allow_html=True)

# Inicializar variables globales
filtered_df = None
df = None

# Database connection configuration
server = 'upgrade-abnb-server.database.windows.net'
database = 'Upgrade_Abnb'
username = 'vmabnbserver'
password = 'JWkWW8Bg%>jy,Xj!'

# Function to create database connection
@st.cache_resource
def create_db_connection():
    """Create database connection with fallback driver options"""
    try:
        drivers = [
            'ODBC Driver 18 for SQL Server',
            'ODBC Driver 17 for SQL Server',
            'ODBC Driver 13 for SQL Server',
            'SQL Server Native Client 11.0',
            'SQL Server'
        ]
        
        # Test available drivers
        available_drivers = [driver for driver in pyodbc.drivers() if any(d in driver for d in ['SQL Server', 'ODBC'])]
        
        for driver in drivers:
            if driver in available_drivers:
                try:
                    connection_string = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}&TrustServerCertificate=yes&Encrypt=yes'
                    engine = create_engine(connection_string)
                    # Test connection
                    with engine.connect() as conn:
                        conn.execute(sqlalchemy.text("SELECT 1"))
                    return engine
                except Exception as e:
                    continue
        
        # If all drivers fail, try without encryption
        for driver in drivers:
            if driver in available_drivers:
                try:
                    connection_string = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver={driver}&TrustServerCertificate=yes'
                    engine = create_engine(connection_string)
                    # Test connection
                    with engine.connect() as conn:
                        conn.execute(sqlalchemy.text("SELECT 1"))
                    return engine
                except Exception as e:
                    continue
        
        raise Exception("Could not establish database connection with any available driver")
    
    except Exception as e:
        st.error(f"Database connection error: {str(e)}")
        return None

# Function to execute queries and return DataFrames
def query_to_df(query, engine):
    """Execute SQL query and return DataFrame"""
    try:
        return pd.read_sql(query, engine)
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
        return None

# Cargar datos
@st.cache_data(ttl=3600)
def load_data():
    try:
        # Create database connection
        engine = create_db_connection()
        
        if engine is None:
            return None
        
        # Load main dataset
        query = "SELECT * FROM [dbo].[listings_completo]"
        df_listings = query_to_df(query, engine)
        
        return df_listings
            
    except Exception as e:
        return None

# Cargar los datos
with st.spinner("🔄 Conectando a la base de datos..."):
    df = load_data()

if df is not None:
    #st.success("✅ Conexión exitosa a la base de datos!")
    
    # Filtros avanzados en sidebar
    if 'origen' in df.columns:
        st.sidebar.markdown(f"""
        <h2 style="color: {colors_airbnb['Rausch']}; font-weight: 700; margin-bottom: 1rem;">
            🔍 Filtros de Análisis
        </h2>
        """, unsafe_allow_html=True)
        st.sidebar.markdown("---")
        
        # 1. FILTRO POR CIUDADES
        st.sidebar.markdown(f"""
        <h3 style="color: {colors_airbnb['Hof']}; font-weight: 600; margin-bottom: 0.5rem;">
            📍 Ciudades
        </h3>
        """, unsafe_allow_html=True)
        ciudades = st.sidebar.multiselect(
            "Seleccionar ciudades:",
            options=sorted(df['origen'].unique()),
            default=sorted(df['origen'].unique()),
            help="Selecciona las ciudades que deseas analizar"
        )
        
        st.sidebar.markdown("---")
        
        # 2. FILTRO POR RANGO DE PRECIOS
        if 'price' in df.columns:
            st.sidebar.markdown(f"""
            <h3 style="color: {colors_airbnb['Hof']}; font-weight: 600; margin-bottom: 0.5rem;">
                💰 Rango de Precios
            </h3>
            """, unsafe_allow_html=True)
            
            # Convertir price a numérico si no lo es
            df['price_numeric'] = pd.to_numeric(df['price'], errors='coerce')
            precio_min = float(df['price_numeric'].min()) if not df['price_numeric'].isna().all() else 0
            precio_max = float(df['price_numeric'].max()) if not df['price_numeric'].isna().all() else 1000
            
            precio_rango = st.sidebar.slider(
                "Precio por noche (€):",
                min_value=precio_min,
                max_value=precio_max,
                value=(precio_min, precio_max),
                step=10.0,
                help="Selecciona el rango de precios por noche"
            )
            
            # Mostrar estadísticas de precio
            st.sidebar.caption(f"💡 Precio promedio: {df['price_numeric'].mean():.0f}€")
        else:
            precio_rango = None
        
        st.sidebar.markdown("---")
        
        # 3. FILTRO POR TIPO DE HOST
        if 'host_is_superhost' in df.columns:
            st.sidebar.markdown(f"""
            <h3 style="color: {colors_airbnb['Hof']}; font-weight: 600; margin-bottom: 0.5rem;">
                👤 Tipo de Host
            </h3>
            """, unsafe_allow_html=True)
            
            # Filtro por Superhost
            host_superhost = st.sidebar.selectbox(
                "Estado de Superhost:",
                options=['Todos', 'Solo Superhosts', 'No Superhosts'],
                help="Filtra por el estado de Superhost"
            )
            
            # Filtro por verificación de identidad
            if 'host_identity_verified' in df.columns:
                host_verificado = st.sidebar.selectbox(
                    "Host verificado:",
                    options=['Todos', 'Solo verificados', 'No verificados'],
                    help="Filtra por hosts con identidad verificada"
                )
            else:
                host_verificado = 'Todos'
        
        st.sidebar.markdown("---")
        
        # 4. FILTRO POR FECHAS
        if 'last_review' in df.columns:
            st.sidebar.markdown(f"""
            <h3 style="color: {colors_airbnb['Hof']}; font-weight: 600; margin-bottom: 0.5rem;">
                📅 Rango de Fechas
            </h3>
            """, unsafe_allow_html=True)
            
            # Convertir fechas si es necesario
            try:
                df['last_review_date'] = pd.to_datetime(df['last_review'], errors='coerce')
                
                if not df['last_review_date'].isna().all():
                    fecha_min = df['last_review_date'].min().date()
                    fecha_max = df['last_review_date'].max().date()
                    
                    col1, col2 = st.sidebar.columns(2)
                    with col1:
                        fecha_inicio = st.date_input(
                            "Desde:",
                            value=fecha_min,
                            min_value=fecha_min,
                            max_value=fecha_max,
                            help="Fecha de inicio del período"
                        )
                    with col2:
                        fecha_fin = st.date_input(
                            "Hasta:",
                            value=fecha_max,
                            min_value=fecha_min,
                            max_value=fecha_max,
                            help="Fecha de fin del período"
                        )
                else:
                    st.sidebar.caption("⚠️ No hay fechas válidas disponibles")
                    fecha_inicio = None
                    fecha_fin = None
            except:
                st.sidebar.caption("⚠️ Error al procesar fechas")
                fecha_inicio = None
                fecha_fin = None
        
        st.sidebar.markdown("---")
        
        # 5. FILTRO POR HOST RATING
        if 'review_scores_rating' in df.columns:
            st.sidebar.markdown(f"""
            <h3 style="color: {colors_airbnb['Hof']}; font-weight: 600; margin-bottom: 0.5rem;">
                ⭐ Rating del Host
            </h3>
            """, unsafe_allow_html=True)
            
            df['rating_numeric'] = pd.to_numeric(df['review_scores_rating'], errors='coerce')
            
            if not df['rating_numeric'].isna().all():
                rating_min = float(df['rating_numeric'].min()) if not df['rating_numeric'].isna().all() else 0.0
                rating_max = float(df['rating_numeric'].max()) if not df['rating_numeric'].isna().all() else 5.0
                
                host_rating_min = st.sidebar.slider(
                    "Puntuación mínima:",
                    min_value=rating_min,
                    max_value=rating_max,
                    value=rating_min,
                    step=0.1,
                    help="Selecciona la puntuación mínima del host"
                )
                
                # Mostrar distribución de ratings
                st.sidebar.caption(f"💡 Rating promedio: {df['rating_numeric'].mean():.1f}/5.0")
            else:
                st.sidebar.caption("⚠️ No hay ratings disponibles")
                host_rating_min = None
        
        # Aplicar filtros
        filtered_df = df.copy()
        
        # Filtrar por ciudades
        if ciudades:
            filtered_df = filtered_df[filtered_df['origen'].isin(ciudades)]
        
        # Filtrar por precio
        if precio_rango and 'price_numeric' in filtered_df.columns:
            filtered_df = filtered_df[
                (filtered_df['price_numeric'] >= precio_rango[0]) & 
                (filtered_df['price_numeric'] <= precio_rango[1])
            ]
        
        # Filtrar por tipo de host (Superhost)
        if 'host_superhost' in locals() and host_superhost != 'Todos' and 'host_is_superhost' in df.columns:
            if host_superhost == 'Solo Superhosts':
                filtered_df = filtered_df[filtered_df['host_is_superhost'] == 't']
            elif host_superhost == 'No Superhosts':
                filtered_df = filtered_df[filtered_df['host_is_superhost'] == 'f']
        
        # Filtrar por host verificado
        if 'host_verificado' in locals() and host_verificado != 'Todos' and 'host_identity_verified' in df.columns:
            if host_verificado == 'Solo verificados':
                filtered_df = filtered_df[filtered_df['host_identity_verified'] == 't']
            elif host_verificado == 'No verificados':
                filtered_df = filtered_df[filtered_df['host_identity_verified'] == 'f']
        
        # Filtrar por fechas
        if 'fecha_inicio' in locals() and fecha_inicio and fecha_fin and 'last_review_date' in filtered_df.columns:
            fecha_inicio_dt = pd.to_datetime(fecha_inicio)
            fecha_fin_dt = pd.to_datetime(fecha_fin)
            filtered_df = filtered_df[
                (filtered_df['last_review_date'] >= fecha_inicio_dt) & 
                (filtered_df['last_review_date'] <= fecha_fin_dt)
            ]
        
        # Filtrar por rating del host
        if 'host_rating_min' in locals() and host_rating_min and 'rating_numeric' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['rating_numeric'] >= host_rating_min]
        
        # Mostrar información de filtros aplicados
        st.sidebar.markdown("---")
        st.sidebar.metric("📊 Registros filtrados", f"{len(filtered_df):,}")
        st.sidebar.metric("📈 Porcentaje del total", f"{(len(filtered_df)/len(df)*100):.1f}%")
        
        # Botón para resetear filtros
        if st.sidebar.button("🔄 Resetear Filtros", help="Reinicia todos los filtros"):
            st.rerun()
        
        # === ANÁLISIS DE DATOS FILTRADOS ===
        st.markdown("---")
        st.header("📊 Análisis de Datos Filtrados")
        
        if len(filtered_df) > 0:
            # Métricas principales con estilo personalizado
            st.markdown("### 📊 Métricas Principales")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                precio_medio = filtered_df['price_numeric'].mean() if 'price_numeric' in filtered_df.columns else 0
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {colors_airbnb['Rausch']}, {colors_airbnb['Arches']}); 
                           padding: 1rem; border-radius: 10px; text-align: center; color: white;">
                    <h2 style="margin: 0; color: white;">💰</h2>
                    <h3 style="margin: 0; color: white;">{precio_medio:.0f}€</h3>
                    <p style="margin: 0; color: white; opacity: 0.9;">Precio medio</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                rating_medio = filtered_df['rating_numeric'].mean() if 'rating_numeric' in filtered_df.columns else 0
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {colors_airbnb['Babu']}, #00D4AA); 
                           padding: 1rem; border-radius: 10px; text-align: center; color: white;">
                    <h2 style="margin: 0; color: white;">⭐</h2>
                    <h3 style="margin: 0; color: white;">{rating_medio:.1f}/5.0</h3>
                    <p style="margin: 0; color: white; opacity: 0.9;">Rating medio</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                superhosts = len(filtered_df[filtered_df['host_is_superhost'] == 't']) if 'host_is_superhost' in filtered_df.columns else 0
                porcentaje_superhosts = (superhosts / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {colors_airbnb['Arches']}, #FF7A47); 
                           padding: 1rem; border-radius: 10px; text-align: center; color: white;">
                    <h2 style="margin: 0; color: white;">👑</h2>
                    <h3 style="margin: 0; color: white;">{porcentaje_superhosts:.1f}%</h3>
                    <p style="margin: 0; color: white; opacity: 0.9;">Superhosts</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                reseñas_promedio = filtered_df['number_of_reviews'].mean() if 'number_of_reviews' in filtered_df.columns else 0
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, {colors_airbnb['Hof']}, {colors_airbnb['Foggy']}); 
                           padding: 1rem; border-radius: 10px; text-align: center; color: white;">
                    <h2 style="margin: 0; color: white;">📝</h2>
                    <h3 style="margin: 0; color: white;">{reseñas_promedio:.0f}</h3>
                    <p style="margin: 0; color: white; opacity: 0.9;">Reseñas promedio</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Crear tabs principales para diferentes análisis
            tab_general, tab_ocupacion, tab_rentabilidad, tab_satisfaccion, tab_conclusiones = st.tabs([
                "📊 General", 
                "📈 Ocupación",
                "💰 Rentabilidad", 
                "⭐ Satisfacción", 
                "  Conclusiones"
            ])
            
            with tab_general:
                st.markdown("### 📊 Vista General del Mercado")
                
                if 'origen' in filtered_df.columns:
                    # =======================
                    # 1. AGREGAR MÉTRICAS POR CIUDAD
                    # =======================
                    # Verificar columnas necesarias
                    required_cols = [
                        'origen', 'latitude', 'longitude', 'price_numeric', 'rating_numeric',
                        'availability_365', 'number_of_reviews'
                    ]
                    missing_cols = [col for col in required_cols if col not in filtered_df.columns]
                    if missing_cols:
                        st.warning(f"Faltan columnas necesarias para el análisis: {', '.join(missing_cols)}")
                    else:
                        # Calcular ocupación estimada e ingresos estimados si no existen
                        if 'ocupacion_estimada' not in filtered_df.columns:
                            filtered_df['ocupacion_estimada'] = 365 - filtered_df['availability_365']
                        if 'porcentaje_ocupacion' not in filtered_df.columns:
                            filtered_df['porcentaje_ocupacion'] = (filtered_df['ocupacion_estimada'] / 365 * 100).round(1)
                        if 'ingresos_anuales_estimados' not in filtered_df.columns:
                            filtered_df['ingresos_anuales_estimados'] = filtered_df['price_numeric'] * filtered_df['ocupacion_estimada']

                        # Agrupar por ciudad y calcular métricas clave
                        city_stats = filtered_df.groupby('origen').agg(
                            latitude=('latitude', 'mean'),
                            longitude=('longitude', 'mean'),
                            avg_price=('price_numeric', 'mean'),
                            total_listings=('listing_id', 'count') if 'listing_id' in filtered_df.columns else ('price_numeric', 'count'),
                            avg_satisfaction=('rating_numeric', 'mean'),
                            avg_occupancy=('porcentaje_ocupacion', 'mean'),
                            avg_revenue=('ingresos_anuales_estimados', 'mean')
                        ).reset_index()

                        # Redondear métricas para visualización
                        city_stats['avg_price'] = city_stats['avg_price'].round(0)
                        city_stats['avg_satisfaction'] = city_stats['avg_satisfaction'].round(2)
                        city_stats['avg_occupancy'] = city_stats['avg_occupancy'].round(0)
                        city_stats['avg_revenue'] = city_stats['avg_revenue'].round(0)

                        # =======================
                        # 3. DASHBOARD MODERNO INTEGRAL
                        # =======================
                        st.markdown("### Dashboard Integral del Mercado")
                        fig = make_subplots(
                            rows=3, cols=3,
                            subplot_titles=[
                                '💰 Análisis de Precios', '🏠 Tamaño del Mercado', '⭐ Métricas de Calidad',
                                '📊 Ocupación vs Ingresos', '🎯 Matriz de Rendimiento', '📈 Distribución de Ingresos',
                                '🌍 Vista Geográfica', '📋 Resumen del Mercado', '🏆 Mejores Rendimientos'
                            ],
                            specs=[
                                [{"type": "bar"}, {"type": "pie"}, {"type": "bar"}],
                                [{"type": "scatter"}, {"type": "scatter"}, {"type": "bar"}],
                                [{"type": "bar"}, {"type": "table"}, {"type": "bar"}]
                            ],
                            vertical_spacing=0.08,
                            horizontal_spacing=0.05
                        )
                        colors = [
                            colors_airbnb['Rausch'],
                            colors_airbnb['Babu'],
                            colors_airbnb['Arches']
                        ] * (len(city_stats) // 3 + 1)

                        # 1. Análisis de Precios (Fila 1, Col 1)
                        fig.add_trace(
                            go.Bar(
                                x=city_stats['origen'],
                                y=city_stats['avg_price'],
                                name='Precio Promedio',
                                marker_color=colors[:len(city_stats)],
                                text=[f'€{price:.0f}' for price in city_stats['avg_price']],
                                textposition='outside',
                                hovertemplate='<b>%{x}</b><br>Precio: €%{y:.0f}<extra></extra>'
                            ),
                            row=1, col=1
                        )
                        # 2. Gráfico de Pastel Tamaño del Mercado (Fila 1, Col 2)
                        fig.add_trace(
                            go.Pie(
                                labels=city_stats['origen'],
                                values=city_stats['total_listings'],
                                name="Cuota de Mercado",
                                marker_colors=colors[:len(city_stats)],
                                textinfo='label+percent',
                                hovertemplate='<b>%{label}</b><br>Anuncios: %{value:,}<br>Cuota: %{percent}<extra></extra>'
                            ),
                            row=1, col=2
                        )
                        # 3. Métricas de Calidad (Fila 1, Col 3)
                        fig.add_trace(
                            go.Bar(
                                x=city_stats['origen'],
                                y=city_stats['avg_satisfaction'],
                                name='Satisfacción',
                                marker_color=colors[:len(city_stats)],
                                text=[f'{rating:.2f}' for rating in city_stats['avg_satisfaction']],
                                textposition='outside',
                                hovertemplate='<b>%{x}</b><br>Puntuación: %{y:.2f}/5<extra></extra>'
                            ),
                            row=1, col=3
                        )
                        # 4. Ocupación vs Ingresos (Fila 2, Col 1)
                        fig.add_trace(
                            go.Scatter(
                                x=city_stats['avg_occupancy'],
                                y=city_stats['avg_revenue'],
                                mode='markers+text',
                                marker=dict(
                                    size=city_stats['total_listings'] / city_stats['total_listings'].max() * 40 + 10,
                                    color=colors[:len(city_stats)],
                                    line=dict(width=2, color='white')
                                ),
                                text=city_stats['origen'],
                                textposition='top center',
                                name='Rendimiento',
                                hovertemplate='<b>%{text}</b><br>Ocupación: %{x:.0f}%<br>Ingresos: €%{y:.0f}<extra></extra>'
                            ),
                            row=2, col=1
                        )
                        # 5. Matriz de Rendimiento - Precio vs Satisfacción (Fila 2, Col 2)
                        fig.add_trace(
                            go.Scatter(
                                x=city_stats['avg_price'],
                                y=city_stats['avg_satisfaction'],
                                mode='markers+text',
                                marker=dict(
                                    size=city_stats['total_listings'] / city_stats['total_listings'].max() * 40 + 10,
                                    color=colors[:len(city_stats)],
                                    line=dict(width=2, color='white')
                                ),
                                text=city_stats['origen'],
                                textposition='top center',
                                name='Precio vs Calidad',
                                hovertemplate='<b>%{text}</b><br>Precio: €%{x:.0f}<br>Puntuación: %{y:.2f}/5<extra></extra>'
                            ),
                            row=2, col=2
                        )
                        # 6. Distribución de Ingresos (Fila 2, Col 3)
                        fig.add_trace(
                            go.Bar(
                                x=city_stats['origen'],
                                y=city_stats['avg_revenue'],
                                name='Ingresos',
                                marker_color=colors[:len(city_stats)],
                                text=[f'€{rev:.0f}' for rev in city_stats['avg_revenue']],
                                textposition='outside',
                                hovertemplate='<b>%{x}</b><br>Ingresos: €%{y:.0f}<extra></extra>'
                            ),
                            row=2, col=3
                        )
                        # 7. Distribución Geográfica de Precios (Fila 3, Col 1)
                        # Asignar regiones manualmente si es necesario
                        regiones = ['Norte España', 'Este España', 'Sur España']
                        precios_regiones = [city_stats['avg_price'].max(), city_stats['avg_price'].median(), city_stats['avg_price'].min()]
                        fig.add_trace(
                            go.Bar(
                                x=regiones,
                                y=precios_regiones,
                                name='Precios Regionales',
                                marker_color=[
                                    colors_airbnb['Rausch'], colors_airbnb['Babu'], colors_airbnb['Arches']
                                ],
                                hovertemplate='<b>%{x}</b><br>Precio Promedio: €%{y:.0f}<extra></extra>'
                            ),
                            row=3, col=1
                        )
                        # 8. Tabla Resumen del Mercado (Fila 3, Col 2)
                        summary_data = [
                            ['Total Mercados', f'{len(city_stats)}'],
                            ['Total Anuncios', f'{city_stats["total_listings"].sum():,}'],
                            ['Precio Promedio', f'€{city_stats["avg_price"].mean():.0f}'],
                            ['Puntuación Promedio', f'{city_stats["avg_satisfaction"].mean():.2f}/5'],
                            ['Ocupación Promedio', f'{city_stats["avg_occupancy"].mean():.0f}%']
                        ]
                        fig.add_trace(
                            go.Table(
                                header=dict(values=['Métrica', 'Valor'],
                                        fill_color=colors_airbnb['Rausch'],
                                        font=dict(color=colors_airbnb['white'], size=12)),
                                cells=dict(values=[[row[0] for row in summary_data],
                                                [row[1] for row in summary_data]],
                                        fill_color=colors_airbnb['background'],
                                        font=dict(size=11))
                            ),
                            row=3, col=2
                        )
                        # 9. Mejores Rendimientos (Fila 3, Col 3)
                        performance_score = (
                            (city_stats['avg_satisfaction'] / 5) * 0.3 +
                            (city_stats['avg_occupancy'] / city_stats['avg_occupancy'].max()) * 0.3 +
                            (city_stats['avg_revenue'] / city_stats['avg_revenue'].max()) * 0.4
                        ) * 100
                        fig.add_trace(
                            go.Bar(
                                x=city_stats['origen'],
                                y=performance_score,
                                name='Puntuación de Rendimiento',
                                marker_color=colors[:len(city_stats)],
                                text=[f'{score:.1f}%' for score in performance_score],
                                textposition='outside',
                                hovertemplate='<b>%{x}</b><br>Puntuación: %{y:.1f}%<extra></extra>'
                            ),
                            row=3, col=3
                        )
                        fig.update_layout(
                            title=dict(
                                text="Dashboard Integral de Análisis del Mercado Airbnb",
                                x=0.5,
                                font=dict(size=24, family="Arial Black")
                            ),
                            height=1200,
                            showlegend=False,
                            template="plotly_white",
                            font=dict(family="Arial", size=10)
                        )
                        fig.update_xaxes(title_text="Ciudad", row=1, col=1)
                        fig.update_yaxes(title_text="Precio (€)", row=1, col=1)
                        fig.update_yaxes(title_text="Puntuación (1-5)", row=1, col=3)
                        fig.update_xaxes(title_text="Ocupación (%)", row=2, col=1)
                        fig.update_yaxes(title_text="Ingresos (€)", row=2, col=1)
                        fig.update_xaxes(title_text="Precio (€)", row=2, col=2)
                        fig.update_yaxes(title_text="Satisfacción", row=2, col=2)
                        fig.update_xaxes(title_text="Ciudad", row=2, col=3)
                        fig.update_yaxes(title_text="Ingresos (€)", row=2, col=3)
                        fig.update_xaxes(title_text="Región", row=3, col=1)
                        fig.update_yaxes(title_text="Precio (€)", row=3, col=1)
                        fig.update_xaxes(title_text="Ciudad", row=3, col=3)
                        fig.update_yaxes(title_text="Puntuación (%)", row=3, col=3)
                        st.plotly_chart(fig, use_container_width=True)

                        # =======================
                        # 4. RESUMEN EJECUTIVO
                        # =======================
                        st.markdown("#### 📋 Resumen Ejecutivo del Mercado")
                        st.info(
                            f"**Mercados Analizados:** {len(city_stats)} principales ciudades españolas\n"
                            f"**Total Propiedades:** {city_stats['total_listings'].sum():,} anuncios activos\n"
                            f"**Precio Promedio del Mercado:** €{city_stats['avg_price'].mean():.0f} por noche\n"
                            f"**Satisfacción General de Huéspedes:** {city_stats['avg_satisfaction'].mean():.2f}/5.0\n"
                            f"**Ocupación Promedio del Mercado:** {city_stats['avg_occupancy'].mean():.0f}%\n"
                            f"**Ingresos Promedio del Mercado:** €{city_stats['avg_revenue'].mean():.0f} anuales"
                        )
                        st.markdown("##### 🏆 Líderes del Mercado por Categoría")
                        col1, col2, col3, col4, col5 = st.columns(5)
                        with col1:
                            st.metric("💎 Premium", f"{city_stats.loc[city_stats['avg_price'].idxmax(), 'origen']}", f"€{city_stats['avg_price'].max():.0f}/noche")
                        with col2:
                            st.metric("⭐ Satisfacción", f"{city_stats.loc[city_stats['avg_satisfaction'].idxmax(), 'origen']}", f"{city_stats['avg_satisfaction'].max():.2f}/5.0")
                        with col3:
                            st.metric("📊 Tamaño", f"{city_stats.loc[city_stats['total_listings'].idxmax(), 'origen']}", f"{city_stats['total_listings'].max():,} anuncios")
                        with col4:
                            st.metric("📈 Ocupación", f"{city_stats.loc[city_stats['avg_occupancy'].idxmax(), 'origen']}", f"{city_stats['avg_occupancy'].max():.0f}%")
                        with col5:
                            st.metric("💸 Ingresos", f"{city_stats.loc[city_stats['avg_revenue'].idxmax(), 'origen']}", f"€{city_stats['avg_revenue'].max():.0f}")

                        st.markdown("##### 📈 Perspectivas Clave del Mercado")
                        price_range = city_stats['avg_price'].max() - city_stats['avg_price'].min()
                        st.write(
                            f"• **Variación de Precios:** €{price_range:.0f} diferencia entre mercados\n"
                            f"• **Concentración del Mercado:** {(city_stats['total_listings'].max()/city_stats['total_listings'].sum()*100):.1f}% de anuncios en el mercado más grande\n"
                            f"• **Consistencia de Calidad:** {city_stats['avg_satisfaction'].std():.2f} desviación estándar en satisfacción\n"
                            f"• **Eficiencia de Rendimiento:** {city_stats['avg_occupancy'].mean():.0f}% tasa de utilización promedio"
                        )

                        # Calcular city_stats a partir de los datos filtrados (filtered_df)
                        city_stats_real = filtered_df.groupby('origen').agg({
                            'price_numeric': 'mean',
                            'listing_id': 'count' if 'listing_id' in filtered_df.columns else 'price_numeric',
                            'rating_numeric': 'mean',
                            'availability_365': lambda x: ((365 - x.mean()) / 365 * 100),
                            'latitude': 'mean',
                            'longitude': 'mean'
                        }).round(2)
                        city_stats_real.columns = ['avg_price', 'total_listings', 'avg_satisfaction', 'avg_occupancy', 'latitude', 'longitude']
                        city_stats_real['avg_revenue'] = city_stats_real['avg_price'] * (city_stats_real['avg_occupancy'] / 100) * 365
                        city_stats_real = city_stats_real.reset_index()

                        # Coordenadas principales si faltan
                        city_coordinates = {
                            'Barcelona': (41.3851, 2.1734),
                            'Madrid': (40.4168, -3.7038),
                            'Valencia': (39.4699, -0.3763),
                            'Sevilla': (37.3891, -5.9845),
                            'Málaga': (36.7213, -4.4214),
                            'Mallorca': (39.6953, 2.9603),
                            'Bilbao': (43.2627, -2.9253),
                            'San Sebastián': (43.3183, -1.9812),
                            'Granada': (37.1773, -3.5986),
                            'Córdoba': (37.8882, -4.7794)
                        }
                        for idx, row in city_stats_real.iterrows():
                            city = row['origen']
                            if city in city_coordinates:
                                city_stats_real.loc[idx, 'latitude'] = city_coordinates[city][0]
                                city_stats_real.loc[idx, 'longitude'] = city_coordinates[city][1]

                        def create_real_spain_map(city_stats):
                            spain_center = [40.0, -4.0]
                            m = folium.Map(
                                location=spain_center,
                                zoom_start=6,
                                tiles='OpenStreetMap'
                            )
                            folium.TileLayer('CartoDB Positron').add_to(m)
                            folium.TileLayer('CartoDB Dark_Matter').add_to(m)
                            max_price = city_stats['avg_price'].max()
                            min_price = city_stats['avg_price'].min()
                            def get_color(price):
                                if price > max_price * 0.8:
                                    return colors_airbnb['Rausch']
                                elif price > max_price * 0.6:
                                    return colors_airbnb['Arches']
                                elif price > max_price * 0.4:
                                    return colors_airbnb['Babu']
                                else:
                                    return colors_airbnb['background']
                            for idx, row in city_stats.iterrows():
                                popup_html = f"""
                                <div style="font-family: 'Segoe UI', Arial, sans-serif; width: 300px; padding: 15px;">
                                    <h3 style="color: #2C3E50; margin: 0 0 15px 0; text-align: center; border-bottom: 2px solid #3498DB;">
                                        🏛️ {row['origen']}
                                    </h3>
                                    <div style="background: linear-gradient(135deg, {colors_airbnb['Rausch']} 0%, {colors_airbnb['Arches']} 100%); \
                                                color: {colors_airbnb['white']}; padding: 10px; border-radius: 8px; margin-bottom: 15px;">
                                        <h4 style="margin: 0; text-align: center;">💰 €{row['avg_price']:.0f} por noche</h4>
                                    </div>
                                    <table style="width: 100%; border-collapse: collapse;">
                                        <tr style="background-color: {colors_airbnb['background']};">
                                            <td style="padding: 8px; border: 1px solid {colors_airbnb['Foggy']};"><strong>🏠 Propiedades:</strong></td>
                                            <td style="padding: 8px; border: 1px solid {colors_airbnb['Foggy']};">{row['total_listings']:,}</td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px; border: 1px solid {colors_airbnb['Foggy']};"><strong>⭐ Satisfacción:</strong></td>
                                            <td style="padding: 8px; border: 1px solid {colors_airbnb['Foggy']};">{row['avg_satisfaction']:.2f}/5.0</td>
                                        </tr>
                                        <tr style="background-color: {colors_airbnb['background']};">
                                            <td style="padding: 8px; border: 1px solid {colors_airbnb['Foggy']};"><strong>📈 Ocupación:</strong></td>
                                            <td style="padding: 8px; border: 1px solid {colors_airbnb['Foggy']};">{row['avg_occupancy']:.0f}%</td>
                                        </tr>
                                        <tr>
                                            <td style="padding: 8px; border: 1px solid {colors_airbnb['Foggy']};"><strong>💸 Ingresos Anuales:</strong></td>
                                            <td style="padding: 8px; border: 1px solid {colors_airbnb['Foggy']};">€{row['avg_revenue']:.0f}</td>
                                        </tr>
                                        <tr style="background-color: {colors_airbnb['background']};">
                                            <td style="padding: 8px; border: 1px solid {colors_airbnb['Foggy']};"><strong>📍 Coordenadas:</strong></td>
                                            <td style="padding: 8px; border: 1px solid {colors_airbnb['Foggy']};">{row['latitude']:.3f}, {row['longitude']:.3f}</td>
                                        </tr>
                                    </table>
                                    <div style="margin-top: 15px; text-align: center; font-size: 12px; color: {colors_airbnb['Foggy']};">
                                        💡 Tamaño del marcador = Volumen de mercado
                                    </div>
                                </div>
                                """
                                marker_size = max(15, min(40, row['total_listings'] / 100))
                                folium.CircleMarker(
                                    location=[row['latitude'], row['longitude']],
                                    radius=marker_size,
                                    popup=folium.Popup(popup_html, max_width=350),
                                    tooltip=f"{row['origen']} - €{row['avg_price']:.0f}/noche - {row['total_listings']} propiedades",
                                    color='white',
                                    weight=3,
                                    fillColor=get_color(row['avg_price']),
                                    fillOpacity=0.8
                                ).add_to(m)
                                folium.Marker(
                                    location=[row['latitude'], row['longitude']],
                                    icon=folium.DivIcon(
                                        html=f"""
                                        <div style="background-color: rgba(255,255,255,0.9); 
                                                   border: 2px solid {get_color(row['avg_price'])}; 
                                                   border-radius: 5px; 
                                                   padding: 2px 6px; 
                                                   font-weight: bold; 
                                                   font-size: 12px; 
                                                   color: #2C3E50;
                                                   box-shadow: 0 2px 4px rgba(0,0,0,0.3);">
                                            {row['origen']}
                                        </div>
                                        """,
                                        icon_size=(80, 20),
                                        icon_anchor=(40, 35)
                                    )
                                ).add_to(m)
                            legend_html = f"""
                            <div style="position: fixed; 
                                        top: 10px; right: 10px; width: 280px; 
                                        background-color: {colors_airbnb['white']}; border: 3px solid {colors_airbnb['Babu']}; z-index: 9999; 
                                        font-size: 14px; font-family: 'Segoe UI', Arial; 
                                        padding: 15px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.3);">
                                <h3 style="margin: 0 0 15px 0; color: {colors_airbnb['Hof']}; text-align: center; border-bottom: 2px solid {colors_airbnb['Babu']}; padding-bottom: 5px;">
                                    🗺️ Mapa del Mercado Airbnb España
                                </h3>
                                <h4 style="margin: 10px 0 5px 0; color: {colors_airbnb['Foggy']};">💰 Niveles de Precio:</h4>
                                <p style="margin: 3px 0;"><span style="color: {colors_airbnb['Rausch']}; font-size: 18px;">●</span> Premium: &gt;€{max_price * 0.8:.0f}</p>
                                <p style="margin: 3px 0;"><span style="color: {colors_airbnb['Arches']}; font-size: 18px;">●</span> Alto: €{max_price * 0.6:.0f}-{max_price * 0.8:.0f}</p>
                                <p style="margin: 3px 0;"><span style="color: {colors_airbnb['Babu']}; font-size: 18px;">●</span> Medio: €{max_price * 0.4:.0f}-{max_price * 0.6:.0f}</p>
                                <p style="margin: 3px 0;"><span style="color: {colors_airbnb['white']}; font-size: 18px;">●</span> Asequible: &lt;€{max_price * 0.4:.0f}</p>
                                <hr style="margin: 10px 0; border: 1px solid {colors_airbnb['Foggy']};">
                                <h4 style="margin: 10px 0 5px 0; color: {colors_airbnb['Foggy']};">📊 Información:</h4>
                                <p style="margin: 3px 0; font-size: 12px;">🔵 Tamaño = Volumen de mercado</p>
                                <p style="margin: 3px 0; font-size: 12px;">📍 Click para detalles completos</p>
                                <p style="margin: 3px 0; font-size: 12px;">🗺️ Múltiples capas disponibles</p>
                                <div style="margin-top: 10px; padding: 8px; background-color: {colors_airbnb['background']}; border-radius: 5px; text-align: center;">
                                    <strong style="color: {colors_airbnb['Hof']};">Total: {len(city_stats)} ciudades</strong><br>
                                    <span style="font-size: 12px; color: {colors_airbnb['Foggy']};">{city_stats['total_listings'].sum():,} propiedades</span>
                                </div>
                            </div>
                            """
                            m.get_root().html.add_child(folium.Element(legend_html))
                            folium.LayerControl().add_to(m)
                            plugins.Fullscreen().add_to(m)
                            plugins.MeasureControl().add_to(m)
                            return m

                        st.markdown("#### 🗺️ Mapa Real de España con Datos Airbnb")
                        spain_map = create_real_spain_map(city_stats_real)
                        folium_static = st.components.v1.html if hasattr(st, "components") else st._legacy_html
                        folium_static(spain_map._repr_html_(), height=600)
                else:
                    st.info("No hay datos disponibles para Valencia con los filtros actuales.")
            
            with tab_ocupacion:
                st.markdown("### 📈 Análisis de Ocupación")
                
                # Análisis basado en disponibilidad
                if 'availability_365' in filtered_df.columns:
                    # Calcular métricas de ocupación
                    filtered_df['ocupacion_estimada'] = 365 - filtered_df['availability_365']
                    filtered_df['porcentaje_ocupacion'] = (filtered_df['ocupacion_estimada'] / 365 * 100).round(1)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        ocupacion_media = filtered_df['porcentaje_ocupacion'].mean()
                        st.metric("Ocupación Promedio", f"{ocupacion_media:.1f}%")
                    
                    with col2:
                        alta_ocupacion = len(filtered_df[filtered_df['porcentaje_ocupacion'] > 70])
                        st.metric("Listings Alta Ocupación (>70%)", alta_ocupacion)
                    
                    with col3:
                        baja_ocupacion = len(filtered_df[filtered_df['porcentaje_ocupacion'] < 30])
                        st.metric("Listings Baja Ocupación (<30%)", baja_ocupacion)

                    # --- Análisis de ocupación anual por ciudad y año ---
                    # Usar el dataframe original cargado (df) para obtener históricos por año
                    if df is not None and 'date' in df.columns and 'listing_id' in df.columns and 'availability_365' in df.columns:
                        df['date'] = pd.to_datetime(df['date'], errors='coerce')
                        df['year'] = df['date'].dt.year
                        df_ult_por_listado = (
                            df.sort_values('date')
                            .drop_duplicates(subset=['listing_id', 'year'], keep='last')
                        )
                        df_ult_por_listado['noches_ocupadas'] = 365 - df_ult_por_listado['availability_365']
                        df_ult_por_listado['dias_del_año'] = df_ult_por_listado['year'].apply(lambda y: 366 if y % 4 == 0 else 365)
                        ocupacion_anual = df_ult_por_listado.groupby('year').agg(
                            noches_ocupadas=('noches_ocupadas', 'sum'),
                            capacidad_total=('dias_del_año', 'sum')
                        )
                        ocupacion_anual['tasa_ocupacion_%'] = (
                            ocupacion_anual['noches_ocupadas'] / ocupacion_anual['capacidad_total'] * 100
                        )
                        ocupacion_origen_anio = (
                            df_ult_por_listado.groupby(['origen', 'year']).agg(
                                noches_ocupadas=('noches_ocupadas', 'sum'),
                                capacidad_total=('dias_del_año', 'sum')
                            )
                            .assign(tasa_ocupacion_=lambda x: x['noches_ocupadas'] / x['capacidad_total'] * 100)
                            .rename(columns={'tasa_ocupacion_': 'tasa_ocupacion_%'})
                            .reset_index()
                        )
                        colors_ocupacion = {
                            'Mallorca': colors_airbnb['Rausch'],
                            'Málaga': colors_airbnb['Babu'],
                            'Valencia': colors_airbnb['Arches']
                        }
                        ocupacion_filtrada = ocupacion_origen_anio[ocupacion_origen_anio['year'] >= 2012].copy()
                        fig3 = px.line(
                            ocupacion_filtrada,
                            x='year',
                            y='tasa_ocupacion_%',
                            color='origen',
                            title='Tasa de Ocupación por Ciudad y Año (%)',
                            markers=True,
                            labels={'tasa_ocupacion_%': 'Ocupación (%)', 'year': 'Año', 'origen': 'Ciudad'},
                            color_discrete_map=colors_ocupacion
                        )
                        fig3.update_layout(
                            plot_bgcolor=colors_airbnb['background'],
                            paper_bgcolor=colors_airbnb['background'],
                            font_color=colors_airbnb['Hof'],
                            legend_title_text='Ciudad'
                        )
                        st.plotly_chart(fig3, use_container_width=True)

                        # Mostrar métricas de ocupación anual por ciudad en la misma fila
                        ultimos_anios = ocupacion_filtrada['year'].max()
                        col_malaga, col_valencia, col_mallorca = st.columns(3)
                        for ciudad, col in zip(['Málaga', 'Valencia', 'Mallorca'], [col_malaga, col_valencia, col_mallorca]):
                            df_ciudad = ocupacion_filtrada[ocupacion_filtrada['origen'] == ciudad]
                            if not df_ciudad.empty:
                                tasa_ultimo_anio = df_ciudad[df_ciudad['year'] == ultimos_anios]['tasa_ocupacion_%'].values
                                if len(tasa_ultimo_anio) > 0:
                                    col.metric(f"Ocupación {ciudad}", f"{tasa_ultimo_anio[0]:.1f}%")
                                else:
                                    col.metric(f"Ocupación {ciudad}", "N/A")
                            else:
                                col.metric(f"Ocupación {ciudad}", "N/A")

                        # --- Tasa de ocupación media entre todos los años, 2024 y 2025 (en la misma fila con métricas Streamlit) ---
                        noches_ocupadas_total = df_ult_por_listado['noches_ocupadas'].sum()
                        capacidad_total = df_ult_por_listado['dias_del_año'].sum()
                        tasa_ocupacion_media = (noches_ocupadas_total / capacidad_total) * 100

                        df_2024 = df_ult_por_listado[df_ult_por_listado['year'] == 2024]
                        noches_ocupadas_2024 = df_2024['noches_ocupadas'].sum()
                        capacidad_total_2024 = df_2024['dias_del_año'].sum()
                        tasa_ocupacion_2024 = (noches_ocupadas_2024 / capacidad_total_2024) * 100 if capacidad_total_2024 > 0 else None

                        df_2025 = df_ult_por_listado[df_ult_por_listado['year'] == 2025]
                        noches_ocupadas_2025 = df_2025['noches_ocupadas'].sum()
                        capacidad_total_2025 = df_2025['dias_del_año'].sum()
                        tasa_ocupacion_2025 = (noches_ocupadas_2025 / capacidad_total_2025) * 100 if capacidad_total_2025 > 0 else None

                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Ocupación media (todos los años)", f"{tasa_ocupacion_media:.2f}%")
                        with col2:
                            st.metric("Ocupación 2024", f"{tasa_ocupacion_2024:.2f}%" if tasa_ocupacion_2024 is not None else "N/A")
                        with col3:
                            st.metric("Ocupación 2025", f"{tasa_ocupacion_2025:.2f}%" if tasa_ocupacion_2025 is not None else "N/A")
                    else:
                        st.info("No hay datos históricos de ocupación anual disponibles para mostrar la evolución por ciudad.")                

                else:
                    st.info("No hay datos de disponibilidad para calcular la ocupación.")
            
            with tab_rentabilidad:
                st.markdown("### 💰 Análisis de Rentabilidad")
                
                if 'price_numeric' in filtered_df.columns:
                    # Calcular ingresos estimados anuales
                    if 'availability_365' in filtered_df.columns:
                        filtered_df['dias_ocupados'] = 365 - filtered_df['availability_365']
                        filtered_df['ingresos_anuales_estimados'] = filtered_df['price_numeric'] * filtered_df['dias_ocupados']
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            ingresos_promedio = filtered_df['ingresos_anuales_estimados'].mean()
                            st.metric("Ingresos Anuales Promedio", f"{ingresos_promedio:,.0f}€")
                        
                        with col2:
                            top_10_percent = filtered_df['ingresos_anuales_estimados'].quantile(0.9)
                            st.metric("Top 10% Ingresos", f"{top_10_percent:,.0f}€")
                        
                        with col3:
                            rentabilidad_alta = len(filtered_df[filtered_df['ingresos_anuales_estimados'] > ingresos_promedio * 1.5])
                            st.metric("Listings Alta Rentabilidad", rentabilidad_alta)
                        
                        # --- ANÁLISIS AVANZADO DE RENTABILIDAD ---

                        st.markdown("#### 📊 Análisis Avanzado de Rentabilidad (RevPAR, ADR, Relación Precio-Calidad)")

                        # Asegurar que 'date' es datetime y crear columna 'year'
                        if 'date' in df.columns and 'listing_id' in df.columns and 'availability_365' in df.columns:
                            df['date'] = pd.to_datetime(df['date'], errors='coerce')
                            df['year'] = df['date'].dt.year

                            # Último registro por alojamiento y año para calcular disponibilidad
                            df_ult_por_listado = (
                                df.sort_values('date')
                                .drop_duplicates(subset=['listing_id', 'year'], keep='last')
                                .copy()
                            )
                            df_ult_por_listado['dias_del_año'] = df_ult_por_listado['year'].apply(lambda y: 366 if y % 4 == 0 else 365)
                            df_ult_por_listado['noches_ocupadas'] = df_ult_por_listado['dias_del_año'] - df_ult_por_listado['availability_365']

                            # Ingresos totales por año (sumando precios de noches efectivamente ocupadas)
                            if 'price_numeric' in df_ult_por_listado.columns:
                                ingresos_por_año = df_ult_por_listado.groupby('year').apply(lambda x: (x['price_numeric'] * x['noches_ocupadas']).sum())
                                habitaciones_disponibles_por_año = df_ult_por_listado.groupby('year')['noches_ocupadas'].sum()
                                revpar_directo = (ingresos_por_año / habitaciones_disponibles_por_año).to_frame(name='RevPAR')

                                adr = df_ult_por_listado.groupby('year')['price_numeric'].mean()
                                noches_ocupadas = df_ult_por_listado.groupby('year')['noches_ocupadas'].sum()
                                capacidad_total = df_ult_por_listado.groupby('year')['dias_del_año'].sum()
                                tasa_ocupacion = (noches_ocupadas / capacidad_total)
                                revpar_por_tasa = ((adr * tasa_ocupacion)).to_frame(name='RevPAR_ADR_tasa')

                                revpar_comparado = revpar_directo.join(revpar_por_tasa)
                                fig = go.Figure()
                                fig.add_trace(go.Bar(
                                    x=revpar_comparado.index.astype(str),
                                    y=revpar_comparado['RevPAR'],
                                    name='RevPAR (directo)',
                                    marker_color=colors_airbnb['Rausch']
                                ))
                                fig.add_trace(go.Bar(
                                    x=revpar_comparado.index.astype(str),
                                    y=revpar_comparado['RevPAR_ADR_tasa'],
                                    name='RevPAR (ADR × Ocupación)',
                                    marker_color=colors_airbnb['Babu']
                                ))
                                fig.update_layout(
                                    title='Comparación de RevPAR por Año',
                                    xaxis_title='Año',
                                    yaxis_title='RevPAR (€)',
                                    barmode='group',
                                    height=500,
                                    showlegend=True,
                                    plot_bgcolor=colors_airbnb['background'],
                                    paper_bgcolor=colors_airbnb['background'],
                                    font_color=colors_airbnb['Hof']
                                )
                                st.plotly_chart(fig, use_container_width=True)

                                # --- RevPAR por ciudad y año ---
                                ingresos_por_origen_anio = df_ult_por_listado.groupby(['origen', 'year']).apply(lambda x: (x['price_numeric'] * x['noches_ocupadas']).sum())
                                disponibles_por_origen_anio = df_ult_por_listado.groupby(['origen', 'year'])['noches_ocupadas'].sum()
                                revpar_directo_ciudad = (ingresos_por_origen_anio / disponibles_por_origen_anio).to_frame(name='RevPAR_directo').reset_index();

                                adr_origen_anio = df_ult_por_listado.groupby(['origen', 'year'])['price_numeric'].mean()
                                noches_ocupadas_ciudad = df_ult_por_listado.groupby(['origen', 'year'])['noches_ocupadas'].sum()
                                capacidad_total_ciudad = df_ult_por_listado.groupby(['origen', 'year'])['dias_del_año'].sum()
                                tasa_ocupacion_ciudad = (noches_ocupadas_ciudad / capacidad_total_ciudad)
                                revpar_adr_ciudad = ((adr_origen_anio * tasa_ocupacion_ciudad)).to_frame(name='RevPAR_ADR_tasa').reset_index();

                                revpar_comparado_ciudad = pd.merge(revpar_directo_ciudad, revpar_adr_ciudad, on=['origen', 'year']);
                                fig2 = px.bar(
                                    revpar_comparado_ciudad.melt(
                                        id_vars=['origen', 'year'],
                                        value_vars=['RevPAR_directo', 'RevPAR_ADR_tasa'],
                                        var_name='Método', value_name='RevPAR (€)'
                                    ),
                                    x='year', y='RevPAR (€)', color='Método', barmode='group',
                                    facet_col='origen', facet_col_wrap=3,
                                    title='Comparación de RevPAR por Año y Ciudad (Directo vs ADR × Ocupación)'
                                )
                                fig2.update_layout(
                                    height=800,
                                    showlegend=True,
                                    plot_bgcolor=colors_airbnb['background'],
                                    paper_bgcolor=colors_airbnb['background'],
                                    font_color=colors_airbnb['Hof']
                                )
                                st.plotly_chart(fig2, use_container_width=True)
                                
                                # --- Gráfico de precio medio por noche ponderado por noches ocupadas con paleta Airbnb ---
 
                                # Paleta de colores Airbnb por región
                                airbnb_palette = {
                                    'Mallorca': '#FF5A5F',   # primary
                                    'Málaga': '#00A699',     # secondary
                                    'Valencia': '#FC642D'    # accent
                                }

                                # Calcular el precio medio por noche ponderado por noches ocupadas para cada región
                                tabla_precio_ponderado = (
                                    df_ult_por_listado
                                    .groupby('origen')
                                    .apply(lambda x: np.average(x['price'], weights=x['noches_ocupadas']))
                                    .reset_index(name='Precio Medio por Noche (€)')
                                    .sort_values('Precio Medio por Noche (€)', ascending=False)
                                )

                                # Asignar color Airbnb a cada barra según la región
                                bar_colors = tabla_precio_ponderado['origen'].map(airbnb_palette)

                                # --- Crear host_perf si no existe ---
                                if 'host_perf' not in globals():
                                    # Crear host_perf: resumen por host_id
                                    host_perf = (
                                        df_ult_por_listado.groupby('host_id')
                                        .agg(
                                            calificacion_promedio=('calificacion_promedio', 'mean') if 'calificacion_promedio' in df_ult_por_listado.columns else ('review_scores_rating', 'mean'),
                                            count_listings=('listing_id', 'count')
                                        )
                                        .reset_index()
                                    )
                                    # Añadir columna 'origen' por host (modo)
                                    origen_por_host = (
                                        df_ult_por_listado.groupby('host_id')['origen']
                                        .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else np.nan)
                                        .reset_index()
                                    )
                                    host_perf = host_perf.merge(origen_por_host, on='host_id', how='left')
                                    # Crear columna 'categoria_valoracion' en host_perf
                                    def categorizar_valoracion(score):
                                        if score >= 4.8:
                                            return 'Excelente'
                                        elif score >= 4.5:
                                            return 'Muy Bueno'
                                        elif score >= 4.0:
                                            return 'Bueno'
                                        elif score >= 3.0:
                                            return 'Regular'
                                        else:
                                            return 'Deficiente'
                                    host_perf['categoria_valoracion'] = host_perf['calificacion_promedio'].apply(categorizar_valoracion)

                                # 1. Relacionar cada alojamiento con la valoración de su host
                                df_ult_por_listado = df_ult_por_listado.copy()
                                df_ult_por_listado = df_ult_por_listado.merge(
                                    host_perf[['host_id', 'categoria_valoracion']],
                                    on='host_id',
                                    how='left'
                                )

                                # 2. Tabla resumen: precio medio por categoría de valoración de host
                                tabla_precio_valoracion = df_ult_por_listado.groupby('categoria_valoracion')['price'].agg(['count', 'mean', 'median', 'std']).reset_index()
                                tabla_precio_valoracion.columns = ['Categoría Valoración Host', 'Nº Alojamientos', 'Precio Medio (€)', 'Mediana (€)', 'Desviación (€)']
                                tabla_precio_valoracion = tabla_precio_valoracion.sort_values('Precio Medio (€)', ascending=False)

                                # Si no existe, añade la columna de calificación promedio del host al dataframe de alojamientos
                                if 'calificacion_promedio' not in df_ult_por_listado.columns:
                                    df_ult_por_listado = df_ult_por_listado.merge(
                                        host_perf[['host_id', 'calificacion_promedio']],
                                        on='host_id',
                                        how='left'
                                    )

                                # Elimina filas con valores nulos en precio o calificación y filtra outliers de precio > 80000
                                df_corr = df_ult_por_listado[['price', 'calificacion_promedio']].dropna()
                                df_corr = df_corr[df_corr['price'] <= 80000]

                                # Calcular la correlación de Pearson
                                correlacion = df_corr['price'].corr(df_corr['calificacion_promedio'])

                                # Visualización: ambos gráficos en la misma fila con Streamlit
                                col1, col2 = st.columns(2)

                                with col1:
                                    fig1, ax1 = plt.subplots(figsize=(7, 4))
                                    bars = ax1.barh(
                                        tabla_precio_ponderado['origen'],
                                        tabla_precio_ponderado['Precio Medio por Noche (€)'],
                                        color=bar_colors,
                                        edgecolor='grey'
                                    )
                                    ax1.set_xlabel('Precio Medio por Noche (€)')
                                    ax1.set_title('💶 Precio Medio por Noche y Región (ponderado)')
                                    ax1.invert_yaxis()
                                    for i, v in enumerate(tabla_precio_ponderado['Precio Medio por Noche (€)']):
                                        ax1.text(v + 1, i, f"{v:.2f} €", va='center', fontsize=9, fontweight='bold')
                                    # Leyenda personalizada
                                    from matplotlib.patches import Patch
                                    legend_elements = [
                                        Patch(facecolor=airbnb_palette['Mallorca'], label='Mallorca'),
                                        Patch(facecolor=airbnb_palette['Málaga'], label='Málaga'),
                                        Patch(facecolor=airbnb_palette['Valencia'], label='Valencia')
                                    ]
                                    ax1.legend(handles=legend_elements, title='Región', loc='lower right')
                                    plt.tight_layout()
                                    st.pyplot(fig1)

                                with col2:
                                    fig2, ax2 = plt.subplots(figsize=(7, 4))
                                    sns.scatterplot(data=df_corr, x='calificacion_promedio', y='price', alpha=0.5, ax=ax2)
                                    ax2.set_title('Relación entre Precio y Calificación Promedio del Host')
                                    ax2.set_xlabel('Calificación Promedio del Host')
                                    ax2.set_ylabel('Precio (€)')
                                    ax2.grid(True, alpha=0.3)
                                    plt.tight_layout()
                                    st.pyplot(fig2)
                                    st.caption(f"Coeficiente de correlación (Pearson): {correlacion:.3f}")
                            
                            
                        st.markdown("### Málaga")

                        # --- Análisis específico para Málaga ---

                        # Filtrar datos solo para Málaga
                        malaga_revpar = revpar_comparado_ciudad[revpar_comparado_ciudad['origen'] == 'Málaga']
                        malaga_df = df_ult_por_listado[df_ult_por_listado['origen'] == 'Málaga'].copy()

                        # 1. RevPAR medios para Málaga
                        revpar_directo_malaga = malaga_revpar['RevPAR_directo'].mean()
                        revpar_tasa_malaga = malaga_revpar['RevPAR_ADR_tasa'].mean()
                        st.markdown(f"**RevPAR directo medio Málaga:** {revpar_directo_malaga:.2f} €")
                        st.markdown(f"**RevPAR ADR×Ocupación medio Málaga:** {revpar_tasa_malaga:.2f} €")

                        # 2. RevPAR por año en Málaga (líneas con paleta Airbnb)
                        Colors_airbnb = {
                            'RevPAR_directo': colors_airbnb['Rausch'],
                            'RevPAR_ADR_tasa': colors_airbnb['Babu']
                        }
                        df_long = malaga_revpar.melt(
                            id_vars=['origen', 'year'],
                            value_vars=['RevPAR_directo', 'RevPAR_ADR_tasa'],
                            var_name='Método', value_name='RevPAR (€)'
                        )
                        fig = px.line(
                            df_long,
                            x='year',
                            y='RevPAR (€)',
                            color='Método',
                            markers=True,
                            color_discrete_map=Colors_airbnb,
                            title='RevPAR por Año en Málaga (Directo vs ADR × Ocupación)'
                        )
                        fig.update_layout(
                            height=500,
                            showlegend=True,
                            plot_bgcolor=colors_airbnb['background'],
                            paper_bgcolor=colors_airbnb['background'],
                            font_color=colors_airbnb['Hof']
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        # 3. Precio medio en Málaga (general, 2024 y 2025)
                        precio_medio_malaga = malaga_df['price'].mean()
                        precio_medio_malaga_2024 = malaga_df[malaga_df['year'] == 2024]['price'].mean()
                        precio_medio_malaga_2025 = malaga_df[malaga_df['year'] == 2025]['price'].mean()
                        st.markdown(f"💶 **Precio medio en Málaga (general):** {precio_medio_malaga:.2f} €")
                        st.markdown(f"💶 **Precio medio en Málaga en 2024:** {precio_medio_malaga_2024:.2f} €")
                        st.markdown(f"💶 **Precio medio en Málaga en 2025:** {precio_medio_malaga_2025:.2f} €")

                        # 4. Gráfico de evolución del precio medio por años en Málaga
                        precio_medio_anual = malaga_df.groupby('year')['price'].mean().reset_index()
                        fig = px.line(
                            precio_medio_anual,
                            x='year',
                            y='price',
                            markers=True,
                            title='Evolución del Precio Medio por Año en Málaga',
                            labels={'year': 'Año', 'price': 'Precio Medio (€)'},
                            line_shape='spline'
                        )
                        fig.update_traces(line=dict(color=colors_airbnb['Rausch'], width=3), marker=dict(color=colors_airbnb['Babu'], size=8))
                        fig.update_layout(
                            plot_bgcolor=colors_airbnb['background'],
                            paper_bgcolor=colors_airbnb['background'],
                            font_color=colors_airbnb['Hof'],
                            xaxis=dict(dtick=1),
                            yaxis=dict(gridcolor='#E0E0E0')
                        )
                        st.plotly_chart(fig, use_container_width=True)

                          # 5. --- Mapa de precios y ubicación para Málaga ---
                        df_malaga = df_ult_por_listado[df_ult_por_listado['origen'] == 'Málaga'].copy()
                        size_malaga = (df_malaga['price'] / df_malaga['price'].max()) * 8 + 2
                        center_lat_malaga = df_malaga['latitude'].mean()
                        center_lon_malaga = df_malaga['longitude'].mean()

                        # Definir paleta de colores Airbnb para niveles de precio
                        airbnb_price_palette = {
                            'Precio Bajo': colors_airbnb['Babu'],    # verde azulado
                            'Precio Medio': colors_airbnb['Arches'], # naranja
                            'Precio Alto': colors_airbnb['Rausch']   # rojo coral
                        }

                        # Si no existe la columna de categoría de precio, crearla
                        if 'categoria_precio' not in df_malaga.columns:
                            p33 = df_malaga['price'].quantile(0.33)
                            p66 = df_malaga['price'].quantile(0.66)
                            def categorizar_precio(precio):
                                if precio <= p33:
                                    return 'Precio Bajo'
                                elif precio <= p66:
                                    return 'Precio Medio'
                                else:
                                    return 'Precio Alto'
                            df_malaga['categoria_precio'] = df_malaga['price'].apply(categorizar_precio)

                        # Usar scatter_map (nuevo recomendado por Plotly)
                        fig = px.scatter_map(
                            df_malaga,
                            lat="latitude",
                            lon="longitude",
                            size=size_malaga,
                            color="categoria_precio",
                            color_discrete_map=airbnb_price_palette,
                            size_max=10,
                            hover_name="name" if "name" in df_malaga.columns else None,
                            hover_data={"price": True, "latitude": False, "longitude": False},
                            title="Alojamientos en Málaga: Precio y Ubicación (por nivel de precio)"
                        )
                        fig.update_layout(
                            mapbox_style="open-street-map",
                            mapbox_zoom=8,
                            mapbox_center={"lat": center_lat_malaga, "lon": center_lon_malaga},
                            margin={"r":0,"t":40,"l":0,"b":0},
                        )
                        st.plotly_chart(fig, use_container_width=True)


                        st.markdown("### Valencia")

                        # --- Análisis específico para Valencia ---

                        # Filtrar datos solo para Valencia
                        valencia_revpar = revpar_comparado_ciudad[revpar_comparado_ciudad['origen'] == 'Valencia']
                        valencia_df = df_ult_por_listado[df_ult_por_listado['origen'] == 'Valencia'].copy()

                        # 1. RevPAR medios para Valencia
                        revpar_directo_valencia = valencia_revpar['RevPAR_directo'].mean()
                        revpar_tasa_valencia = valencia_revpar['RevPAR_ADR_tasa'].mean()
                        st.markdown(f"**RevPAR directo medio Valencia:** {revpar_directo_valencia:.2f} €")
                        st.markdown(f"**RevPAR ADR×Ocupación medio Valencia:** {revpar_tasa_valencia:.2f} €")

                        # 2. RevPAR por año en Valencia (líneas con paleta Airbnb)
                        Colors_airbnb = {
                            'RevPAR_directo': colors_airbnb['Rausch'],
                            'RevPAR_ADR_tasa': colors_airbnb['Babu']
                        }
                        df_long = valencia_revpar.melt(
                            id_vars=['origen', 'year'],
                            value_vars=['RevPAR_directo', 'RevPAR_ADR_tasa'],
                            var_name='Método', value_name='RevPAR (€)'
                        )
                        fig = px.line(
                            df_long,
                            x='year',
                            y='RevPAR (€)',
                            color='Método',
                            markers=True,
                            color_discrete_map=Colors_airbnb,
                            title='RevPAR por Año en Valencia (Directo vs ADR × Ocupación)'
                        )
                        fig.update_layout(
                            height=500,
                            showlegend=True,
                            plot_bgcolor=colors_airbnb['background'],
                            paper_bgcolor=colors_airbnb['background'],
                            font_color=colors_airbnb['Hof']
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        # 3. Precio medio en Valencia (general, 2024 y 2025)
                        precio_medio_valencia = valencia_df['price'].mean()
                        precio_medio_valencia_2024 = valencia_df[valencia_df['year'] == 2024]['price'].mean()
                        precio_medio_valencia_2025 = valencia_df[valencia_df['year'] ==  2025]['price'].mean()
                        st.markdown(f"💶 **Precio medio en Valencia (general):** {precio_medio_valencia:.2f} €")
                        st.markdown(f"💶 **Precio medio en Valencia en 2024:** {precio_medio_valencia_2024:.2f} €")
                        st.markdown(f"💶 **Precio medio en Valencia en 2025:** {precio_medio_valencia_2025:.2f} €")

                        # 4. Gráfico de evolución del precio medio por años en Valencia
                        precio_medio_anual = valencia_df.groupby('year')['price'].mean().reset_index()
                        fig = px.line(
                            precio_medio_anual,
                            x='year',
                            y='price',
                            markers=True,
                            title='Evolución del Precio Medio por Año en Valencia',
                            labels={'year': 'Año', 'price': 'Precio Medio (€)'},
                            line_shape='spline'
                        )
                        fig.update_traces(line=dict(color=colors_airbnb['Rausch'], width=3), marker=dict(color=colors_airbnb['Babu'], size=8))
                        fig.update_layout(
                            plot_bgcolor=colors_airbnb['background'],
                            paper_bgcolor=colors_airbnb['background'],
                            font_color=colors_airbnb['Hof'],
                            xaxis=dict(dtick=1),
                            yaxis=dict(gridcolor='#E0E0E0')
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        # 5. --- Mapa de precios y ubicación para Valencia ---
                        df_valencia = df_ult_por_listado[df_ult_por_listado['origen'] == 'Valencia'].copy()
                        size_valencia = (df_valencia['price'] / df_valencia['price'].max()) * 8 + 2
                        center_lat_valencia = df_valencia['latitude'].mean()
                        center_lon_valencia = df_valencia['longitude'].mean()

                        # Definir paleta de colores Airbnb para niveles de precio
                        airbnb_price_palette = {
                            'Precio Bajo': colors_airbnb['Babu'],    # verde azulado
                            'Precio Medio': colors_airbnb['Arches'], # naranja
                            'Precio Alto': colors_airbnb['Rausch']   # rojo coral
                        }

                        # Si no existe la columna de categoría de precio, crearla
                        if 'categoria_precio' not in df_valencia.columns:
                            p33 = df_valencia['price'].quantile(0.33)
                            p66 = df_valencia['price'].quantile(0.66)
                            def categorizar_precio(precio):
                                if precio <= p33:
                                    return 'Precio Bajo'
                                elif precio <= p66:
                                    return 'Precio Medio'
                                else:
                                    return 'Precio Alto'
                            df_valencia['categoria_precio'] = df_valencia['price'].apply(categorizar_precio)

                        # Usar scatter_map (nuevo recomendado por Plotly)
                        fig = px.scatter_map(
                            df_valencia,
                            lat="latitude",
                            lon="longitude",
                            size=size_valencia,
                            color="categoria_precio",
                            color_discrete_map=airbnb_price_palette,
                            size_max=10,
                            hover_name="name" if "name" in df_valencia.columns else None,
                            hover_data={"price": True, "latitude": False, "longitude": False},
                            title="Alojamientos en Valencia: Precio y Ubicación (por nivel de precio)"
                        )
                        fig.update_layout(
                            mapbox_style="open-street-map",
                            mapbox_zoom=8,
                            mapbox_center={"lat": center_lat_valencia, "lon": center_lon_valencia},
                            margin={"r":0,"t":40,"l":0,"b":0},
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        st.markdown("### Mallorca")

                        # --- Análisis específico para Mallorca ---

                        # Filtrar datos solo para Mallorca
                        mallorca_revpar = revpar_comparado_ciudad[revpar_comparado_ciudad['origen'] == 'Mallorca']
                        mallorca_df = df_ult_por_listado[df_ult_por_listado['origen'] == 'Mallorca'].copy()

                        # 1. RevPAR medios para Mallorca
                        revpar_directo_mallorca = mallorca_revpar['RevPAR_directo'].mean()
                        revpar_tasa_mallorca = mallorca_revpar['RevPAR_ADR_tasa'].mean()
                        st.markdown(f"**RevPAR directo medio Mallorca:** {revpar_directo_mallorca:.2f} €")
                        st.markdown(f"**RevPAR ADR×Ocupación medio Mallorca:** {revpar_tasa_mallorca:.2f} €")

                        # 2. RevPAR por año en Mallorca (líneas con paleta Airbnb)
                        Colors_airbnb = {
                            'RevPAR_directo': colors_airbnb['Rausch'],
                            'RevPAR_ADR_tasa': colors_airbnb['Babu']
                        }
                        df_long = mallorca_revpar.melt(
                            id_vars=['origen', 'year'],
                            value_vars=['RevPAR_directo', 'RevPAR_ADR_tasa'],
                            var_name='Método', value_name='RevPAR (€)'
                        )
                        fig = px.line(
                            df_long,
                            x='year',
                            y='RevPAR (€)',
                            color='Método',
                            markers=True,
                            color_discrete_map=Colors_airbnb,
                            title='RevPAR por Año en Mallorca (Directo vs ADR × Ocupación)'
                        )
                        fig.update_layout(
                            height=500,
                            showlegend=True,
                            plot_bgcolor=colors_airbnb['background'],
                            paper_bgcolor=colors_airbnb['background'],
                            font_color=colors_airbnb['Hof']
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        # 3. Precio medio en Mallorca (general, 2024 y 2025)
                        precio_medio_mallorca = mallorca_df['price'].mean()
                        precio_medio_mallorca_2024 = mallorca_df[mallorca_df['year'] == 2024]['price'].mean()
                        precio_medio_mallorca_2025 = mallorca_df[mallorca_df['year'] == 2025]['price'].mean()
                        st.markdown(f"💶 **Precio medio en Mallorca (general):** {precio_medio_mallorca:.2f} €")
                        st.markdown(f"💶 **Precio medio en Mallorca en 2024:** {precio_medio_mallorca_2024:.2f} €")
                        st.markdown(f"💶 **Precio medio en Mallorca en 2025:** {precio_medio_mallorca_2025:.2f} €")

                        # 4. Gráfico de evolución del precio medio por años en Mallorca
                        precio_medio_anual = mallorca_df.groupby('year')['price'].mean().reset_index()
                        fig = px.line(
                            precio_medio_anual,
                            x='year',
                            y='price',
                            markers=True,
                            title='Evolución del Precio Medio por Año en Mallorca',
                            labels={'year': 'Año', 'price': 'Precio Medio (€)'},
                            line_shape='spline'
                        )
                        fig.update_traces(line=dict(color=colors_airbnb['Rausch'], width=3), marker=dict(color=colors_airbnb['Babu'], size=8))
                        fig.update_layout(
                            plot_bgcolor=colors_airbnb['background'],
                            paper_bgcolor=colors_airbnb['background'],
                            font_color=colors_airbnb['Hof'],
                            xaxis=dict(dtick=1),
                            yaxis=dict(gridcolor='#E0E0E0')
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        # 5. --- Mapa de precios y ubicación para Mallorca ---
                        df_mallorca = df_ult_por_listado[df_ult_por_listado['origen'] == 'Mallorca'].copy()
                        size_mallorca = (df_mallorca['price'] / df_mallorca['price'].max()) * 8 + 2
                        center_lat_mallorca = df_mallorca['latitude'].mean()
                        center_lon_mallorca = df_mallorca['longitude'].mean()

                        # Definir paleta de colores Airbnb para niveles de precio
                        airbnb_price_palette = {
                            'Precio Bajo': colors_airbnb['Babu'],    # verde azulado
                            'Precio Medio': colors_airbnb['Arches'], # naranja
                            'Precio Alto': colors_airbnb['Rausch']   # rojo coral
                        }

                        # Si no existe la columna de categoría de precio, crearla
                        if 'categoria_precio' not in df_mallorca.columns:
                            p33 = df_mallorca['price'].quantile(0.33)
                            p66 = df_mallorca['price'].quantile(0.66)
                            def categorizar_precio(precio):
                                if precio <= p33:
                                    return 'Precio Bajo'
                                elif precio <= p66:
                                    return 'Precio Medio'
                                else:
                                    return 'Precio Alto'
                            df_mallorca['categoria_precio'] = df_mallorca['price'].apply(categorizar_precio)

                        # Usar scatter_map (nuevo recomendado por Plotly)
                        fig = px.scatter_map(
                            df_mallorca,
                            lat="latitude",
                            lon="longitude",
                            size=size_mallorca,
                            color="categoria_precio",
                            color_discrete_map=airbnb_price_palette,
                            size_max=10,
                            hover_name="name" if "name" in df_mallorca.columns else None,
                            hover_data={"price": True, "latitude": False, "longitude": False},
                            title="Alojamientos en Mallorca: Precio y Ubicación (por nivel de precio)"
                        )
                        fig.update_layout(
                            mapbox_style="open-street-map",
                            mapbox_zoom=8,
                            mapbox_center={"lat": center_lat_mallorca, "lon": center_lon_mallorca},
                            margin={"r":0,"t":40,"l":0,"b":0},
                        )
                        st.plotly_chart(fig, use_container_width=True)

                else:
                    st.info("No hay datos de precios disponibles para calcular la rentabilidad.")
            
            with tab_satisfaccion:
                st.markdown("### ⭐ Análisis de Satisfacción")
                
                if 'rating_numeric' in filtered_df.columns:

                    # =========================
                    # ANÁLISIS DE SATISFACCIÓN
                    # =========================

                    # Preparación de datos para el análisis de satisfacción
                    df_analysis = filtered_df.copy()

                    # Crear weighted_satisfaction (promedio ponderado de todas las métricas de review)
                    satisfaction_columns = [
                        'review_scores_rating', 'review_scores_accuracy', 'review_scores_cleanliness',
                        'review_scores_checkin', 'review_scores_communication', 'review_scores_location',
                        'review_scores_value'
                    ]

                    # Normalizar todas las métricas a escala 0-1 y calcular promedio ponderado
                    df_analysis['weighted_satisfaction'] = df_analysis[satisfaction_columns].mean(axis=1) / 5.0

                    # Definir ciudades únicas
                    cities = sorted(df_analysis['origen'].unique())

                    # Crear resumen por ciudades
                    city_summary = df_analysis.groupby('origen').agg({
                        'weighted_satisfaction': ['mean', 'std'],
                        'price_numeric': 'mean',
                        'number_of_reviews': 'mean'
                    }).round(3)

                    city_summary.columns = ['Avg_Satisfaction', 'Std_Satisfaction', 'Avg_Price', 'Avg_Reviews']

                    # Identificar mejor y peor ciudad
                    best_city = city_summary['Avg_Satisfaction'].idxmax()
                    worst_city = city_summary['Avg_Satisfaction'].idxmin()
                    satisfaction_gap = city_summary.loc[best_city, 'Avg_Satisfaction'] - city_summary.loc[worst_city, 'Avg_Satisfaction']

                    # Análisis estadístico ANOVA
                    from scipy import stats
                    city_groups = [group['weighted_satisfaction'].values for name, group in df_analysis.groupby('origen')]
                    f_stat, p_value_cities = stats.f_oneway(*city_groups)

                    # Análisis por tipo de host
                    host_analysis_by_city = df_analysis.groupby(['origen', 'host_is_superhost'])['weighted_satisfaction'].mean()

                    # Componentes por ciudad
                    city_components = df_analysis.groupby('origen')[satisfaction_columns].mean()

                    # Categorías de satisfacción
                    def categorize_satisfaction(score):
                        if score >= 0.9:
                            return 'Excelente'
                        elif score >= 0.8:
                            return 'Muy Bueno'
                        elif score >= 0.7:
                            return 'Bueno'
                        elif score >= 0.6:
                            return 'Regular'
                        else:
                            return 'Deficiente'

                    df_analysis['satisfaction_category'] = df_analysis['weighted_satisfaction'].apply(categorize_satisfaction)
                    satisfaction_by_city_category = df_analysis.groupby('origen')['satisfaction_category'].value_counts(normalize=True).unstack(fill_value=0) * 100;

                    # Visualización con Streamlit y Plotly
                    st.markdown("#### Comparativa de Satisfacción por Ciudad y Tipo de Host")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Ciudad con mayor satisfacción", f"{best_city} ({city_summary.loc[best_city, 'Avg_Satisfaction']:.3f})")
                    with col2:
                        st.metric("Ciudad con menor satisfacción", f"{worst_city} ({city_summary.loc[worst_city, 'Avg_Satisfaction']:.3f})")

                    st.markdown(f"**Brecha de satisfacción:** {satisfaction_gap:.3f} puntos")

                    # Gráfico de barras: Satisfacción promedio por ciudad
                    fig1 = px.bar(
                        city_summary.reset_index(),
                        x='origen',
                        y='Avg_Satisfaction',
                        color='origen',
                        color_discrete_sequence=list(colors_airbnb.values()),
                        title="Satisfacción promedio por ciudad"
                    )
                    st.plotly_chart(fig1, use_container_width=True)

                    # Gráfico de barras: Satisfacción por tipo de host y ciudad
                    city_host_satisfaction = df_analysis.groupby(['origen', 'host_is_superhost'])['weighted_satisfaction'].mean().unstack()
                    fig2 = go.Figure()
                    fig2.add_trace(go.Bar(
                        x=city_host_satisfaction.index,
                        y=city_host_satisfaction['f'],
                        name='Host Regular',
                        marker_color=colors_airbnb['Rausch']
                    ))
                    fig2.add_trace(go.Bar(
                        x=city_host_satisfaction.index,
                        y=city_host_satisfaction['t'],
                        name='Superhost',
                        marker_color=colors_airbnb['Babu']
                    ))
                    fig2.update_layout(
                        barmode='group',
                        title="Satisfacción por tipo de host y ciudad",
                        xaxis_title="Ciudad",
                        yaxis_title="Satisfacción ponderada"
                    )
                    st.plotly_chart(fig2, use_container_width=True)

                    # Boxplot: Distribución de satisfacción por ciudad
                    fig3 = px.box(
                        df_analysis,
                        x='origen',
                        y='weighted_satisfaction',
                        color='origen',
                        color_discrete_sequence=[colors_airbnb['Babu'], colors_airbnb['Rausch'], colors_airbnb['Arches']],
                        title="Distribución de satisfacción ponderada por ciudad"
                    )
                    st.plotly_chart(fig3, use_container_width=True)

                    # Gráfico de componentes de satisfacción por ciudad
                    components = [
                        'review_scores_rating', 'review_scores_cleanliness', 'review_scores_communication',
                        'review_scores_accuracy', 'review_scores_checkin', 'review_scores_location', 'review_scores_value'
                    ]
                    component_names = [
                        'Valoración General', 'Limpieza', 'Comunicación', 'Precisión',
                        'Check-in', 'Ubicación', 'Relación Calidad-Precio'
                    ]
                    city_components_plot = city_components.copy()
                    city_components_plot.columns = component_names
                    fig4 = px.bar(
                        city_components_plot.reset_index().melt(id_vars='origen'),
                        x='variable',
                        y='value',
                        color='origen',
                        barmode='group',
                        title="Componentes de satisfacción por ciudad",
                        labels={'variable': 'Componente', 'value': 'Puntuación promedio'}
                    )
                    st.plotly_chart(fig4, use_container_width=True)

                    # Gráfico de barras apiladas: Distribución de categorías de satisfacción por ciudad
                    fig5 = px.bar(
                        satisfaction_by_city_category.reset_index(),
                        x='origen',
                        y=['Excelente', 'Muy Bueno', 'Bueno', 'Regular', 'Deficiente'],
                        title="Distribución de categorías de satisfacción por ciudad",
                        labels={'value': 'Porcentaje (%)', 'origen': 'Ciudad'},
                        color_discrete_sequence=list(colors_airbnb.values())
                    )
                    st.plotly_chart(fig5, use_container_width=True)

                    # Tabla resumen por ciudad
                    st.markdown("##### 📋 Resumen de satisfacción por ciudad")
                    st.dataframe(city_summary.style.background_gradient(cmap='Blues'), use_container_width=True)

                    # Análisis por tipo de host en cada ciudad
                    st.markdown("##### 👥 Ventaja de Superhost por ciudad")
                    for city in cities:
                        try:
                            regular_sat = host_analysis_by_city.loc[(city, 'f')] if (city, 'f') in host_analysis_by_city.index else None
                            super_sat = host_analysis_by_city.loc[(city, 't')] if (city, 't') in host_analysis_by_city.index else None
                            if regular_sat is not None and super_sat is not None:
                                difference = super_sat - regular_sat
                                improvement = (difference / regular_sat * 100)
                                trend = "📈" if difference > 0 else "📉" if difference < 0 else "➡️"
                                st.markdown(
                                    f"{trend} **{city}**: Host Regular = {regular_sat:.3f} | Superhost = {super_sat:.3f} | "
                                    f"Ventaja Superhost: {difference:+.3f} ({improvement:+.1f}%)"
                                )
                            else:
                                st.markdown(f"⚠️ {city}: Datos incompletos de superhost")
                        except Exception as e:
                            st.markdown(f"❌ Error procesando {city}: {str(e)}")

                    # Análisis estadístico
                    significance = "SÍ" if p_value_cities < 0.05 else "NO"
                    st.markdown(f"**¿Diferencias estadísticamente significativas entre ciudades?** {significance} (p = {p_value_cities:.2e})")
            
                else:
                    st.info("No hay datos de satisfacción disponibles para mostrar el análisis.")


            with tab_conclusiones:
                st.markdown("### 📋 Conclusiones y Recomendaciones")
                
                # Análisis y conclusiones automáticas basadas en los datos
                st.subheader("🔍 Insights Principales")
                
                if len(filtered_df) > 0:
                    conclusions = []
                    
                    # Análisis de precios por ciudad
                    if 'origen' in filtered_df.columns and 'price_numeric' in filtered_df.columns:
                        city_prices = filtered_df.groupby('origen')['price_numeric'].mean().sort_values(ascending=False)
                        most_expensive = city_prices.index[0]
                        least_expensive = city_prices.index[-1]
                        conclusions.append(f"🏆 **{most_expensive}** es la ciudad más cara con un precio promedio de {city_prices.iloc[0]:.0f}€")
                        conclusions.append(f"💰 **{least_expensive}** es la ciudad más económica con un precio promedio de {city_prices.iloc[-1]:.0f}€")
                    
                    # Análisis de calidad
                    if 'rating_numeric' in filtered_df.columns:
                        rating_promedio = filtered_df['rating_numeric'].mean()
                        if rating_promedio >= 4.5:
                            conclusions.append("⭐ La satisfacción de los huéspedes es excelente en general")
                        elif rating_promedio >= 4.0:
                            conclusions.append("⭐ La satisfacción de los huéspedes es buena, pero hay margen de mejora")
                        else:
                            conclusions.append("⚠️ La satisfacción de los huéspedes es baja, se recomienda mejorar la experiencia")
                    
                    # Análisis de superhosts
                    if 'host_is_superhost' in filtered_df.columns:
                        superhost_pct = (filtered_df['host_is_superhost'] == 't').mean() * 100
                        conclusions.append(f"👑 {superhost_pct:.1f}% de los listings son gestionados por Superhosts")
                    
                    # Análisis de ocupación
                    if 'availability_365' in filtered_df.columns:
                        ocupacion_media = 100 - (filtered_df['availability_365'].mean() / 365 * 100)
                        conclusions.append(f"📈 La ocupación promedio es del {ocupacion_media:.1f}%")
                    
                    # Mostrar conclusiones
                    for conclusion in conclusions:
                        st.markdown(f"- {conclusion}")
                
                st.markdown("---")
                
                st.subheader("💡 Recomendaciones Estratégicas")
                
                recommendations = [
                    "🎯 **Para Inversores**: Considerar propiedades en zonas con alta ocupación y precios estables",
                    "🏠 **Para Hosts**: Aspirar al estatus de Superhost para mejorar visibilidad y tarifas",
                    "📊 **Optimización de Precios**: Analizar competencia local y ajustar precios según temporada",
                    "⭐ **Mejora de Calidad**: Invertir en amenities y servicio al cliente para mejorar ratings",
                    "📈 **Marketing**: Enfocar promociones en períodos de baja ocupación",
                    "🔍 **Análisis Continuo**: Monitorear tendencias del mercado y ajustar estrategias"
                ]
                
                for rec in recommendations:
                    st.markdown(f"• {rec}")
                
                # Añadir métricas finales
                st.markdown("---")
                st.subheader("📊 Resumen Ejecutivo")
                
                if len(filtered_df) > 0:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        total_listings = len(filtered_df)
                        st.metric("Total Análisis", f"{total_listings:,}")
                    
                    with col2:
                        if 'price_numeric' in filtered_df.columns:
                            precio_med = filtered_df['price_numeric'].mean()
                            st.metric("Precio Medio", f"{precio_med:.0f}€")
                    
                    with col3:
                        if 'rating_numeric' in filtered_df.columns:
                            rating_med = filtered_df['rating_numeric'].mean()
                            st.metric("Calidad Media", f"{rating_med:.2f}/5.0")
                    
                    with col4:
                        if 'availability_365' in filtered_df.columns:
                            ocupacion = ((365 - filtered_df['availability_365']) / 365 * 100).mean()
                            st.metric("Ocupación Media", f"{ocupacion:.1f}%")
        
        else:
            st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados.")
            st.info("💡 Prueba ajustando los filtros para obtener resultados.")
else:
    st.error("❌ No se pudo cargar los datos. Verifique la conexión a la base de datos.")
    st.info("**Pasos para solucionar:**")
    st.markdown("""
    1. Verificar que el servidor SQL esté disponible
    2. Confirmar credenciales de acceso
    3. Verificar que la tabla `listings_completo` existe
    4. Instalar dependencias: `pip install -r requirements.txt`
    """)

# Información de conexión
with st.expander("ℹ️ Información de conexión"):
    st.write("**Servidor:** upgrade-abnb-server.database.windows.net")
    st.write("**Base de datos:** Upgrade_Abnb")
    st.write("**Tabla:** listings_completo")
    st.write("**Usuario:** vmabnbserver")
