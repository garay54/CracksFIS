import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
import skfuzzy as fuzz
import json
import os

class CrackHierarchicalFIS:
    def __init__(self, run_gui=True):
        # ============================================================
        # 1. UNIVERSOS DE DISCURSO
        # ============================================================
        
        # FIS 1 - Entradas dimensionales
        self.w_universe = np.linspace(0, 30, 301)      # Anchura W: 0-30 mm (calibración mm/px)
        self.l_universe = np.linspace(0, 2000, 401)    # Longitud L: 0-2000 mm (seguimiento SORT)
        
        # FIS 2 - Entradas de extensión
        self.d_universe = np.linspace(0, 1, 201)       # Densidad D: 0-1 (fracción de área afectada)
        self.c_universe = np.linspace(0, 1, 201)       # Completitud C: 0-1 (continuidad de grieta)
        
        # Salidas intermedias y final
        self.sd_universe = np.linspace(0, 100, 201)    # Severidad Dimensional
        self.se_universe = np.linspace(0, 100, 201)    # Severidad de Extensión
        self.sf_universe = np.linspace(0, 100, 201)    # Severidad Final
        
        # ============================================================
        # 2. PARÁMETROS DE FUNCIONES DE MEMBRESÍA
        # ============================================================
        # Calibrados inicialmente según el documento de referencia de la tesis
        self.params = {
            # FIS 1 - Variables dimensionales
            'W': {
                'pequeña': [0.0, 0.0, 1.0, 3.0],      # Fisuras finas / capilares (< 3 mm - Norma IMT 2023)
                'media': [2.0, 6.0, 19.0],            # Grietas medias (3 a 19 mm - Norma IMT 2023)
                'grande': [16.0, 22.0, 30.0, 30.0]    # Grietas anchas (> 19 mm - Norma IMT 2023)
            },
            'L': {
                'corta': [0.0, 0.0, 200.0, 500.0],
                'media': [400.0, 800.0, 1200.0],
                'larga': [1000.0, 1500.0, 2000.0, 2000.0]
            },
            
            # FIS 2 - Variables de extensión
            'D': {
                'baja': [0.0, 0.0, 0.08, 0.22],       # Baja densidad superficial
                'media': [0.12, 0.32, 0.55],
                'alta': [0.42, 0.68, 1.0, 1.0]
            },
            'C': {
                'truncada': [0.0, 0.0, 0.25, 0.55],   # Alta incertidumbre / grieta cortada
                'parcial': [0.25, 0.55, 0.85],
                'completa': [0.55, 0.8, 1.0, 1.0]     # Grieta que atraviesa el parche
            },
            
            # Salidas FIS 1 y FIS 2
            'SD': {
                'baja': [0, 0, 20, 45],
                'media': [25, 50, 75],
                'alta': [55, 80, 100, 100]
            },
            'SE': {
                'baja': [0, 0, 20, 45],
                'media': [25, 50, 75],
                'alta': [55, 80, 100, 100]
            },
            
            # Salida FIS 3 (Severidad Final)
            'SF': {
                'leve': [0, 0, 20, 40],
                'moderada': [25, 50, 75],
                'critica': [60, 80, 100, 100]
            }
        }
        
        self.run_gui = run_gui
        self.dragging_point = None
        self.active_ax = None
        self.ax_var_map = {}  # Mapeo de axes a variables
        
        if run_gui:
            # ============================================================
            # 3. CONFIGURACIÓN DE LA FIGURA
            # ============================================================
            self.fig = plt.figure(figsize=(18, 11))
            self.fig.canvas.manager.set_window_title('Sistema FIS Jerárquico - Evaluación de Grietas en Pavimentos')
            
            # Fila 1: FIS 1 - Severidad Dimensional (W, L, SD)
            self.ax_w = plt.subplot2grid((4, 4), (0, 0))
            self.ax_l = plt.subplot2grid((4, 4), (0, 1))
            self.ax_sd = plt.subplot2grid((4, 4), (0, 2))
            self.ax_surf1 = plt.subplot2grid((4, 4), (0, 3), projection='3d')
            
            # Fila 2: FIS 2 - Severidad de Extensión (D, C, SE)
            self.ax_d = plt.subplot2grid((4, 4), (1, 0))
            self.ax_c = plt.subplot2grid((4, 4), (1, 1))
            self.ax_se = plt.subplot2grid((4, 4), (1, 2))
            self.ax_surf2 = plt.subplot2grid((4, 4), (1, 3), projection='3d')
            
            # Fila 3: FIS 3 - Severidad Final (SD, SE, SF)
            self.ax_sd_in = plt.subplot2grid((4, 4), (2, 0))
            self.ax_se_in = plt.subplot2grid((4, 4), (2, 1))
            self.ax_sf = plt.subplot2grid((4, 4), (2, 2))
            self.ax_surf3 = plt.subplot2grid((4, 4), (2, 3), projection='3d')
            
            # Fila 4: Panel de control e informe de resultados
            self.ax_result = plt.subplot2grid((4, 4), (3, 0), colspan=4)
            self.ax_result.axis('off')
            
            plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.15, 
                              hspace=0.4, wspace=0.3)
            
            # ============================================================
            # 4. SLIDERS PARA VALORES DE ENTRADA
            # ============================================================
            # Sliders para FIS 1 (Dimensional)
            ax_slider_w = plt.axes([0.1, 0.08, 0.15, 0.02])
            self.slider_w = Slider(ax_slider_w, 'W: Ancho (mm)', 0, 30, valinit=6.0)
            
            ax_slider_l = plt.axes([0.1, 0.05, 0.15, 0.02])
            self.slider_l = Slider(ax_slider_l, 'L: Longitud (mm)', 0, 2000, valinit=600.0)
            
            # Sliders para FIS 2 (Extensión)
            ax_slider_d = plt.axes([0.4, 0.08, 0.15, 0.02])
            self.slider_d = Slider(ax_slider_d, 'D: Densidad', 0, 1.0, valinit=0.30)
            
            ax_slider_c = plt.axes([0.4, 0.05, 0.15, 0.02])
            self.slider_c = Slider(ax_slider_c, 'C: Completitud', 0, 1.0, valinit=0.8)
            
            # Botón de cálculo y guardado
            ax_btn_calc = plt.axes([0.70, 0.05, 0.11, 0.05])
            self.btn_calc = Button(ax_btn_calc, 'Calcular Severidad', color='#e74c3c', hovercolor='#c0392b')
            self.btn_calc.on_clicked(self.calculate_full_inference)
            
            ax_btn_save = plt.axes([0.82, 0.05, 0.11, 0.05])
            self.btn_save = Button(ax_btn_save, 'Guardar Registro', color='#3498db', hovercolor='#2980b9')
            self.btn_save.on_clicked(self.save_record)
            
            # Conectar sliders
            self.slider_w.on_changed(self.update_preview)
            self.slider_l.on_changed(self.update_preview)
            self.slider_d.on_changed(self.update_preview)
            self.slider_c.on_changed(self.update_preview)
            
            # Conectar eventos interactivos
            self.fig.canvas.mpl_connect('button_press_event', self.on_press)
            self.fig.canvas.mpl_connect('button_release_event', self.on_release)
            self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
            
            self.setup_plots()
            self.update_all_surfaces()
            self.calculate_full_inference(None)
            plt.show()

    def evaluate(self, w_val, l_val, d_val, c_val):
        """Ejecuta la inferencia difusa jerárquica programáticamente"""
        sd_res = self.infer_fis1(w_val, l_val)
        se_res = self.infer_fis2(d_val, c_val)
        sf_res = self.infer_fis3(sd_res, se_res)
        
        if sf_res < 35.0:
            nivel = "LEVE"
            rec = "MONITOREO PERIÓDICO / Sellado menor localizado en caso de desarrollo puntual."
        elif sf_res < 70.0:
            nivel = "MODERADA"
            rec = "SELLADO DE GRIETAS con asfalto modificado / Fresado superficial localizado."
        else:
            nivel = "CRÍTICA"
            rec = "REHABILITACIÓN ESTRUCTURAL / Reencarpetado asfáltico completo de la sección."
            
        return {
            "sd": sd_res,
            "se": se_res,
            "sf": sf_res,
            "nivel": nivel,
            "recomendacion": rec
        }

    
    # ================================================================
    # MÉTODOS DE MEMBRESÍA
    # ================================================================
    
    def get_mf(self, universe, params):
        """Genera función de membresía triangular, trapezoidal o gaussiana."""
        if isinstance(params, dict):
            if params.get('type') == 'gauss':
                center, sigma = params['p']
                return np.exp(-0.5 * ((universe - center) / sigma) ** 2)
            params = params['p']
        if len(params) == 3:
            return fuzz.trimf(universe, params)
        else:
            return fuzz.trapmf(universe, params)

    def smooth_aggregate(self, rule_outputs):
        """Implica por producto y agrega por suma probabilística para suavizar transiciones."""
        aggregated = np.zeros_like(rule_outputs[0][1])
        for strength, mf in rule_outputs:
            contribution = np.clip(strength * mf, 0.0, 1.0)
            aggregated = aggregated + contribution - aggregated * contribution
        return np.clip(aggregated, 0.0, 1.0)

    def consequent_center(self, params):
        if isinstance(params, dict):
            if params.get('type') == 'gauss':
                return float(params['p'][0])
            params = params['p']
        if len(params) == 3:
            return float(params[1])
        return float((params[1] + params[2]) / 2)

    def smooth_rule_centroid(self, weighted_rules):
        total = 0.0
        weighted = 0.0
        for strength, params in weighted_rules:
            if strength <= 0:
                continue
            total += strength
            weighted += strength * self.consequent_center(params)
        if total <= 1e-12:
            return 0.0
        return float(weighted / total)
    
    # ================================================================
    # FIS 1: SEVERIDAD DIMENSIONAL (W, L -> SD)
    # ================================================================
    
    def infer_fis1(self, w_val, l_val):
        p = self.params
        
        # Fuzzificación
        mf_w_p = self.get_mf(self.w_universe, p['W']['pequeña'])
        mf_w_m = self.get_mf(self.w_universe, p['W']['media'])
        mf_w_g = self.get_mf(self.w_universe, p['W']['grande'])
        
        mf_l_c = self.get_mf(self.l_universe, p['L']['corta'])
        mf_l_m = self.get_mf(self.l_universe, p['L']['media'])
        mf_l_l = self.get_mf(self.l_universe, p['L']['larga'])
        
        mu_w_p = fuzz.interp_membership(self.w_universe, mf_w_p, w_val)
        mu_w_m = fuzz.interp_membership(self.w_universe, mf_w_m, w_val)
        mu_w_g = fuzz.interp_membership(self.w_universe, mf_w_g, w_val)
        
        mu_l_c = fuzz.interp_membership(self.l_universe, mf_l_c, l_val)
        mu_l_m = fuzz.interp_membership(self.l_universe, mf_l_m, l_val)
        mu_l_l = fuzz.interp_membership(self.l_universe, mf_l_l, l_val)
        
        # Salida
        mf_sd_b = self.get_mf(self.sd_universe, p['SD']['baja'])
        mf_sd_m = self.get_mf(self.sd_universe, p['SD']['media'])
        mf_sd_a = self.get_mf(self.sd_universe, p['SD']['alta'])
        
        # Reglas Dimensionales (W domina ligeramente)
        r1 = mu_w_p * mu_l_c  # W=P, L=C -> SD=Baja
        r2 = mu_w_p * mu_l_m  # W=P, L=M -> SD=Baja
        r3 = mu_w_p * mu_l_l  # W=P, L=L -> SD=Media
        r4 = mu_w_m * mu_l_c  # W=M, L=C -> SD=Baja
        r5 = mu_w_m * mu_l_m  # W=M, L=M -> SD=Media
        r6 = mu_w_m * mu_l_l  # W=M, L=L -> SD=Alta
        r7 = mu_w_g * mu_l_c  # W=G, L=C -> SD=Media
        r8 = mu_w_g * mu_l_m  # W=G, L=M -> SD=Alta
        r9 = mu_w_g * mu_l_l  # W=G, L=L -> SD=Alta
        
        return self.smooth_rule_centroid([
            (r1, p['SD']['baja']), (r2, p['SD']['baja']), (r3, p['SD']['media']),
            (r4, p['SD']['baja']), (r5, p['SD']['media']), (r6, p['SD']['alta']),
            (r7, p['SD']['media']), (r8, p['SD']['alta']), (r9, p['SD']['alta'])
        ])
    
    # ================================================================
    # FIS 2: SEVERIDAD DE EXTENSIÓN (D, C -> SE)
    # ================================================================
    
    def infer_fis2(self, d_val, c_val):
        p = self.params
        
        # Fuzzificación
        mf_d_b = self.get_mf(self.d_universe, p['D']['baja'])
        mf_d_m = self.get_mf(self.d_universe, p['D']['media'])
        mf_d_a = self.get_mf(self.d_universe, p['D']['alta'])
        
        mf_c_t = self.get_mf(self.c_universe, p['C']['truncada'])
        mf_c_p = self.get_mf(self.c_universe, p['C']['parcial'])
        mf_c_c = self.get_mf(self.c_universe, p['C']['completa'])
        
        mu_d_b = fuzz.interp_membership(self.d_universe, mf_d_b, d_val)
        mu_d_m = fuzz.interp_membership(self.d_universe, mf_d_m, d_val)
        mu_d_a = fuzz.interp_membership(self.d_universe, mf_d_a, d_val)
        
        mu_c_t = fuzz.interp_membership(self.c_universe, mf_c_t, c_val)
        mu_c_p = fuzz.interp_membership(self.c_universe, mf_c_p, c_val)
        mu_c_c = fuzz.interp_membership(self.c_universe, mf_c_c, c_val)
        
        # Salida
        mf_se_b = self.get_mf(self.se_universe, p['SE']['baja'])
        mf_se_m = self.get_mf(self.se_universe, p['SE']['media'])
        mf_se_a = self.get_mf(self.se_universe, p['SE']['alta'])
        
        # Reglas de Extensión (Incertidumbre C=truncada penaliza con mayor severidad)
        r1 = mu_c_c * mu_d_b  # C=completa, D=Baja -> SE=Baja
        r2 = mu_c_c * mu_d_m  # C=completa, D=Media -> SE=Media
        r3 = mu_c_c * mu_d_a  # C=completa, D=Alta -> SE=Alta
        r4 = mu_c_p * mu_d_b  # C=parcial, D=Baja -> SE=Baja
        r5 = mu_c_p * mu_d_m  # C=parcial, D=Media -> SE=Media
        r6 = mu_c_p * mu_d_a  # C=parcial, D=Alta -> SE=Alta
        r7 = mu_c_t * mu_d_b  # C=truncada, D=Baja -> SE=Media (Penalización)
        r8 = mu_c_t * mu_d_m  # C=truncada, D=Media -> SE=Media (Penalización suavizada)
        r9 = mu_c_t * mu_d_a  # C=truncada, D=Alta -> SE=Alta
        
        return self.smooth_rule_centroid([
            (r1, p['SE']['baja']), (r2, p['SE']['media']), (r3, p['SE']['alta']),
            (r4, p['SE']['baja']), (r5, p['SE']['media']), (r6, p['SE']['alta']),
            (r7, p['SE']['media']), (r8, p['SE']['media']), (r9, p['SE']['alta'])
        ])
    
    # ================================================================
    # FIS 3: SEVERIDAD FINAL (SD, SE -> SF)
    # ================================================================
    
    def infer_fis3(self, sd_val, se_val):
        p = self.params
        
        # Fuzzificación
        mf_sd_b = self.get_mf(self.sd_universe, p['SD']['baja'])
        mf_sd_m = self.get_mf(self.sd_universe, p['SD']['media'])
        mf_sd_a = self.get_mf(self.sd_universe, p['SD']['alta'])
        
        mf_se_b = self.get_mf(self.se_universe, p['SE']['baja'])
        mf_se_m = self.get_mf(self.se_universe, p['SE']['media'])
        mf_se_a = self.get_mf(self.se_universe, p['SE']['alta'])
        
        mu_sd_b = fuzz.interp_membership(self.sd_universe, mf_sd_b, sd_val)
        mu_sd_m = fuzz.interp_membership(self.sd_universe, mf_sd_m, sd_val)
        mu_sd_a = fuzz.interp_membership(self.sd_universe, mf_sd_a, sd_val)
        
        mu_se_b = fuzz.interp_membership(self.se_universe, mf_se_b, se_val)
        mu_se_m = fuzz.interp_membership(self.se_universe, mf_se_m, se_val)
        mu_se_a = fuzz.interp_membership(self.se_universe, mf_se_a, se_val)
        
        # Consecuente final
        mf_sf_l = self.get_mf(self.sf_universe, p['SF']['leve'])
        mf_sf_m = self.get_mf(self.sf_universe, p['SF']['moderada'])
        mf_sf_c = self.get_mf(self.sf_universe, p['SF']['critica'])
        
        # Reglas Jerárquicas Asimétricas (Dimensión SD pesa más que extensión SE)
        #                     SE_Baja      SE_Media     SE_Alta
        # SD_Baja             Leve         Leve         Moderada
        # SD_Media            Leve         Moderada     Crítica
        # SD_Alta             Moderada     Crítica      Crítica
        
        r1 = mu_sd_b * mu_se_b  # SD=B, SE=B -> SF=Leve
        r2 = mu_sd_b * mu_se_m  # SD=B, SE=M -> SF=Leve
        r3 = mu_sd_b * mu_se_a  # SD=B, SE=A -> SF=Moderada
        r4 = mu_sd_m * mu_se_b  # SD=M, SE=B -> SF=Leve
        r5 = mu_sd_m * mu_se_m  # SD=M, SE=M -> SF=Moderada
        r6 = mu_sd_m * mu_se_a  # SD=M, SE=A -> SF=Crítica
        r7 = mu_sd_a * mu_se_b  # SD=A, SE=B -> SF=Moderada
        r8 = mu_sd_a * mu_se_m  # SD=A, SE=M -> SF=Crítica
        r9 = mu_sd_a * mu_se_a  # SD=A, SE=A -> SF=Crítica
        
        return self.smooth_rule_centroid([
            (r1, p['SF']['leve']), (r2, p['SF']['leve']), (r3, p['SF']['moderada']),
            (r4, p['SF']['leve']), (r5, p['SF']['moderada']), (r6, p['SF']['critica']),
            (r7, p['SF']['moderada']), (r8, p['SF']['critica']), (r9, p['SF']['critica'])
        ])
    
    # ================================================================
    # VISUALIZACIÓN E INTERFAZ GRÁFICA
    # ================================================================
    
    def setup_plots(self):
        # FIS 1 - Entrada/Salida
        self.draw_variable(self.ax_w, 'W', self.w_universe, 'W: Anchura (mm)')
        self.draw_variable(self.ax_l, 'L', self.l_universe, 'L: Longitud (mm)')
        self.draw_variable(self.ax_sd, 'SD', self.sd_universe, 'SD: Sev. Dimensional')
        
        # FIS 2 - Entrada/Salida
        self.draw_variable(self.ax_d, 'D', self.d_universe, 'D: Densidad de Área')
        self.draw_variable(self.ax_c, 'C', self.c_universe, 'C: Completitud')
        self.draw_variable(self.ax_se, 'SE', self.se_universe, 'SE: Sev. Extensión')
        
        # FIS 3 - Entrada/Salida
        self.draw_variable(self.ax_sd_in, 'SD', self.sd_universe, 'SD (entrada FIS3)')
        self.draw_variable(self.ax_se_in, 'SE', self.se_universe, 'SE (entrada FIS3)')
        self.draw_variable(self.ax_sf, 'SF', self.sf_universe, 'SF: Severidad Final')
        
        # Mapeo de axes a variables para interacción de arrastre
        self.ax_var_map = {
            self.ax_w: ('W', self.w_universe),
            self.ax_l: ('L', self.l_universe),
            self.ax_sd: ('SD', self.sd_universe),
            self.ax_d: ('D', self.d_universe),
            self.ax_c: ('C', self.c_universe),
            self.ax_se: ('SE', self.se_universe),
            self.ax_sd_in: ('SD', self.sd_universe),
            self.ax_se_in: ('SE', self.se_universe),
            self.ax_sf: ('SF', self.sf_universe)
        }
    
    def draw_variable(self, ax, var_key, universe, title):
        ax.clear()
        colors = ['#3498db', '#e67e22', '#e74c3c']
        
        for (name, p), color in zip(self.params[var_key].items(), colors):
            mf = self.get_mf(universe, p)
            y_vals = [0, 1, 0] if len(p) == 3 else [0, 1, 1, 0]
            
            ax.plot(universe, mf, label=name, lw=2, color=color, alpha=0.7)
            ax.fill_between(universe, mf, alpha=0.15, color=color)
            
            # Dibujar puntos de control interactivos
            for i, px in enumerate(p):
                ax.plot(px, y_vals[i], 'o', color=color, markersize=6, 
                       markeredgecolor='black', alpha=0.8, picker=True, 
                       pickradius=8, gid=f"{var_key}:{name}:{i}")
        
        ax.set_title(title, fontsize=9, fontweight='bold')
        ax.set_ylim(-0.1, 1.15)
        ax.legend(fontsize='x-small', loc='upper right')
        ax.grid(alpha=0.25)
    
    def update_all_surfaces(self):
        res = 15  # Resolución baja para que el render sea fluido
        
        # Superficie FIS 1 (W vs L)
        w_range = np.linspace(0, 30, res)
        l_range = np.linspace(0, 2000, res)
        W, L = np.meshgrid(w_range, l_range)
        SD = np.zeros_like(W)
        for i in range(res):
            for j in range(res):
                SD[i,j] = self.infer_fis1(W[i,j], L[i,j])
        
        self.ax_surf1.clear()
        self.ax_surf1.plot_surface(W, L, SD, cmap='Blues', alpha=0.7)
        self.ax_surf1.set_title('Superficie FIS 1', fontsize=8, fontweight='bold')
        self.ax_surf1.set_xlabel('W (mm)', fontsize=6)
        self.ax_surf1.set_ylabel('L (mm)', fontsize=6)
        self.ax_surf1.set_zlabel('SD', fontsize=6)
        self.ax_surf1.tick_params(labelsize=6)
        
        # Superficie FIS 2 (D vs C)
        d_range = np.linspace(0, 1, res)
        c_range = np.linspace(0, 1, res)
        D, C = np.meshgrid(d_range, c_range)
        SE = np.zeros_like(D)
        for i in range(res):
            for j in range(res):
                SE[i,j] = self.infer_fis2(D[i,j], C[i,j])
        
        self.ax_surf2.clear()
        self.ax_surf2.plot_surface(D, C, SE, cmap='Oranges', alpha=0.7)
        self.ax_surf2.set_title('Superficie FIS 2', fontsize=8, fontweight='bold')
        self.ax_surf2.set_xlabel('D', fontsize=6)
        self.ax_surf2.set_ylabel('C', fontsize=6)
        self.ax_surf2.set_zlabel('SE', fontsize=6)
        self.ax_surf2.tick_params(labelsize=6)
        
        # Superficie FIS 3 (SD vs SE)
        sd_range = np.linspace(0, 100, res)
        se_range = np.linspace(0, 100, res)
        SD_in, SE_in = np.meshgrid(sd_range, se_range)
        SF = np.zeros_like(SD_in)
        for i in range(res):
            for j in range(res):
                SF[i,j] = self.infer_fis3(SD_in[i,j], SE_in[i,j])
        
        self.ax_surf3.clear()
        self.ax_surf3.plot_surface(SD_in, SE_in, SF, cmap='Reds', alpha=0.7)
        self.ax_surf3.set_title('Superficie FIS 3 (Final)', fontsize=8, fontweight='bold')
        self.ax_surf3.set_xlabel('SD', fontsize=6)
        self.ax_surf3.set_ylabel('SE', fontsize=6)
        self.ax_surf3.set_zlabel('SF', fontsize=6)
        self.ax_surf3.tick_params(labelsize=6)
    
    def update_preview(self, val):
        pass  # Evitamos recalculado en tiempo real en sliders pesados si lo desea el usuario,
              # pero en este script se activa mediante botón o final de arrastre.
    
    def calculate_full_inference(self, event):
        w_val = self.slider_w.val
        l_val = self.slider_l.val
        d_val = self.slider_d.val
        c_val = self.slider_c.val
        
        # Inferencia encadenada usando el método evaluate
        res = self.evaluate(w_val, l_val, d_val, c_val)
        self.sd_result = res["sd"]
        self.se_result = res["se"]
        self.sf_result = res["sf"]
        nivel = res["nivel"]
        rec = res["recomendacion"]
        
        # Determinación del color para la interfaz gráfica
        if self.sf_result < 35.0:
            color_hex = '#2ecc71'
        elif self.sf_result < 70.0:
            color_hex = '#f39c12'
        else:
            color_hex = '#e74c3c'
            
        self.ax_result.clear()
        self.ax_result.axis('off')
        
        result_text = (
            f"=========================================================================================\n"
            f"  ENTRADAS: W={w_val:.2f} mm | L={l_val:.1f} mm | D={d_val:.2f} | C={c_val:.2f}\n"
            f"  ---------------------------------------------------------------------------------------\n"
            f"  [FIS 1] Severidad Dimensional (SD): {self.sd_result:.1f}%\n"
            f"  [FIS 2] Severidad de Extensión   (SE): {self.se_result:.1f}%\n"
            f"  ---------------------------------------------------------------------------------------\n"
            f"  [FIS 3] SEVERIDAD FINAL DE GRIETA (SF): {self.sf_result:.1f}%  ->  Nivel: {nivel}\n"
            f"  RECOMENDACIÓN TÉCNICA: {rec}\n"
            f"========================================================================================="
        )
        
        self.ax_result.text(0.5, 0.5, result_text, transform=self.ax_result.transAxes,
                          fontsize=9.5, fontfamily='monospace', verticalalignment='center',
                          horizontalalignment='center',
                          bbox=dict(boxstyle='round', facecolor=color_hex, alpha=0.2))
        
        self.fig.canvas.draw_idle()

    # ================================================================
    # REGISTRO DE DATOS Y CASOS
    # ================================================================
    
    def save_record_data(self, w_val, l_val, d_val, c_val, sd_val, se_val, sf_val, label):
        """Guarda un registro auditable del caso evaluado en un archivo JSON"""
        record = {
            "inputs": {
                "w_anchura_mm": float(w_val),
                "l_longitud_mm": float(l_val),
                "d_densidad": float(d_val),
                "c_completitud": float(c_val)
            },
            "intermediate": {
                "sd_dimensional": float(sd_val),
                "se_extension": float(se_val)
            },
            "output": {
                "sf_final_score": float(sf_val),
                "severity_label": label
            }
        }
        
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fis_evaluations.json")
        try:
            records = []
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    records = json.load(f)
            records.append(record)
            with open(filepath, 'w') as f:
                json.dump(records, f, indent=4)
            print(f"Registro guardado exitosamente en: {filepath}")
        except Exception as e:
            print(f"Error al guardar registro: {e}")

    def save_record(self, event):
        self.save_record_data(
            self.slider_w.val,
            self.slider_l.val,
            self.slider_d.val,
            self.slider_c.val,
            self.sd_result,
            self.se_result,
            self.sf_result,
            "LEVE" if self.sf_result < 35.0 else ("MODERADA" if self.sf_result < 70.0 else "CRÍTICA")
        )

    # ================================================================
    # INTERACTIVIDAD POR ARRASTRE DE PUNTOS
    # ================================================================
    
    def on_press(self, event):
        if event.inaxes not in self.ax_var_map:
            return
        self.active_ax = event.inaxes
        
        for line in self.active_ax.get_lines():
            gid = line.get_gid()
            if gid:
                cont, _ = line.contains(event)
                if cont:
                    self.dragging_point = gid
                    return
    
    def on_motion(self, event):
        if self.dragging_point is None or event.xdata is None:
            return
        
        var, name, idx = self.dragging_point.split(':')
        idx = int(idx)
        new_x = float(event.xdata)
        
        # Determinar límites de la variable física
        if var == 'W':
            limit = 30.0
        elif var == 'L':
            limit = 2000.0
        elif var in ['SD', 'SE', 'SF']:
            limit = 100.0
        else:
            limit = 1.0
            
        new_x = max(0.0, min(new_x, limit))
        self.params[var][name][idx] = new_x
        self.params[var][name].sort()
        
        # Redibujar variables modificadas
        var_key, universe = self.ax_var_map[self.active_ax]
        title = self.active_ax.get_title()
        self.draw_variable(self.active_ax, var_key, universe, title)
        self.fig.canvas.draw_idle()
    
    def on_release(self, event):
        if self.dragging_point is not None:
            self.update_all_surfaces()
            self.calculate_full_inference(None)
        self.dragging_point = None

