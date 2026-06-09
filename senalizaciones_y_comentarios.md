# <span style="color:#e06c75">Guía de Señalizaciones Físicas</span> + <span style="color:#61afef">Comentarios para los Autores</span>

**<span style="color:#c678dd">Instrucciones:</span>** Imprime el artículo. Cada entrada indica **dónde** marcar, **qué** encerrar/subrayar, y el **comentario exacto** que debes escribir a mano en el margen. Al final, la lista de comentarios formales que enviarás a los autores.

---

# <span style="color:#e5c07b">🖊️ SEÑALIZACIONES FÍSICAS</span> <span style="color:#98c379">(para escribir a mano sobre el papel)</span>

---

### <span style="color:#e06c75">1.</span> Abstract — última frase

<span style="color:#98c379">**Dónde:**</span> Última oración del Abstract, la que dice *"antecedent-consequent recognition shows promise as a structural fingerprint for musical audio"*.

<span style="color:#98c379">**Acción:**</span> Subráyala completamente.

<span style="color:#61afef">**Comentario al margen:**</span>
> "El mejor MRR es 9.83% y el mejor Top-5 es 15%. Con Top-5 de 15%, el 85% de las queries falla. La afirmación 'shows promise as a fingerprint' está inflada respecto a la magnitud real. Reformular como prueba de concepto o bajar el tono de la conclusión."

---

### <span style="color:#e06c75">2.</span> Sección III.A — lista de los 8 extractores

<span style="color:#98c379">**Dónde:**</span> El listado numerado 1) al 8) de los extractores.

<span style="color:#98c379">**Acción:**</span> Encierra en un rectángulo los ítems 1 (pYIN), 6 (FCN-$f_0$) y 7 (pYIN+CREPE).

<span style="color:#61afef">**Comentario al margen:**</span>
> "Los extractores comparados fueron diseñados para tareas distintas (monofónicos, polifónicos, habla — FCN-$f_0$ [ref. 10] fue entrenado para speech, no para canto polifónico). ¿Se normalizó por dominio de entrenamiento? Si no, ¿cómo se justifica el ranking de la Tabla II?"

---

### <span style="color:#e06c75">3.</span> Sección III.B — cómputo del SSM

<span style="color:#98c379">**Dónde:**</span> La frase *"Euclidean distance between downsampled feature vectors combining pitch (converted to MIDI scale) and normalized Root Mean Square (RMS) energy"*.

<span style="color:#98c379">**Acción:**</span> Encierra en un círculo "MIDI scale" y "RMS energy".

<span style="color:#61afef">**Comentario al margen:**</span>
> "Pitch en MIDI (rango ~24–96) vs. RMS normalizada (rango 0–1). Sin normalización por componente, la distancia euclidiana está dominada por pitch en dos órdenes de magnitud. La energía es matemáticamente irrelevante en el SSM. ¿Qué ponderación o normalización (z-score, min-max) se aplicó? Debe explicitarse, porque condiciona toda la detección de fronteras."

---

### <span style="color:#e06c75">4.</span> Sección III.D — Ecuaciones (1) y (2) <span style="color:#c678dd">⚠️ BUG LÓGICO</span>

<span style="color:#98c379">**Dónde:**</span> Las dos ecuaciones completas. Encierra los operadores **∨** (el "o" lógico) en ambas.

<span style="color:#98c379">**Acción:**</span> Encierra con rojo ambos símbolos ∨ en la Ecuación (1) y en la Ecuación (2).

<span style="color:#61afef">**Comentario al margen:**</span>
> <span style="color:#e06c75">**¡Inconsistencia lógica!**</span> Un segmento con pitch ascendente en la ventana terminal (∫df₀/dt > ε) Y energía baja (Ē < τₑ) satisface simultáneamente la condición de A (por el primer disyunto de la Ec. 1) y la de C (por el segundo disyunto de la Ec. 2). Las condiciones NO son mutuamente excluyentes. El paper no define regla de precedencia ni en III.D ni en el Algoritmo 1. La salida del clasificador queda INDEFINIDA para un subconjunto no trivial de entradas. CORREGIR: especificar precedencia explícita, o reescribir las condiciones como conjunciones disjuntas."

