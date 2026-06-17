# CracksFIS

## Portfolio summary / Resumen de portafolio

CracksFIS is an applied AI project for evaluating structural cracks with fuzzy logic. It combines computer vision outputs and interpretable fuzzy inference rules to estimate crack condition from width, length, completeness, and density.

CracksFIS es un proyecto de IA aplicada para evaluar grietas estructurales mediante logica difusa. Integra salidas de vision por computadora y reglas interpretables de inferencia difusa para estimar la condicion de una grieta a partir de anchura, longitud, completitud y densidad.

**Technologies / Tecnologias:** Python, fuzzy inference systems, computer vision, data visualization.

**Project status / Estado:** Active research/prototype repository for crack evaluation and thesis-related experimentation.

**Next steps / Proximos pasos:** consolidate the current FIS version, separate generated artifacts from source code, and add a reproducible evaluation workflow.

---

Sistema de logica difusa para evaluar grietas en pavimentos mediante una arquitectura jerarquica:

- FIS 1: `W, L -> SD`
- FIS 2: `D, C -> SE`
- FIS 3: `SD, SE -> SF`

El repositorio incluye el motor FIS, figuras para tesis, reportes auxiliares y un dashboard local para explorar funciones de membresia, reglas y superficies de respuesta.

## Dashboard

Desde esta carpeta:

```powershell
python -m http.server 8787 --bind 127.0.0.1 -d dashboard
```

Luego abrir:

```text
http://127.0.0.1:8787
```

## Archivos principales

- `fis_grietas_v2.py`: implementacion vigente del sistema difuso jerarquico.
- `dashboard/`: interfaz interactiva para evaluar casos, editar membresias y visualizar superficies.
- `figuras_tesis/`: figuras exportadas para documentacion metodologica.
- `tracking_completitud.py`: calculo auxiliar de completitud de observacion.
