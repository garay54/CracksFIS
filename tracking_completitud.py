"""
Módulo de seguimiento temporal de grietas con detección de inicio/fin.
Determina si una grieta está completa o truncada en los bordes del frame.
"""
import os
import re
import cv2
import numpy as np
from ultralytics import YOLO
import sys
import csv
from collections import defaultdict

# SORT tracker
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, 'libs'))
from sort import Sort

# --- CONFIGURACIÓN ---
DEFAULT_MODEL_PATH = os.path.join(SCRIPT_DIR, "best.pt")
DEFAULT_MIN_CONF = 0.35
DEFAULT_MAX_AGE = 10
DEFAULT_IOU_THRESH = 0.2
DEFAULT_MIN_HITS = 2
BORDE_MARGEN = 15  # píxeles desde el borde para considerar "toca borde"


class CrackTrackAnalyzer:
    """
    Analizador de tracks de grietas con detección de completitud.
    """
    def __init__(self, img_height, img_width, borde_margen=BORDE_MARGEN):
        self.img_h = img_height
        self.img_w = img_width
        self.margen = borde_margen
        
        # Almacenamiento por track_id
        self.track_history = defaultdict(lambda: {
            'bboxes': [],
            'frames': [],
            'longitudes': [],
            'anchos_prom': [],
            'anchos_max': [],
            'toca_borde_superior': False,
            'toca_borde_inferior': False,
            'primer_frame': None,
            'ultimo_frame': None,
            'estado': 'ACTIVO'
        })
    
    def bbox_toca_borde(self, bbox, lado='cualquiera'):
        """
        Determina si un bbox toca algún borde de la imagen.
        
        Args:
            bbox: (x1, y1, x2, y2)
            lado: 'superior', 'inferior', 'izquierdo', 'derecho', 'cualquiera'
        
        Returns:
            bool
        """
        x1, y1, x2, y2 = bbox
        m = self.margen
        
        if lado == 'superior':
            return y1 < m
        elif lado == 'inferior':
            return y2 > (self.img_h - m)
        elif lado == 'izquierdo':
            return x1 < m
        elif lado == 'derecho':
            return x2 > (self.img_w - m)
        else:  # cualquiera
            return (y1 < m or y2 > (self.img_h - m) or 
                    x1 < m or x2 > (self.img_w - m))
    
    def actualizar_track(self, track_id, bbox, frame_num, longitud=None, 
                        ancho_prom=None, ancho_max=None):
        """
        Actualiza información de un track.
        """
        tid = int(track_id)
        hist = self.track_history[tid]
        
        # Primera vez que vemos este track
        if hist['primer_frame'] is None:
            hist['primer_frame'] = frame_num
            if self.bbox_toca_borde(bbox, 'superior'):
                hist['toca_borde_superior'] = True
        
        # Actualizar última observación
        hist['ultimo_frame'] = frame_num
        hist['bboxes'].append(bbox)
        hist['frames'].append(frame_num)
        
        if longitud is not None:
            hist['longitudes'].append(longitud)
        if ancho_prom is not None:
            hist['anchos_prom'].append(ancho_prom)
        if ancho_max is not None:
            hist['anchos_max'].append(ancho_max)
        
        # Verificar si toca borde inferior en esta observación
        if self.bbox_toca_borde(bbox, 'inferior'):
            hist['toca_borde_inferior'] = True
    
    def finalizar_track(self, track_id):
        """
        Marca un track como finalizado y determina su estado de completitud.
        """
        tid = int(track_id)
        hist = self.track_history[tid]
        
        if len(hist['bboxes']) == 0:
            hist['estado'] = 'INVALIDO'
            return
        
        ultima_bbox = hist['bboxes'][-1]
        
        # Determinar estado de completitud
        inicio_capturado = not hist['toca_borde_superior']
        fin_capturado = not self.bbox_toca_borde(ultima_bbox, 'inferior')
        
        if inicio_capturado and fin_capturado:
            hist['estado'] = 'COMPLETA'
        elif not inicio_capturado and not fin_capturado:
            hist['estado'] = 'TRUNCADA_AMBOS_LADOS'
        elif not inicio_capturado:
            hist['estado'] = 'TRUNCADA_INICIO'
        else:  # not fin_capturado
            hist['estado'] = 'TRUNCADA_FIN'
    
    def obtener_metricas_track(self, track_id):
        """
        Calcula métricas agregadas de un track.
        """
        tid = int(track_id)
        hist = self.track_history[tid]
        
        if len(hist['frames']) == 0:
            return None
        
        return {
            'track_id': tid,
            'estado': hist['estado'],
            'frames_activos': len(hist['frames']),
            'primer_frame': hist['primer_frame'],
            'ultimo_frame': hist['ultimo_frame'],
            'longitud_total_px': sum(hist['longitudes']) if hist['longitudes'] else 0,
            'longitud_promedio_px': np.mean(hist['longitudes']) if hist['longitudes'] else 0,
            'ancho_promedio_px': np.mean(hist['anchos_prom']) if hist['anchos_prom'] else 0,
            'ancho_maximo_px': max(hist['anchos_max']) if hist['anchos_max'] else 0,
            'toca_borde_superior': hist['toca_borde_superior'],
            'toca_borde_inferior': hist['toca_borde_inferior']
        }
    
    def obtener_todos_tracks_finalizados(self):
        """
        Retorna métricas de todos los tracks finalizados.
        """
        tracks_finalizados = []
        for tid in self.track_history.keys():
            if self.track_history[tid]['estado'] != 'ACTIVO':
                metricas = self.obtener_metricas_track(tid)
                if metricas:
                    tracks_finalizados.append(metricas)
        return tracks_finalizados


