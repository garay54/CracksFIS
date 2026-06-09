# <span style="color:#e06c75">Comentarios de Consenso</span> <span style="color:#98c379">— en lenguaje natural</span>

<span style="color:#abb2bf">Estos son los 9 puntos donde coincidimos todos los revisores, reescritos como los dirías tú al marcar el paper. Sin tecnicismos, directo al grano. Cada comentario incluye la referencia exacta para que los autores sepan a qué responde.</span>

---

### <span style="color:#e06c75">4.</span> Las ecuaciones permiten clasificar un segmento como A y C al mismo tiempo

<span style="color:#c678dd">**Referencia para los autores:** Sección III.D "Formal Definitions of Melodic Functions", Ecuaciones (1) y (2).</span>

**<span style="color:#98c379">Dónde marcar:</span>** Ecuaciones (1) y (2) en la Sección III.D. Encierra los símbolos de "o" (∨) en ambas.

**<span style="color:#61afef">Comentario al margen:</span>**
> "Esto está mal. Si un segmento tiene el tono subiendo Y la energía bajando al mismo tiempo, cumple ambas condiciones a la vez: la ecuación 1 dice que es A, la 2 dice que es C. No dice en ningún lado cuál gana. ¿Qué hace el programa en ese caso? Hay que arreglar esto antes de interpretar resultados."

---

### <span style="color:#e06c75">7.</span> Usan el mismo umbral de "voicing" para todos los extractores, y no son comparables

<span style="color:#c678dd">**Referencia para los autores:** Sección III.E "MC-MSA Framework Algorithm", Algoritmo 1, línea 6 (`prob(s_i) < τ_voicing`), en conjunto con Tabla I, fila "Voicing Threshold" (`τ_voicing = 0.5`).</span>

**<span style="color:#98c379">Dónde marcar:</span>** Algoritmo 1, línea 6 (`if prob < 0.5`). Traza una flecha hacia la Tabla I (τ_voicing = 0.5).

**<span style="color:#61afef">Comentario al margen:</span>**
> "Le ponen el mismo filtro de 0.5 a 8 extractores distintos, como si todos midieran la confianza en la misma escala. Cada uno da un número distinto cuando 'no está seguro'. Así están favoreciendo o castigando a cada extractor sin darse cuenta."

---

### <span style="color:#e06c75">8.</span> El pipeline es una cadena sin control de errores

<span style="color:#c678dd">**Referencia para los autores:** Sección III.E, Algoritmo 1 (líneas 1 a 12) y Sección IV.E "Discussion and Error Propagation", párrafo 1.</span>

**<span style="color:#98c379">Dónde marcar:</span>** Algoritmo 1 completo. Traza un corchete vertical sobre las líneas 1→4→5→9 y escribe "EFECTO DOMINÓ" al lado.

**<span style="color:#61afef">Comentario al margen:**
> "Todo depende de todo. Si el separador de voces falla, el f₀ sale mal, el SSM se hace con basura, las fronteras quedan en cualquier lado, y el clasificador decide sobre segmentos que ni siquiera son frases reales. Los autores lo mencionan de pasada en la discusión pero nunca miden cuánto empeora en cada paso. Sin ese desglose, los números de la Tabla II no se sabe de dónde vienen."

---

### <span style="color:#e06c75">9.</span> 80 pares y encima todos del mismo tipo (original→acústico)

<span style="color:#c678dd">**Referencia para los autores:** Sección IV.A "Dataset and Setup", párrafo 1 (frase *"a curated corpus of 80 pairs of musical works (160 tracks in total)"*), en conjunto con los párrafos 2 y 3 que describen el diseño original→acústico.</span>

**<span style="color:#98c379">Dónde marcar:</span>** Sección IV.A, la frase *"a curated corpus of 80 pairs"*. Enciérrala.

