# CracksFIS

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
