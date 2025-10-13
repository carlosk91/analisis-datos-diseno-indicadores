# Proyecto Final – Caso: Lending Club

**Contexto:** Eres parte del equipo de análisis de datos de **Lending Club**, una plataforma de préstamos P2P que conecta inversionistas con prestatarios. La empresa busca mejorar sus decisiones de riesgo, rentabilidad y crecimiento utilizando únicamente los datos históricos disponibles del **dataset de Lending Club**.

**Formato:** Equipos de 4 personas
**Entrega:** 1) *Notebook* (.ipynb) con todo el código, análisis y visualizaciones. 2) Presentación ejecutiva (PPT/Canva/Slides) de **15 minutos** + **5 min Q&A**.
**Enfoque:** Aplicar análisis **descriptivo, diagnóstico, predictivo y prescriptivo** sobre los datos históricos de préstamos.

---

## 1) Contexto de negocio

Como analista de datos de **Lending Club**, tienes los datos de todos los préstamos otorgados (monto, tasa, estado, propósito, ingresos, antigüedad laboral, score crediticio, etc.) y quieres responder preguntas clave para optimizar el portafolio de préstamos, la gestión del riesgo y la rentabilidad.

---

## 2) Preguntas de negocio clave

Estas son las preguntas que el equipo de Analytics debe resolver usando el dataset:

### A. Análisis descriptivo – ¿Qué está pasando?

* ¿Cómo se distribuyen los préstamos por grado de riesgo (grade/subgrade)?
* ¿Qué proporción de préstamos está en mora (*charged-off*, *late*, *fully paid*)?
* ¿Cuáles son los propósitos de préstamo más frecuentes y qué ticket promedio tienen?
* ¿Cómo se comportan los ingresos y la relación *debt-to-income* (DTI) de los clientes?

### B. Análisis diagnóstico – ¿Por qué ocurre?

* ¿Qué factores explican la probabilidad de impago? (ej. tasa de interés, DTI, antigüedad laboral, monto solicitado)
* ¿Hay patrones de comportamiento por categoría de préstamo o nivel de ingreso?
* ¿Existen relaciones entre el score crediticio, la tasa de interés y el *loan status*?

### C. Análisis predictivo – ¿Qué podría pasar?

* ¿Podemos predecir la probabilidad de que un préstamo entre en mora o se pague completamente? (clasificación)
* ¿Podemos estimar el rendimiento esperado o *loss rate* de un préstamo? (regresión)
* ¿Qué variables explican mejor el desempeño crediticio?

### D. Análisis prescriptivo – ¿Qué deberíamos hacer?

* Si ajustamos los criterios de aprobación (por ejemplo, DTI o score mínimo), ¿cómo afectaría eso la tasa de aprobación y el *loss rate*?
* ¿Qué segmentos de clientes deberíamos priorizar para aumentar la rentabilidad?
* ¿Cómo podríamos diseñar una política de tasas de interés más eficiente según el perfil de riesgo?

---

## 3) Objetivo general

Usando los datos de Lending Club, el equipo debe:

1. **Analizar** el portafolio de préstamos para entender el perfil del cliente y los determinantes del impago.
2. **Modelar** la relación entre características del préstamo y el rendimiento del portafolio.
3. **Recomendar** acciones basadas en los resultados que permitan optimizar el riesgo y la rentabilidad.

---

## 4) Entregables

**A. Notebook (Jupyter):**

1. **Carga de datos y exploración:** inspección inicial y descripción de variables.
2. **Limpieza de datos:** manejo de nulos, duplicados, outliers y trazabilidad.
3. **Análisis descriptivo:** KPIs (porcentaje de impagos, *loss rate*, rentabilidad media, distribución por grado, DTI promedio).
4. **Diagnóstico:** correlaciones, visualizaciones de relaciones (ej. DTI vs tasa de interés vs estado del préstamo), pruebas de hipótesis básicas.
5. **Predictivo:** modelo sencillo de regresión o clasificación con métricas **RMSE, MAE o R²**, interpretabilidad y comparación con un baseline.
6. **Prescriptivo:** escenarios “what-if” (p. ej., modificar criterios de score o DTI y ver impacto en *loss rate* y volumen aprobado).
7. **Conclusiones:** insights de negocio, riesgos y próximos pasos.

**B. Presentación ejecutiva:**

1. Contexto y objetivo de negocio.
2. Limpieza y calidad de los datos.
3. Hallazgos descriptivos y diagnósticos.
4. Resultados predictivos y métricas.
5. Escenarios prescriptivos y recomendaciones para el negocio.

---

## 5) Indicadores sugeridos (KPIs)

* **Tasa de aprobación:** % de préstamos emitidos / solicitados.
* **Tasa de impago:** % de préstamos en mora o *charged-off*.
* **Loss rate:** monto perdido / monto prestado.
* **Yield promedio:** interés cobrado efectivo.
* **DTI promedio:** deuda / ingreso.
* **Tasa de recuperación:** pagos recuperados / monto en mora.

---

## 6) Rúbrica de evaluación (100 pts)

**A. Descriptivo (25 pts)** – KPIs, exploración, visualizaciones.
**B. Diagnóstico (25 pts)** – relaciones, pruebas de hipótesis, interpretación.
**C. Predictivo (25 pts)** – uso de RMSE, MAE, R²; baseline y análisis de errores.
**D. Prescriptivo y presentación (25 pts)** – escenarios, recomendaciones, claridad ejecutiva.

---

## 7) Reglas y notas técnicas

* Se pueden usar **pandas**, **numpy**, **matplotlib**, **seaborn**, **scikit-learn**, **scipy**.
* Todas las decisiones de limpieza deben documentarse con antes/después.
* No se requiere conocimiento avanzado de ML: basta con modelos interpretables (regresión lineal, regresión logística, árbol de decisión simple).
* Las recomendaciones deben basarse en KPIs observados o simulados.

---

## 8) Preguntas guía para la presentación final

1. ¿Qué aprendimos del comportamiento histórico de Lending Club?
2. ¿Qué factores influyen más en el impago o en el rendimiento?
3. ¿Cómo cambiarían nuestros resultados si modificamos las políticas de aprobación?
4. ¿Qué decisiones puede tomar la dirección basadas en estos hallazgos?
5. ¿Qué riesgos o sesgos encontramos en los datos?

---

### Resultado esperado

Un análisis integral que permita responder:

> “¿Cómo puede Lending Club aumentar su rentabilidad sin comprometer la calidad de su portafolio de préstamos?”