---

### <span style="color:#e06c75">5.</span> Sección III.D — Ecuación (1), parámetro ε

<span style="color:#98c379">**Dónde:**</span> El símbolo $\epsilon$ en la Ecuación (1).

<span style="color:#98c379">**Acción:**</span> Enciérralo en un círculo y traza una flecha hacia la Tabla I (página siguiente), donde aparece *"Pitch Slope Threshold ε = 0.15"*.

<span style="color:#61afef">**Comentario al margen:**</span>
> "¿Unidades de ε? La integral ∫(df₀/dt)dt: ¿se evalúa en MIDI·s? ¿En semitonos acumulados? ¿En Hz·s? El valor 0.15 no es interpretable ni replicable sin unidades. Mismo problema con la magnitud que compara la integral."

---

### <span style="color:#e06c75">6.</span> Sección III.E — Algoritmo 1, línea 1 <span style="color:#c678dd">⚠️ CONTRADICCIÓN INTERNA</span>

<span style="color:#98c379">**Dónde:**</span> Línea 1 del pseudocódigo: *"V ← SourceSeparation(X, Demucs)"*.

<span style="color:#98c379">**Acción:**</span> Subráyala con doble línea y escribe "CONTRADICCIÓN" al lado. Traza una flecha hacia la Tabla II (filas 4 "CREPE" y 8 "Demucs+CREPE").

<span style="color:#61afef">**Comentario al margen:**</span>
> <span style="color:#e06c75">**¡Contradicción interna!**</span> La línea 1 aplica Demucs INCONDICIONALMENTE a toda entrada X, antes de cualquier ramificación por Eₜᵧₚₑ. Pero la Tabla II reporta 'CREPE' (fila 4) y 'Demucs + CREPE' (fila 8) como configuraciones distintas. Si Demucs se aplica siempre, las filas 4 y 8 miden lo mismo y una sobra. Si no se aplica siempre, el Algoritmo 1 está mal escrito. Aclarar y corregir consistentemente."

---

### <span style="color:#e06c75">7.</span> Sección III.E — Algoritmo 1, línea 6 y Tabla I

<span style="color:#98c379">**Dónde:**</span> Línea 6 del pseudocódigo: *"if prob(si) < τvoicing then Sfunc[i] ← X"*. En la Tabla I, fila *"Voicing Threshold | τvoicing | 0.5"*.

<span style="color:#98c379">**Acción:**</span> Encierra ambas ocurrencias de τvoicing (0.5) y únelas con una flecha.

<span style="color:#61afef">**Comentario al margen:**</span>
> "Se aplica UN único umbral de voicing (0.5) a las salidas de 8 extractores distintos. Estos extractores NO producen confianzas calibradas en la misma escala: unos usan probabilidades de modelo (CREPE), otros flags derivados (pYIN), otros scores no calibrados. El umbral universal sesga la asignación a la clase X de forma sistemáticamente distinta por extractor, confundiendo la comparación de la Tabla II. ¿Por qué no un umbral por extractor calibrado en validación?"

---

### <span style="color:#e06c75">8.</span> Sección III.E — Algoritmo 1 completo

<span style="color:#98c379">**Dónde:**</span> El bloque completo del Algoritmo 1 (líneas 1 a 12).

<span style="color:#98c379">**Acción:**</span> Traza un corchete vertical que abarque las líneas 1→4→5→9 y escribe "PIPELINE SECUENCIAL SIN CORRECCIÓN" al lado.

<span style="color:#61afef">**Comentario al margen:**</span>
> "El pipeline es estrictamente secuencial: separación → extracción de f₀ → SSM → fronteras → clasificación. La Sección IV.E reconoce errores en cascada, pero solo cualitativamente. Se requiere ablación por etapa que aísle dónde se origina la degradación de retrieval: ¿en la separación? ¿en la extracción de f₀? ¿en el SSM? ¿en el clasificador? Sin esa descomposición no es posible interpretar las diferencias entre extractores en la Tabla II."

