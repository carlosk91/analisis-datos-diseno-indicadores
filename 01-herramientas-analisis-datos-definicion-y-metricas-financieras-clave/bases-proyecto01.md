# Proyecto Final – Caso: Lending Club

**Contexto:** Eres parte del equipo de análisis de datos de **Lending Club**, una plataforma de préstamos P2P que conecta inversionistas con prestatarios. La empresa busca entender, diagnosticar y optimizar su desempeño financiero utilizando únicamente los datos históricos disponibles del **dataset de Lending Club**.

**Formato:** Equipos de 4 personas
**Entrega:** 1) *Notebook* (.ipynb) con todo el análisis y visualizaciones. 2) Presentación ejecutiva (PPT/Canva/Slides) de **15 minutos** + **5 min Q&A**.

---

## 1) Contexto de negocio

Como analista de **Lending Club**, cuentas con los datos históricos de préstamos: monto, tasa, score, ingresos, propósito, antigüedad laboral, estado del préstamo, entre otros. Tu objetivo es identificar patrones de riesgo, rentabilidad y eficiencia operativa que orienten la toma de decisiones de negocio.

---

## 2) Preguntas de negocio clave

### A. Análisis descriptivo – ¿Qué está pasando?

* ¿Cómo se distribuyen los préstamos por grado de riesgo (*grade/subgrade*) y por propósito?
* ¿Cuál es la proporción de préstamos en mora (*charged-off*, *late*, *fully paid*)?
* ¿Qué características tienen los clientes con mejores tasas de repago? (edad, ingreso, score, DTI)

### B. Análisis diagnóstico – ¿Por qué ocurre?

* ¿Qué factores se relacionan con la probabilidad de impago o pérdida?
* ¿Cómo impactan la tasa de interés, el DTI o el ingreso en la rentabilidad?
* ¿Existen diferencias significativas entre segmentos de clientes o tipos de préstamo?

### C. Análisis explicativo / regresión – ¿Qué variables influyen más?

* Utiliza **modelos de regresión simples o múltiples** (lineales o logísticos) para cuantificar relaciones. Ejemplos:

  * ¿Cómo influye la tasa de interés y el DTI en el rendimiento del préstamo?
  * ¿Qué variables predicen mejor el *loss rate* o el *yield*?
* Evalúa tus modelos con **RMSE, MAE o R²** y enfócate en **interpretar los coeficientes**, no en optimizar.

### D. Análisis prescriptivo – ¿Qué deberíamos hacer?

* Si modificamos los criterios de aprobación (ej. score mínimo o DTI máximo), ¿cómo cambiaría el portafolio?
* ¿Qué segmentos de clientes son más rentables o menos riesgosos?
* ¿Qué estrategias podríamos implementar para mejorar el rendimiento del portafolio?

Ejemplo de tabla de escenarios:

| Política                      | Aprobaciones | Loss Rate | Yield Esperado |
| ----------------------------- | ------------ | --------- | -------------- |
| Actual                        | 100%         | 6%        | 12%            |
| Escenario A (más conservador) | 85%          | 3%        | 10%            |
| Escenario B (más agresivo)    | 110%         | 8%        | 13%            |

---

## 3) Entregables

**A. Notebook (Jupyter):**

1. **Carga y exploración inicial:** descripción de variables y dimensiones del dataset.
2. **Limpieza de datos:** manejo de nulos, duplicados y outliers, documentando decisiones antes/después.
3. **Análisis descriptivo:** construcción de KPIs clave (tasa de impago, loss rate, yield promedio, DTI promedio) y visualizaciones con *takeaways* claros.
4. **Análisis diagnóstico:** correlaciones, pruebas de hipótesis y segmentaciones.
5. **Análisis explicativo (regresiones):** modelos simples para entender la influencia de variables sobre KPIs.
6. **Análisis prescriptivo:** escenarios “what-if” con impacto en rentabilidad y riesgo.
7. **Conclusiones:** aprendizajes, riesgos y recomendaciones.

**B. Presentación ejecutiva (15 min):**

1. Contexto y objetivo de negocio.
2. Limpieza y calidad de los datos.
3. Hallazgos descriptivos (gráficas e insights clave).
4. Diagnóstico y regresiones interpretativas.
5. Escenarios prescriptivos y recomendaciones concretas.

---

## 4) Indicadores sugeridos (KPIs)

* **Tasa de aprobación** = préstamos emitidos / solicitados.
* **Tasa de impago** = préstamos en mora o *charged-off* / total.
* **Loss rate** = monto perdido / monto prestado.
* **Yield promedio** = interés efectivo promedio.
* **DTI promedio** = deuda / ingreso.
* **Tasa de recuperación** = pagos recuperados / monto en mora.

---

## 5) Rúbrica de evaluación (100 pts)

| Dimensión                       | Puntos | Descripción                                                                   |
| ------------------------------- | ------ | ----------------------------------------------------------------------------- |
| **Descriptivo**                 | 30     | KPIs claros, visualizaciones informativas, narración con sentido de negocio.  |
| **Diagnóstico**                 | 25     | Relaciones entre variables, correlaciones e hipótesis interpretadas.          |
| **Explicativo (regresiones)**   | 15     | Modelos simples, interpretación de coeficientes, uso correcto de RMSE/MAE/R². |
| **Prescriptivo + Presentación** | 30     | Escenarios simulados, decisiones accionables, claridad ejecutiva.             |

> **Bonos (+5 pts):** cohorte de análisis temporal, dashboards bien diseñados, interpretación financiera sólida.

---

## 6) Reglas técnicas

* Usar **pandas**, **numpy**, **matplotlib**, **seaborn**, **scikit-learn**, **scipy**.
* Documentar todas las transformaciones y limpiezas.
* Los modelos deben ser **interpretables**, no complejos.
* El foco está en **entender, visualizar y comunicar**, no en optimizar.

---

## 7) Preguntas guía para la presentación

1. ¿Qué patrones relevantes identificamos en el portafolio de Lending Club?
2. ¿Qué factores explican mejor el rendimiento o impago?
3. ¿Qué decisiones de negocio se desprenden de los análisis?
4. ¿Qué escenarios alternativos pueden mejorar los KPIs?