def obtener_carpeta_salida_tracking(base_dir=None, base="resultados_tracking"):
    """Genera carpeta única para resultados."""
    if base_dir is None:
        base_dir = SCRIPT_DIR
    
    existing = [d for d in os.listdir(base_dir) 
                if os.path.isdir(os.path.join(base_dir, d))]
    pattern = re.compile(rf"^{base}_(\d+)$")
    nums = [int(m.group(1)) for d in existing if (m := pattern.match(d))]
    next_idx = max(nums) + 1 if nums else 1
    out_dir = os.path.join(base_dir, f"{base}_{next_idx}")
    os.makedirs(out_dir, exist_ok=True)
    return out_dir


def detectar_y_preparar_detecciones(model, img, min_conf=DEFAULT_MIN_CONF):
    """Detecta grietas y prepara formato para SORT."""
    results = model(img, verbose=False)[0]
    dets_list = []
    
    if results.boxes is not None:
        for *xyxy, conf, cls in results.boxes.data.cpu().numpy():
            if conf < min_conf:
                continue
            x1, y1, x2, y2 = map(int, xyxy)
            dets_list.append([x1, y1, x2, y2, conf])
    
    if len(dets_list) == 0:
        return np.empty((0, 5), dtype=float)
    
    return np.array(dets_list, dtype=float).reshape(-1, 5)


def calcular_longitud_esqueleto(mask):
    """
    Calcula longitud aproximada del esqueleto de la máscara.
    """
    from skimage.morphology import skeletonize
    
    if mask is None or not np.any(mask):
        return 0
    
    binary_mask = (mask > 0).astype(np.uint8)
    skeleton = skeletonize(binary_mask)
    longitud_px = np.sum(skeleton)
    
    return float(longitud_px)


def dibujar_tracks_con_estado(img, tracks, analyzer, frame_num):
    """
    Dibuja tracks con información de estado de completitud.
    """
    draw = img.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.5
    thickness = 2
    
    for track in tracks:
        if len(track) < 5:
            continue
        x1, y1, x2, y2, tid = track[:5]
        x1, y1, x2, y2, tid = int(x1), int(y1), int(x2), int(y2), int(tid)
        
        # Color según si toca bordes
        bbox = (x1, y1, x2, y2)
        toca_superior = analyzer.bbox_toca_borde(bbox, 'superior')
        toca_inferior = analyzer.bbox_toca_borde(bbox, 'inferior')
        
        if toca_superior or toca_inferior:
            color = (0, 165, 255)  # Naranja: grieta truncada
        else:
            color = (0, 255, 0)  # Verde: potencialmente completa
        
        # Dibujar bbox
        cv2.rectangle(draw, (x1, y1), (x2, y2), color, 2)
        
        # Texto con ID y estado
        texto = f"ID{tid}"
        if toca_superior:
            texto += " ^"
        if toca_inferior:
            texto += " v"
        
        (tw, th), _ = cv2.getTextSize(texto, font, scale, thickness)
        # Centrar el texto en el bbox
        tx = x1 + (x2 - x1) // 2 - tw // 2
        ty = y1 + (y2 - y1) // 2 + th // 2
        
        # Opcional: fondo semitransparente o sólido para legibilidad
        cv2.rectangle(draw, (tx - 2, ty - th - 2), 
                     (tx + tw + 2, ty + 2), color, -1)
        cv2.putText(draw, texto, (tx, ty), font, scale, (0, 0, 0), thickness)
    
    return draw