---

### <span style="color:#e06c75">9.</span> Sección IV.A — tamaño del dataset

<span style="color:#98c379">**Dónde:**</span> La frase *"a curated corpus of 80 pairs of musical works (160 tracks in total)"*.

<span style="color:#98c379">**Acción:**</span> Enciérrala en un rectángulo y escribe "n=80" al margen.

<span style="color:#61afef">**Comentario al margen:**</span>
> "Con n=80 pares, diferencias de 1–3 puntos de MRR en la Tabla II son probablemente indistinguibles del ruido muestral. Además, el diseño original→acústico fija la dirección de la variación tímbrica y no cubre casos reales de CSI (cambios de tonalidad, reordenamientos estructurales, covers instrumentales). Las conclusiones sobre 'invariancia estructural' deben acotarse a este escenario específico, o ampliarse a Covers80/Da-Tacos como los propios autores mencionan en Future Work."

---

### <span style="color:#e06c75">10.</span> Sección IV.B — justificación de hiperparámetros

<span style="color:#98c379">**Dónde:**</span> Los tres ítems numerados 1)–3) que justifican los hiperparámetros. Encierra la palabra *"optimal"* en el ítem 2.

<span style="color:#61afef">**Comentario al margen:**</span>
> "La palabra 'optimal' implica selección sobre los datos. No se reporta partición train/dev/test ni held-out. Si los umbrales ε, τₑ, δ se ajustaron sobre los mismos 80 pares de la Tabla II, los resultados están inflados por construcción. Pido: (a) explicitar el procedimiento de tuning, y (b) si no hubo held-out, repartir el corpus y rehacer, o reportar superficie de sensibilidad (MRR vs ε, τₑ) que muestre estabilidad."

---

### <span style="color:#e06c75">11.</span> Sección IV.B — ítem 3, justificación de δ <span style="color:#c678dd">⚠️ ERROR FACTUAL</span>

<span style="color:#98c379">**Dónde:**</span> La frase *"This window provides sufficient frames for a stable linear regression of the f₀ slope"* en el ítem 3 de la justificación de hiperparámetros. Traza una flecha hacia las Ecuaciones (1) y (2).

<span style="color:#61afef">**Comentario al margen:**</span>
> "¿Regresión lineal o integral? La justificación dice 'linear regression', pero las Ecs. (1) y (2) usan ∫(df₀/dt)dt, que algebraicamente se reduce a f₀(t_end) − f₀(t_end − δ) y NO es una regresión. Si se implementó regresión, las ecuaciones deben reescribirse. Si se implementó la integral, la justificación del ítem 3 no aplica y debe corregirse. Aclarar la operación real."

---

### <span style="color:#e06c75">12.</span> Tabla II — columna DTW, valor RMVPE

<span style="color:#98c379">**Dónde:**</span> Columna DTW de la Tabla II. Encierra en rojo el valor **0.8773** en la fila de RMVPE.

<span style="color:#61afef">**Comentario al margen:**</span>
> "Valores de DTW abarcan DOS ÓRDENES DE MAGNITUD: RMVPE = 0.8773 vs. resto = 20.41–49.30. No se especifica si DTW se reporta como distancia o similitud, ni normalización, ni unidades. El valor 0.8773 sugiere o bien normalización distinta solo en esa fila, o error de transcripción. Aclarar definición operacional y verificar el valor."

---

### <span style="color:#e06c75">13.</span> Tabla II — toda la tabla

<span style="color:#98c379">**Dónde:**</span> La Tabla II completa. Traza un rectángulo alrededor de toda la tabla y márcala con "FALTAN IC".

<span style="color:#61afef">**Comentario al margen:**</span>
> "Toda la tabla reporta valores puntuales: sin intervalos de confianza, sin desviación estándar, sin tests pareados entre filas. Con n=80 y diferencias de pocos puntos entre métodos, la mayoría del ranking podría ser estadísticamente indistinguible. Reportar bootstrap CI al 95% sobre MRR y Top-5, y tests pareados (bootstrap pareado o Wilcoxon) entre al menos los métodos top. Sin esto, 'SPICE > FCN-f₀' no es defendible."