**<span style="color:#61afef">Comentario al margen:</span>**
> "80 pares es poquísimo para medir diferencias de 2 o 3 puntos entre métodos. Y solo probaron 'original producido → cover acústico'. ¿Qué pasa si el cover es en otro tono, o es instrumental, o cambia la estructura? Así no se puede afirmar que la melodía es invariante en general. Ellos mismos mencionan Covers80 al final… pues úsenlo."

---

### <span style="color:#e06c75">10.</span> Afinaron los parámetros sobre los mismos datos que usaron para evaluar

<span style="color:#c678dd">**Referencia para los autores:** Sección IV.B "Parameter Justification and Heuristic Tuning", ítems 1, 2 y 3. Específicamente, frase *"was identified as the optimal indicator"* en el ítem 2 (Energy Decay Threshold), y el hecho de que no se reporta partición train/dev/test ni conjunto held-out en ninguna parte de la sección.</span>

**<span style="color:#98c379">Dónde marcar:</span>** Sección IV.B, los tres ítems. Encierra la palabra "optimal" en el ítem 2.

**<span style="color:#61afef">Comentario al margen:</span>**
> "Dicen que los valores son 'óptimos'. ¿Óptimos con respecto a qué? Si ajustaron ε, τₑ y δ probando sobre los mismos 80 pares de la Tabla II, los resultados no valen: están inflados porque ya 'sabían' las respuestas. ¿Hubo un conjunto separado para afinar? Si no, hay que rehacer las pruebas o al menos mostrar qué pasa si cambian los valores un poco."

---

### <span style="color:#e06c75">12.</span> El DTW de RMVPE no cuadra con los demás

<span style="color:#c678dd">**Referencia para los autores:** Tabla II, columna "DTW", fila correspondiente al método RMVPE (fila 5). El valor reportado es 0.8773. Contrastar con el resto de la columna (valores entre 20.41 y 49.30) y con la definición de DTW en Sección IV.C "Evaluation Metrics", párrafo 1.</span>

**<span style="color:#98c379">Dónde marcar:</span>** Tabla II, columna DTW. Encierra en rojo el valor **0.8773** de la fila RMVPE.

**<span style="color:#61afef">Comentario al margen:</span>**
> "Todos los DTW andan entre 20 y 50, menos este que da 0.87. O usaron una fórmula distinta solo para esta fila, o se equivocaron al copiar el número. Esto no es una diferencia pequeña, son dos órdenes de magnitud. Hay que revisarlo."

---

### <span style="color:#e06c75">13.</span> Todos los resultados son puntuales, sin margen de error

<span style="color:#c678dd">**Referencia para los autores:** Tabla II completa (las cuatro columnas: Avg. LCS, MRR, Top-5, DTW). Ningún valor va acompañado de desviación estándar, intervalo de confianza ni resultado de test estadístico. La Sección IV.C describe las métricas pero nunca menciona variabilidad. La Sección IV.D interpreta el ranking entre métodos sin ningún respaldo estadístico.</span>

**<span style="color:#98c379">Dónde marcar:</span>** Tabla II completa. Escribe "¿Y EL MARGEN DE ERROR?" al lado.

**<span style="color:#61afef">Comentario al margen:</span>**
> "Son 80 canciones, no 8000. Con tan pocos datos, la diferencia entre 7.12% y 9.83% puede ser puro azar. Sin barras de error o algún test estadístico no se puede decir que SPICE es mejor que FCN-f₀. Cualquier journal serio pide intervalos de confianza o al menos un test pareado."

---

### <span style="color:#e06c75">14.</span> Solo se comparan entre ellos, no contra nada que ya exista

<span style="color:#c678dd">**Referencia para los autores:** Tabla II (las 8 filas son todas variantes del método MC-MSA propuesto). Sección IV.D "Comparative Analysis" compara exclusivamente estas 8 variantes entre sí. No se incluye ningún sistema CSI estándar como baseline (chroma-based SSM, MFCC+DTW, coberturas tonales). La Sección IV.C describe las métricas de retrieval pero nunca se aplican a un método de referencia externo.</span>

**<span style="color:#98c379">Dónde marcar:</span>** Al pie de la Tabla II.

