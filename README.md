<style>
body {
    background-image: url('image/Image (5).jpg');
    background-size: cover;
    background-repeat: no-repeat;
    background-attachment: fixed;
}
</style>

# Plataforma de Análisis de Airbnb

## Descripción
Este proyecto implementa una plataforma avanzada de análisis de datos para propiedades de Airbnb. La herramienta permite a usuarios, propietarios y analistas de mercado visualizar y analizar información detallada sobre alojamientos, comportamiento de precios, distribuciones geográficas y tendencias del mercado inmobiliario turístico.

## Tabla de Contenidos
- [Instalación](#instalación)
- [Características](#características)
- [Estructura del Dashboard](#estructura-del-dashboard)
- [Análisis Realizados](#análisis-realizados)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Equipo](#equipo)
- [Licencia](#licencia)
- [Contacto](#contacto)

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/usuario/Plataforma-Airbnb.git

# Navegar al directorio del proyecto
cd Plataforma-Airbnb

# Crear y activar entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python app.py
```

## Características

- **Dashboard Interactivo**: Visualización dinámica e interactiva de datos de propiedades
- **Análisis de Precios**: Algoritmos avanzados para estudio de patrones de precios por zona y temporada
- **Visualización Geoespacial**: Mapas de calor e indicadores de densidad de alojamientos
- **Modelos Predictivos**: Predicciones de tendencias de precios basadas en aprendizaje automático
- **Análisis Comparativo**: Herramientas para comparar métricas entre diferentes ciudades o regiones
- **Exportación de Datos**: Capacidad de exportar resultados en múltiples formatos

## Estructura del Dashboard

- **General**
        - Alojamientos
        - Hosts
- **Ocupación**
        - General
        - Mallorca
        - Málaga
        - Valencia
- **Rentabilidad**
        - General
        - Mallorca
        - Málaga
        - Valencia
- **Satisfacción**
        - General
        - Mallorca
        - Málaga
        - Valencia
- **Conclusiones**

## Análisis Realizados

- **Análisis de Precios**: Estudio detallado de variables que influyen en los precios de alojamientos, incluyendo factores estacionales, características de la propiedad y dinámicas de oferta-demanda
- **Análisis Geoespacial**: Distribución de propiedades y correlación con puntos de interés turístico, transporte y servicios
- **Análisis de Sentimiento**: Evaluación cuantitativa de reseñas y satisfacción de clientes mediante técnicas de NLP
- **Segmentación de Mercado**: Clasificación multidimensional de propiedades por características, rendimiento y público objetivo
- **Tendencias Temporales**: Estudio de la evolución del mercado a lo largo del tiempo y predicción de comportamientos futuros

## Tecnologías Utilizadas

- **Lenguajes**: Python 3.8+
- **Análisis de Datos**: Pandas, NumPy, SciPy
- **Visualización**: Matplotlib, Seaborn, Plotly, Folium
- **Frontend**: Flask/Streamlit
- **Machine Learning**: Scikit-learn, TensorFlow para modelos predictivos
- **Base de Datos**: PostgreSQL/MongoDB
- **Despliegue**: Docker, AWS/GCP

## Estructura del Proyecto

```
Plataforma-Airbnb/
├── app.py                  # Punto de entrada principal
├── requirements.txt        # Dependencias del proyecto
├── data/                   # Conjuntos de datos y recursos
├── models/                 # Modelos de aprendizaje automático
├── notebooks/              # Jupyter notebooks para análisis exploratorio
├── src/                    # Código fuente principal
│   ├── preprocessing/      # Módulos de preprocesamiento de datos
│   ├── visualization/      # Componentes de visualización
│   └── analysis/           # Algoritmos de análisis
└── tests/                  # Pruebas unitarias y de integración
```

## Equipo

- **Belén Parrado Serrano** - Analista de Datos - [GitHub](https://github.com/usuario)
- **Victor Marti** - Analista de Datos - [GitHub](https://github.com/usuario)
- **Andrei Baidurov** - Analista de Datos - [GitHub](https://github.com/usuario)

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - vea el archivo [LICENSE.md](LICENSE.md) para más detalles.

## Contacto

Para consultas o colaboraciones, por favor contacte a través de [email@ejemplo.com](mailto:email@ejemplo.com) o abra un issue en este repositorio.