---

### <span style="color:#e06c75">14.</span> Tabla II — ausencia de baseline externo

<span style="color:#98c379">**Dónde:**</span> Tabla II. Escribe al pie de la tabla (o en el margen inferior):

<span style="color:#61afef">**Comentario al margen:**</span>
> "La tabla compara 8 variantes del método propuesto ENTRE SÍ, pero no contra ningún sistema CSI estándar de referencia. Sin al menos un baseline externo (e.g., chroma-based SSM, coberturas tonales) sobre los mismos 80 pares, los valores absolutos de MRR y Top-5 no son contextualizables. Incluir baseline externo bajo el mismo protocolo."

---

### <span style="color:#e06c75">15.</span> Sección IV.E — hipótesis de "structural homogenization"

<span style="color:#98c379">**Dónde:**</span> El párrafo que comienza con *"This suggests a phenomenon of structural homogenization..."* y el párrafo siguiente. Encierra la frase "structural homogenization".

<span style="color:#61afef">**Comentario al margen:**</span>
> "Hipótesis post-hoc no falsable con los datos presentados. No se reporta: entropía de secuencias generadas, tasa de colisión inter-pista, distribución de similitudes entre pares NO coincidentes. La diferencia clave (Avg. LCS 84.94% FCN-f₀ vs. 83.59% SPICE) es 1.35 puntos porcentuales sobre n=80. Sin intervalos de confianza, esa diferencia podría ser RUIDO (ver comentario Tabla II). Soportar con métricas adicionales o atenuar la afirmación a 'hipótesis a verificar en trabajo futuro'."

---

### <span style="color:#e06c75">16.</span> Sección V — Conclusiones, claim de invariancia

<span style="color:#98c379">**Dónde:**</span> La frase *"while style, tempo, and instrumentation may change drastically in a cover version, the underlying functional logic of the melody often remains invariant"*.

<span style="color:#98c379">**Acción:**</span> Subráyala completamente.

<span style="color:#61afef">**Comentario al margen:**</span>
> "Claim de invariancia general extraído de un experimento con variación tímbrica UNIDIRECCIONAL (original producido → cover acústico) donde el mejor sistema recupera correctamente en Top-5 solo el 15% de los casos. Acotar la conclusión al escenario evaluado, o presentar evidencia adicional sobre transposición, cambio de género, covers instrumentales."

---

# <span style="color:#e5c07b">📋 COMENTARIOS FORMALES</span> <span style="color:#98c379">(para enviar a los autores)</span>

<span style="color:#98c379">Copia y pega esta sección en el formato de revisión de la revista/conferencia.</span>

---

### <span style="color:#e06c75">Comentario 1</span> — Abstract inflado

> El abstract afirma que *"antecedent-consequent recognition shows promise as a structural fingerprint for musical audio"*, pero el mejor MRR reportado en la Tabla II es 9.83% y el mejor Top-5 es 15%. Con un Top-5 de 15%, el 85% de las queries falla en recuperar la coincidencia en las primeras cinco posiciones. Solicito reformular el abstract para que la afirmación cualitativa sea consistente con la magnitud cuantitativa, o presentar el sistema explícitamente como prueba de concepto preliminar.

---

### <span style="color:#e06c75">Comentario 2</span> — Heterogeneidad de extractores <span style="color:#abb2bf">(Sección III.A)</span>

> Los ocho extractores comparados fueron diseñados para tareas distintas: algunos para audio monofónico, otros para melodía predominante en polifonía, y FCN-$f_0$ [ref. 10] específicamente para pitch estimation en señales de habla. Aplicarlos sobre audio musical polifónico sin controlar por estas diferencias de dominio compromete la validez de la comparación. Solicito aclarar si se realizó alguna normalización o calibración por dominio de entrenamiento. En caso contrario, justificar el ranking de la Tabla II bajo estas condiciones.