if __name__ == "__main__":
    import argparse
    import sys
    
    # Comprobar si se pasaron argumentos de línea de comandos
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='Evaluación Jerárquica Difusa de Grietas')
        parser.add_argument('--w', type=float, required=True, help='Anchura de grieta en mm (0-30)')
        parser.add_argument('--l', type=float, required=True, help='Longitud de grieta en mm (0-2000)')
        parser.add_argument('--d', type=float, required=True, help='Densidad superficial (0-1)')
        parser.add_argument('--c', type=float, required=True, help='Completitud/continuidad (0-1)')
        parser.add_argument('--save', action='store_true', help='Guardar el caso evaluado en JSON')
        args = parser.parse_args()
        
        # Usar backend no interactivo para evitar fallos de interfaz gráfica en ejecuciones headless
        import matplotlib
        matplotlib.use('Agg')
        
        fis = CrackHierarchicalFIS(run_gui=False)
        res = fis.evaluate(args.w, args.l, args.d, args.c)
        
        print("\n==================================================")
        print("  RESULTADOS DE INFERENCIA DIFUSA DE GRIETAS")
        print("==================================================")
        print(f"  Entrada W (Ancho):       {args.w:.3f} mm")
        print(f"  Entrada L (Longitud):    {args.l:.1f} mm")
        print(f"  Entrada D (Densidad):    {args.d:.3f}")
        print(f"  Entrada C (Completitud): {args.c:.3f}")
        print("  --------------------------------------------------")
        print(f"  [FIS 1] Severidad Dimensional (SD): {res['sd']:.1f}%")
        print(f"  [FIS 2] Severidad de Extensión   (SE): {res['se']:.1f}%")
        print(f"  --------------------------------------------------")
        print(f"  [FIS 3] SEVERIDAD FINAL (SF):       {res['sf']:.1f}%")
        print(f"  NIVEL LINGÜÍSTICO:                  {res['nivel']}")
        print(f"  RECOMENDACIÓN TÉCNICA:              {res['recomendacion']}")
        print("==================================================\n")
        
        if args.save:
            fis.save_record_data(args.w, args.l, args.d, args.c, res['sd'], res['se'], res['sf'], res['nivel'])
    else:
        # Ejecución gráfica por defecto
        CrackHierarchicalFIS(run_gui=True)