def trackear_grietas_con_analisis_completitud(
    carpeta_entrada,
    carpeta_salida=None,
    modelo_path=None,
    min_conf=DEFAULT_MIN_CONF,
    max_age=DEFAULT_MAX_AGE,
    iou_thresh=DEFAULT_IOU_THRESH,
    min_hits=DEFAULT_MIN_HITS,
    borde_margen=BORDE_MARGEN,
    guardar_todos=False,
    calcular_metricas_geometricas=False
):
    """
    Realiza tracking con análisis de completitud de grietas.
    
    Args:
        carpeta_entrada: Carpeta con imágenes secuenciales
        carpeta_salida: Carpeta de resultados (None = auto)
        modelo_path: Ruta al modelo YOLO
        min_conf: Umbral de confianza
        max_age: Frames para mantener track sin detección
        iou_thresh: Umbral IoU para SORT
        min_hits: Detecciones mínimas para confirmar track
        borde_margen: Píxeles de margen para detectar bordes
        guardar_todos: Guardar frames sin grietas
        calcular_metricas_geometricas: Calcular longitud/ancho (más lento)
    
    Returns:
        (carpeta_salida, lista_metricas_tracks)
    """
    # Configuración
    if modelo_path is None:
        modelo_path = DEFAULT_MODEL_PATH
        if not os.path.exists(DEFAULT_MODEL_PATH):
            modelo_path = os.path.join(SCRIPT_DIR, "modelos", "best.pt")
    
    if not os.path.exists(modelo_path):
        raise FileNotFoundError(f"Modelo no encontrado: {modelo_path}")
    
    if not os.path.exists(carpeta_entrada):
        raise FileNotFoundError(f"Carpeta no encontrada: {carpeta_entrada}")
    
    if carpeta_salida is None:
        carpeta_salida = obtener_carpeta_salida_tracking()
    else:
        os.makedirs(carpeta_salida, exist_ok=True)
    
    print(f"📁 Entrada: {carpeta_entrada}")
    print(f"💾 Salida: {carpeta_salida}")
    print(f"🤖 Modelo: {modelo_path}")
    
    # Cargar modelo
    modelo = YOLO(modelo_path)
    print("✅ Modelo YOLO cargado")
    
    # Inicializar tracker
    tracker = Sort(max_age=max_age, min_hits=min_hits, iou_threshold=iou_thresh)
    print(f"✅ SORT inicializado (max_age={max_age}, min_hits={min_hits}, iou={iou_thresh})")
    
    # Obtener imágenes
    imagenes = sorted([f for f in os.listdir(carpeta_entrada) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
    
    if len(imagenes) == 0:
        print("⚠️ No hay imágenes")
        return carpeta_salida, []
    
    # Leer primera imagen para obtener dimensiones
    img_sample = cv2.imread(os.path.join(carpeta_entrada, imagenes[0]))
    img_h, img_w = img_sample.shape[:2]
    
    # Inicializar analizador
    analyzer = CrackTrackAnalyzer(img_h, img_w, borde_margen)
    print(f"✅ Analizador inicializado (imagen: {img_w}x{img_h}, margen: {borde_margen}px)")
    
    # Variables de tracking
    tracks_activos = set()
    frames_procesados = 0
    frames_con_grietas = 0
    
    print(f"📸 Procesando {len(imagenes)} imágenes...\n")
    
    # Procesar frames
    for idx, nombre_imagen in enumerate(imagenes):
        ruta_imagen = os.path.join(carpeta_entrada, nombre_imagen)
        img = cv2.imread(ruta_imagen)
        
        if img is None:
            print(f"⚠️ Error leyendo: {nombre_imagen}")
            continue
        
        # Detectar
        dets = detectar_y_preparar_detecciones(modelo, img, min_conf)
        
        # Actualizar tracker
        if len(dets) > 0:
            tracks = tracker.update(dets)
        else:
            tracks = tracker.update(np.empty((0, 5)))
        
        # Procesar tracks detectados
        tracks_en_frame = set()
        for track in tracks:
            if len(track) < 5:
                continue
            
            x1, y1, x2, y2, tid = track[:5]
            tid = int(tid)
            tracks_en_frame.add(tid)
            bbox = (int(x1), int(y1), int(x2), int(y2))
            
            # Calcular métricas geométricas (opcional, más lento)
            longitud = None
            ancho_prom = None
            ancho_max = None
            
            if calcular_metricas_geometricas and results.masks is not None:
                # Aquí iría la lógica de calcular longitud/ancho del mask
                # (simplificado por brevedad)
                pass
            
            # Actualizar analyzer
            analyzer.actualizar_track(tid, bbox, idx, longitud, ancho_prom, ancho_max)
            
            # Registrar como activo
            if tid not in tracks_activos:
                tracks_activos.add(tid)
        
        # Detectar tracks que murieron
        tracks_muertos = tracks_activos - tracks_en_frame
        for tid in tracks_muertos:
            analyzer.finalizar_track(tid)
            print(f"   🏁 Track {tid} finalizado en frame {idx}")
        
        tracks_activos = tracks_en_frame
        
        # Visualizar
        img_anotada = dibujar_tracks_con_estado(img, tracks, analyzer, idx)
        
        # Guardar
        if len(tracks) > 0 or guardar_todos:
            nombre_salida = f"frame_{idx:06d}_{nombre_imagen}"
            ruta_salida = os.path.join(carpeta_salida, nombre_salida)
            cv2.imwrite(ruta_salida, img_anotada)
            
            if len(tracks) > 0:
                frames_con_grietas += 1
                print(f"✅ Frame {idx+1}/{len(imagenes)}: {len(tracks)} tracks activos")
        
        frames_procesados += 1
    
    # Finalizar tracks restantes
    for tid in tracks_activos:
        analyzer.finalizar_track(tid)
    
    # Obtener métricas finales
    metricas_tracks = analyzer.obtener_todos_tracks_finalizados()
    
    # Guardar reporte CSV
    csv_path = os.path.join(carpeta_salida, "reporte_completitud_tracks.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'track_id', 'estado', 'frames_activos', 'primer_frame', 'ultimo_frame',
            'longitud_total_px', 'longitud_promedio_px', 'ancho_promedio_px', 
            'ancho_maximo_px', 'toca_borde_superior', 'toca_borde_inferior'
        ])
        writer.writeheader()
        writer.writerows(metricas_tracks)
    
    print(f"\n✅ Tracking completado:")
    print(f"   - Frames procesados: {frames_procesados}")
    print(f"   - Frames con grietas: {frames_con_grietas}")
    print(f"   - Tracks detectados: {len(metricas_tracks)}")
    print(f"   - Reporte CSV: {csv_path}")
    
    # Resumen por estado
    estados = defaultdict(int)
    for m in metricas_tracks:
        estados[m['estado']] += 1
    
    print(f"\n📊 Resumen de completitud:")
    for estado, count in estados.items():
        print(f"   - {estado}: {count}")
    
    return carpeta_salida, metricas_tracks


# ============================================
# FUNCIÓN DE PRUEBA GENÉRICA
# ============================================

def crear_video_sintetico_prueba(carpeta_salida="test_video_sintetico", 
                                  num_frames=50, ancho=640, alto=480):
    """
    Crea un video sintético con grietas que aparecen/desaparecen en bordes.
    
    Útil para testing sin datos reales.
    """
    os.makedirs(carpeta_salida, exist_ok=True)
    
    print(f"🎬 Generando video sintético en: {carpeta_salida}")
    
    for i in range(num_frames):
        img = np.ones((alto, ancho, 3), dtype=np.uint8) * 200  # fondo gris claro
        
        # Grieta 1: entra desde arriba, sale por abajo (TRUNCADA_AMBOS_LADOS)
        if i < 30:
            y_start = max(0, -100 + i * 20)
            y_end = min(alto, 200 + i * 20)
            cv2.line(img, (100, y_start), (100, y_end), (50, 50, 50), 3)
        
        # Grieta 2: empieza dentro, sale por abajo (TRUNCADA_FIN)
        if 10 < i < 40:
            y_start = 150
            y_end = min(alto, 150 + (i - 10) * 15)
            cv2.line(img, (300, y_start), (310, y_end), (30, 30, 30), 2)
        
        # Grieta 3: completa (COMPLETA)
        if 20 < i < 35:
            cv2.line(img, (500, 150), (520, 300), (40, 40, 40), 2)
        
        # Guardar
        cv2.imwrite(os.path.join(carpeta_salida, f"frame_{i:04d}.png"), img)
    
    print(f"✅ {num_frames} frames generados")
    return carpeta_salida


if __name__ == "__main__":
    # Prueba 1: Video sintético
    print("=== PRUEBA 1: VIDEO SINTÉTICO ===\n")
    carpeta_test = crear_video_sintetico_prueba()
    
    # Nota: Esto fallará sin modelo YOLO, es solo para mostrar uso
    # trackear_grietas_con_analisis_completitud(carpeta_test)
    
    print("\n=== PRUEBA 2: TUS DATOS REALES ===")
    print("Uso:")
    print("  carpeta, metricas = trackear_grietas_con_analisis_completitud(")
    print("      'ruta/a/tus/frames',")
    print("      modelo_path='best.pt'")
    print("  )")




    #COMPARAR CUANTAS TENEMOS REALES Y CUANTAS SE HIZO EL SEGUIMIENTO CON EL SCRIPT

    #COMPARAR QUE LAS QUE SE DETECTARON CUANTAS PUDE SEGUIR

    # CUANTAS SE DETECTARON DE INICIO A FIN