---

### <span style="color:#e06c75">Comentario 3</span> — Escala de características en el SSM <span style="color:#abb2bf">(Sección III.B)</span>

> Se combina pitch en escala MIDI (rango aproximado 24–96) con RMS normalizada (rango 0–1) en un único vector sobre el que se aplica distancia euclidiana. Sin normalización por componente (z-score o min-max), la distancia está dominada por pitch en aproximadamente dos órdenes de magnitud, haciendo que la contribución de la energía al SSM sea matemáticamente despreciable. Solicitamos explicitar qué ponderación o normalización se aplicó antes del cómputo de distancia, ya que esto condiciona toda la detección de fronteras estructurales.

---

### <span style="color:#e06c75">Comentario 4</span> — Condiciones de clasificación no mutuamente excluyentes <span style="color:#abb2bf">(Sección III.D, Ecuaciones 1 y 2)</span> <span style="color:#c678dd">⚠️ CRÍTICO</span>

> Tal como están definidas, las condiciones para Antecedente (Ec. 1) y Consecuente (Ec. 2) **no son mutuamente excluyentes**. Un segmento con pitch ascendente en la ventana terminal ($\int df_0/dt > \epsilon$) y simultáneamente energía baja ($\bar{E} < \tau_e$) satisface la condición de Antecedente por el primer disyunto de la Ecuación (1) y la de Consecuente por el segundo disyunto de la Ecuación (2). Ni la Sección III.D ni el Algoritmo 1 especifican regla de precedencia para este caso, dejando la salida del clasificador indefinida sobre un subconjunto no trivial de entradas. **Esto debe corregirse antes de cualquier interpretación de los resultados:** especificar precedencia explícita, reemplazar los operadores $\lor$ por una regla de decisión ponderada, o reescribir como conjunciones disjuntas.

---

### <span style="color:#e06c75">Comentario 5</span> — Unidades del umbral ε <span style="color:#abb2bf">(Sección III.D, Ecuación 1, Tabla I)</span>

> No se especifican las unidades de $\epsilon = 0.15$. Dado que pitch se convierte a escala MIDI (Sección III.B), es necesario aclarar si la integral $\int df_0/dt\,dt$ se evalúa en MIDI·s, en semitonos acumulados, en Hz·s, o en otra unidad. Sin esta información, el valor 0.15 no es interpretable ni el experimento replicable. Lo mismo aplica a la magnitud que se compara en la integral.

---

### <span style="color:#e06c75">Comentario 6</span> — Contradicción entre Algoritmo 1 y Tabla II <span style="color:#abb2bf">(Sección III.E, línea 1)</span> <span style="color:#c678dd">⚠️ CRÍTICO</span>

> La línea 1 del Algoritmo 1 aplica Demucs **incondicionalmente** a la entrada $X$: *$V \leftarrow \text{SourceSeparation}(X, \text{Demucs})$*. Sin embargo, la Tabla II presenta "CREPE" (fila 4) y "Demucs + CREPE" (fila 8) como configuraciones distintas. Existe una contradicción experimental: o bien Demucs se aplica siempre (y entonces las filas 4 y 8 miden lo mismo), o bien no se aplica siempre (y entonces el Algoritmo 1 está incorrectamente especificado). Solicitamos aclarar y corregir consistentemente.

---

### <span style="color:#e06c75">Comentario 7</span> — Umbral de voicing universal <span style="color:#abb2bf">(Sección III.E, Algoritmo 1, Tabla I)</span>

> Se aplica un único umbral $\tau_{voicing} = 0.5$ a las salidas de probabilidad de voicing de los ocho extractores. Sin embargo, estos extractores no producen valores de confianza calibrados en la misma escala ni con la misma semántica: algunos generan probabilidades bayesianas, otros scores de confianza no calibrados. Aplicar el mismo umbral a todos sesga la asignación de segmentos a la clase $X$ de forma sistemática y diferenciada por extractor, confundiendo la comparación de la Tabla II. Solicitamos justificar el uso de un umbral universal frente a umbrales por extractor calibrados en un conjunto de validación.