**<span style="color:#61afef">Comentario al margen:</span>**
> "La tabla compara 8 versiones del mismo método. Pero ¿qué tal si con un simple chroma + DTW obtienes mejor resultado? Sin al menos un baseline estándar, los porcentajes no significan nada. 9% de MRR puede ser malísimo o buenísimo y no hay forma de saberlo."

---

### <span style="color:#e06c75">15.</span> Lo de "homogeneización estructural" es una explicación inventada después de ver los datos

<span style="color:#c678dd">**Referencia para los autores:** Sección IV.E "Discussion and Error Propagation", párrafo 2, que comienza con *"Interestingly, the experimental data reveals a trade-off..."* y contiene la frase *"This suggests a phenomenon of structural homogenization"*. La comparación numérica citada proviene de la Tabla II: FCN-f₀ (Avg. LCS 84.94%) vs. SPICE (Avg. LCS 83.59%).</span>

**<span style="color:#98c379">Dónde marcar:</span>** Sección IV.E, el párrafo que empieza con *"Interestingly, the experimental data reveals..."*. Encierra la frase "structural homogenization".

**<span style="color:#61afef">Comentario al margen:</span>**
> "Esto es una explicación a posteriori, no un hallazgo. FCN-f₀ da 84.94% de LCS, SPICE da 83.59%. La diferencia es 1.35 puntos. Con 80 pares y sin barras de error, eso puede no ser nada. Y aunque fuera real, no midieron la entropía de las secuencias ni cuántas colisiones hay entre canciones distintas. Sin eso, no se puede afirmar que hay 'homogeneización'. Por ahora es solo una hipótesis."

---

# <span style="color:#e5c07b">Los que nadie más vio pero son igual de fuertes</span>

### <span style="color:#e06c75">6.</span> El algoritmo dice que siempre usa Demucs, pero la tabla lo trata como opcional

<span style="color:#c678dd">**Referencia para los autores:** Sección III.E, Algoritmo 1, línea 1 (`V ← SourceSeparation(X, Demucs)`). Contrastar con Tabla II, fila 4 ("CREPE") y fila 8 ("Demucs + CREPE"). El algoritmo ejecuta Demucs incondicionalmente, pero la tabla reporta configuraciones con y sin Demucs como si fueran distintas.</span>

**<span style="color:#98c379">Dónde marcar:</span>** Algoritmo 1, línea 1. Subráyala con doble línea. Traza flecha a Tabla II filas 4 y 8.

**<span style="color:#61afef">Comentario al margen:</span>**
> "El algoritmo dice que el primer paso SIEMPRE es separar las voces con Demucs. Pero luego en la Tabla II comparan CREPE solo (fila 4) contra CREPE con Demucs (fila 8) como si fueran cosas distintas. O el algoritmo está mal escrito, o la tabla está mal. Una de dos."

### <span style="color:#e06c75">11.</span> La justificación de δ habla de regresión lineal, pero la ecuación usa una integral

<span style="color:#c678dd">**Referencia para los autores:** Sección IV.B, ítem 3 (Boundary Analysis Window: `δ = 200 ms`), frase *"This window provides sufficient frames for a stable linear regression of the f₀ slope"*. Contrastar con Sección III.D, Ecuaciones (1) y (2), que computan `∫(df₀/dt)dt`, lo cual algebraicamente equivale a `f₀(t_end) − f₀(t_end − δ)`, no a una regresión lineal.</span>

**<span style="color:#98c379">Dónde marcar:</span>** Sección IV.B, ítem 3. Traza flecha hacia Ecuaciones (1) y (2).

**<span style="color:#61afef">Comentario al margen:</span>**
> "Aquí dicen que 200ms da para hacer una regresión lineal del f₀. Pero las ecuaciones (1) y (2) no hacen ninguna regresión: solo calculan la diferencia entre el f₀ al inicio y al final de la ventana. ¿Qué hicieron en realidad? Porque la justificación y la fórmula no dicen lo mismo."
