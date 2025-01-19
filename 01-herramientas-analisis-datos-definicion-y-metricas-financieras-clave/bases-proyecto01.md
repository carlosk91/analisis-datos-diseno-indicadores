# Proyecto: Análisis socioeconómico de Los Ángeles—crimen, negocios y bienes raíces

## Objetivo

Analizar la relación entre la tasa de crimen, actividad comercial y precios de bienes raíces en la ciudad de Los Ángeles utilizando datasets reales. 
Es necesario desarrollar indicadores que puedan relacionar las tres dimensiones de la ciudad. Para ello, el estudiante deberá utilizar los datos geoespaciales
de los tres datasets para poder lograr la unión. 

## Contexto

Eres el nuevo alcalde de Los Ángeles. Con una población de 3.8 millones de personas es difícil concentrarte en todos los problemas que ocurren en la ciudad. Sin embargo, a los angelinos les preocupa mayormente: 

* Crimen
* Pequeños negocios (una economía ágil)
* Precios de sus propiedades

Los Ángeles se divide en ~114 vecindarios, esto te ayudará a dividir y conquistar el problema. Para que puedas apoyar al mayor número de personas, podrías responder preguntas como: 

* ¿Qué vecindarios tienen una mayor tasa de *muerte de negocios*?, ¿se relaciona con la tasa de crimen?
* ¿Qué vecindarios tienen la mayor tasa de crimen?, ¿necesitan mayor atención policial?
* ¿Está esto afectando a los precios de las propiedades?

## Datasets