---

### <span style="color:#e06c75">Comentario 8</span> — Ausencia de ablación por etapa del pipeline <span style="color:#abb2bf">(Sección III.E)</span>

> El pipeline del Algoritmo 1 es estrictamente secuencial y la Sección IV.E reconoce explícitamente que los errores se propagan en cascada. Sin embargo, esta discusión es únicamente cualitativa. Para un trabajo de nivel Q1 se espera al menos un estudio de ablación que descomponga el pipeline por etapas —separación, extracción de $f_0$, segmentación SSM, clasificación por reglas— midiendo individualmente dónde se origina la degradación del retrieval. Sin esta descomposición, no es posible interpretar si las diferencias entre extractores en la Tabla II provienen de la calidad del pitch, de errores en la segmentación, o de fallas en el clasificador.

---

### <span style="color:#e06c75">Comentario 9</span> — Tamaño y representatividad del dataset <span style="color:#abb2bf">(Sección IV.A)</span>

> El corpus de 80 pares original→acústico impone dos limitaciones: (1) con $n=80$, diferencias de 1–3 puntos de MRR entre métodos son probablemente indistinguibles del ruido muestral; (2) el diseño fija la dirección de la variación tímbrica (producido→acústico) y no cubre casos reales de CSI como cambios de tonalidad, reordenamientos estructurales o covers instrumentales. Las conclusiones sobre invariancia estructural deben acotarse explícitamente al escenario evaluado, o ampliarse a benchmarks estándar como Covers80 o Da-Tacos que los propios autores mencionan en la Sección V.

---

### <span style="color:#e06c75">Comentario 10</span> — Sobreajuste de hiperparámetros <span style="color:#abb2bf">(Sección IV.B)</span>

> La Sección IV.B utiliza el término *"optimal"* para describir los valores de $\epsilon$, $\tau_e$ y $\delta$, lo cual implica selección sobre los datos. No se reporta partición train/dev/test ni conjunto held-out. Si estos umbrales se ajustaron sobre los mismos 80 pares utilizados en la Tabla II, los resultados de evaluación están inflados por construcción. Solicitamos: (a) explicitar el procedimiento de tuning, y (b) si no existió held-out, rehacer la evaluación con una partición adecuada, o alternativamente reportar una superficie de sensibilidad (MRR vs. $\epsilon$, $\tau_e$) que demuestre estabilidad de los resultados frente a la elección de hiperparámetros.

---

### <span style="color:#e06c75">Comentario 11</span> — Inconsistencia entre justificación e implementación de δ <span style="color:#abb2bf">(Sección IV.B, Ecuaciones 1-2)</span> <span style="color:#c678dd">⚠️ CRÍTICO</span>

> La justificación del ítem 3 de la Sección IV.B afirma que $\delta = 200$ ms proporciona *"sufficient frames for a stable linear regression of the $f_0$ slope"*. Sin embargo, las Ecuaciones (1) y (2) computan una integral $\int_{t_{end}-\delta}^{t_{end}} (df_0/dt)\, dt$, que algebraicamente se reduce a la diferencia $f_0(t_{end}) - f_0(t_{end}-\delta)$ y **no constituye una regresión lineal**. Solicitamos aclarar cuál es la operación efectivamente implementada y, en su caso, reescribir las ecuaciones o la justificación para que sean consistentes entre sí.

---

### <span style="color:#e06c75">Comentario 12</span> — Anomalía en la métrica DTW <span style="color:#abb2bf">(Tabla II)</span>

> La columna DTW de la Tabla II presenta valores que abarcan dos órdenes de magnitud entre extractores: RMVPE reporta 0.8773, mientras que el resto oscila entre 20.41 y 49.30. La Sección IV.C describe DTW como una métrica de alineación elástica sobre el contorno de $f_0$, pero no especifica si se reporta como distancia o como similitud, ni la normalización aplicada, ni las unidades. El valor anómalo de RMVPE sugiere o bien una normalización distinta solo en esa fila, o un error de transcripción. Solicitamos aclarar la definición operacional de DTW y verificar la consistencia de los valores reportados.

---

### <span style="color:#e06c75">Comentario 13</span> — Ausencia de intervalos de confianza <span style="color:#abb2bf">(Tabla II)</span> <span style="color:#c678dd">⚠️ CRÍTICO</span>

> Toda la Tabla II reporta estimaciones puntuales de rendimiento sin intervalos de confianza, sin desviación estándar y sin tests de significancia pareados entre filas. Con $n=80$ queries y diferencias de pocos puntos porcentuales entre la mayoría de los métodos, el ranking completo podría ser estadísticamente indistinguible. Solicitamos reportar intervalos de confianza bootstrap al 95% sobre MRR y Top-5, así como tests pareados (bootstrap pareado o Wilcoxon signed-rank) entre al menos los tres mejores métodos.

---

### <span style="color:#e06c75">Comentario 14</span> — Ausencia de baseline externo <span style="color:#abb2bf">(Tabla II, Sección IV)</span>

> La Tabla II compara exclusivamente variantes del método propuesto entre sí, sin incluir ningún sistema CSI de referencia estándar (e.g., coberturas basadas en chroma, MFCC con DTW). Sin al menos un baseline externo aplicado a los mismos 80 pares bajo el mismo protocolo experimental, los valores absolutos de MRR y Top-5 no son contextualizables y la magnitud real de la contribución no es evaluable. Solicitamos incluir al menos un baseline reproducible.

---

### <span style="color:#e06c75">Comentario 15</span> — Hipótesis de "homogeneización estructural" no verificada <span style="color:#abb2bf">(Sección IV.E)</span>

> La hipótesis de que FCN-$f_0$ produce *"structural homogenization"* se formula para explicar por qué tiene mayor LCS pero menor MRR que SPICE. Sin embargo, no es falsable con los datos presentados: no se reporta la entropía de las secuencias generadas, ni la tasa de colisión entre pares no coincidentes, ni la distribución de similitud entre pistas no emparejadas. Adicionalmente, la diferencia en Avg. LCS entre FCN-$f_0$ (84.94%) y SPICE (83.59%) es de solo 1.35 puntos porcentuales, magnitud que sin intervalos de confianza podría ser ruido muestral. Solicitamos: (a) soportar esta hipótesis con métricas adicionales (entropía, colisiones inter-pista), o (b) atenuar la afirmación presentándola como hipótesis a verificar en trabajo futuro.

---

### <span style="color:#e06c75">Comentario 16</span> — Claim de invariancia no respaldado <span style="color:#abb2bf">(Sección V)</span>

> La conclusión de que *"while style, tempo, and instrumentation may change drastically in a cover version, the underlying functional logic of the melody often remains invariant"* se extrae de un experimento con variación tímbrica unidireccional (original producido → cover acústico) y donde el mejor sistema acierta en Top-5 solo en el 15% de los casos. Estas condiciones no respaldan una afirmación general de invariancia estructural. Solicitamos acotar explícitamente la conclusión al escenario evaluado, o presentar evidencia experimental adicional sobre otros tipos de variación (transposición tonal, cambio de género, covers instrumentales).

---

# <span style="color:#e5c07b">📊 NOTAS TÁCTICAS</span>

| <span style="color:#c678dd">Prioridad</span> | <span style="color:#c678dd">Comentarios</span> | <span style="color:#c678dd">Tipo</span> |
|:---:|:---|:---|
| <span style="color:#e06c75">🔴 Máxima</span> | **#4, #6, #11** | Bugs objetivos — no admiten defensa |
| <span style="color:#e5c07b">🟡 Alta</span> | **#10, #13, #14** | Estándares metodológicos mínimos (ML/Q1) |
| <span style="color:#61afef">🔵 Media</span> | **#3, #5, #7, #12** | Solicitudes de aclaración técnica (sin musicología) |

<span style="color:#98c379">**Si necesitas recortar por límite de espacio, prioriza: #4 → #6 → #13 → #11 → #10 (en ese orden).**</span>