1.  **Crime Data (2020-Present):** [link](https://data.lacity.org/Public-Safety/Crime-Data-from-2020-to-Present/2nrs-mtv8/about_data)
    *   **Fuente:** Los Angeles Open Data portal 
    *   **Granularidad:** Nivel incidente, gravedad, tipo de crimen, fecha, hora, ubicación (con coordenadas), etc.
    *   **Variables potenciales:**
        *   Tasa de crimen por vecindario
        *   Tipos de crimen (violentos vs. no violentos)
        *   Frecuencia de tipos de crimen (por año)
    *   **Nota:** Podríamos también usar 2010-2019 [link](https://data.lacity.org/Public-Safety/Crime-Data-from-2010-to-2019/63jg-8b9z/about_data)

2.  **Negocios Activos e Inactivos:** [link](https://data.lacity.org/Administration-Finance/Listing-of-All-Businesses/r4uk-afju/about_data)
    *   **Fuente:** Los Angeles Open Data portal
    *   **Granularidad:** Negocio, dirección, nombre, tipo de negocio, fecha de inicio, fecha de cierre (si existe)
    *   **Variables potenciales:**
        *   Densidad de negocios (por vecindario o por kilómetro cuadrado)
        *   Tipos de negocios (e.g., retail, restaurants, servicios)
        *   Churn rate de negocios por vecindario
        *   Edad promedio de los negocios

3.  **Zillow Housing Prices:** [link](https://www.zillow.com/research/data/) 
    *   **Pasos para descarga**
        *   Ir a Home Values
        *   Geography: 'Neighborhood'
        *   Data Type: 'ZHVI All Homes (SFR, Condo/Co-op) Time Series, Smoothed, Seasonally Adjusted($)'
    *   **Fuente:** Zillow Research Data
    *   **Granularidad:** Nivel vecindario, mes a mes, mediana del precio de las propiedades.
    *   **Variables potenciales:**
        *   Mediana del precio de las propiedades
        *   Cambio de la mediana a través del tiempo en el vecindario (e.g., YoY)

### Helper Datasets de los vecindarios

4. **Área por vecindario:** [link](https://geohub.lacity.org/datasets/691805703915458da4b35d8088f29501_0/explore?location=34.019250%2C-118.411774%2C9.84)
    *   *Helper Dataset* que servirá para obtener el área de un vecindario en millas cuadradas. 

5. **Coordenadas por vecindario:** [link](https://geohub.lacity.org/datasets/d6c55385a0e749519f238b77135eafac_0/explore?location=34.065299%2C-118.425582%2C11.05)
    *   *Helper Dataset* que servirá para convertir las coordenadas en el dataset de crimen y dataset de Negocios en un **vecindario** y unir los datasets.

6. **Población por vecindario:** [link](https://data.lacity.org/Community-Economic-Development/Census-Data-by-Neighborhood-Council/nwj3-ufba/about_data)
    *   *Helper Dataset* que servirá para obtener variables demográficas como: población total y desglose de población por etnicidad. 

# Etapas del proyecto

## Fase 1: Adquisición y Limpieza de datos

1.  **Environment Setup:**
    *   Instalación de librerías necesarias: pandas, numpy, geopandas, matplotlib, seaborn, sklearn, statsmodels. 
2.  **Adquisición de datos:**
    *   Descarga de datasets.
3.  **Exploración y limpieza de datos:**
    *   **Dataset de crimen:**
        *   Manejo de nulos
        *   Manejo de variables geoespaciales
        *   Manejo de variables categóricas (texto)
        *   Manejo de variables de fecha
    *   **Dataset de negocios**
        *   Manejo de nulos
        *   Manejo de variables geoespaciales
        *   Manejo de variables categóricas (texto)
        *   Manejo de variables de fecha
    *   **Dataset de Zillow:**
        *   Manejo de nulos
        *   Manejo de variables categóricas (texto)
        *   Manejo de variables de fecha
4.  **Transformación e integración de datos:**
    *   **Agregación Espacial:** 
        *   Los estudiantes tendrán que unir los datasets por medio del **vecindario**. Para ello, necesitarán correr un algoritmo, posiblemente provisto por el profesor para
        que los pares de coordenadas se localicen dentro de un **vecindario**.

## Fase 2: Análisis y diseño de indicadores

1.  **Definición y cálculo de indicadores:**
    *   Proponer al menos **cuatro KPIs** que capturen distintos aspectos de la relación entre crimen, negocios y bienes raíces en un vecindario. 
    *   Explica cada indicador, porqué crees que es relevante y porqué lo calculaste de esa manera. 

2.  **Perfil de un vecindario:**
    *   Selecciona de 3-5 vecindarios con características contrastantes (e.g., alto y bajo crimen, alto y bajo valor de propiedades).
    *   Describe sus características. 

## Fase 3: Análisis Avanzado

1.  **Correlaciones:**
    *   Calcula correlaciones entre indicadores, recuerda que **no** indican causalidad. 
    *   Visualiza las correlaciones. 
    *   ¿Tienen sentido?

2.  **Regresión:**
    *   Construye modelos de regresión para medir factores que pueden influenciar a variables.

3.  **Análisis de clusters:**
    *   Agrupa a los vecindarios de acuerdo a tus indicadores.
    *   Determina el número óptimo de clusters utilizando las técnicas vistas en clase.
    *   **Interpreta** los clusters.
    *   Visualiza los clusters en un mapa. 

4.  **SEM:**
    *   Utilizando tus KPIs, determina una variable latente como la felicidad de los habitantes del vecindario.
    *   Utiliza SEM para medir esa variable. 
    *   ¿Tiene sentido?

5.  **Series de tiempo:**
    *   Analiza las tendencias en tus KPIs.
    *   Utiliza series de tiempo para identificar tendencias, temporalidad y patrones cíclicos, si es que aplica. 
    *   Potencialmente, podrías aplicar técnicas para hacer un forecast de futuras tendencias. 

# Evaluación

*   **Adquisición y Limpieza de datos (15%)**
*   **Análisis y Diseño de Indicadores (25%)** 
*   **Análisis Avanzado (40%)**
*   **Presentación de Resultados (20%)**

**Entregables:**

*   **Presentación Ejecutiva**
    *   Presentación al grupo

