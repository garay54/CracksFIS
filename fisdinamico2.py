import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
import skfuzzy as fuzz

class HierarchicalFIS:
    def __init__(self):
        # ============================================================
        # 1. UNIVERSOS DE DISCURSO
        # ============================================================
        
        # FIS 1 - Entradas geométricas
        self.w_universe = np.linspace(0, 30, 301)      # Anchura: 0-30 mm
        self.l_universe = np.linspace(0, 200, 401)    # Longitud: 0-200 mm
        
        # FIS 2 - Entradas visuales
        self.c_universe = np.linspace(0, 1, 201)      # Completitud: 0-1
        self.a_universe = np.linspace(0, 1, 201)      # Apariencia: 0-1
        
        # Salidas intermedias y final
        self.sg_universe = np.linspace(0, 100, 201)   # Severidad Geométrica
        self.sv_universe = np.linspace(0, 100, 201)   # Severidad Visual
        self.sf_universe = np.linspace(0, 100, 201)   # Severidad Final
        
        # ============================================================
        # 2. PARÁMETROS DE FUNCIONES DE MEMBRESÍA
        # ============================================================
        
        self.params = {
            # FIS 1 - Variables geométricas
            'W': {
                'pequeña': [0.0, 0.0, 3.0, 8.0],
                'media': [5.0, 12.0, 18.0],
                'grande': [15.0, 22.0, 30.0, 30.0]
            },
            'L': {
                'corta': [0.0, 0.0, 30.0, 60.0],
                'media': [40.0, 80.0, 120.0],
                'larga': [100.0, 150.0, 200.0, 200.0]
            },
            
            # FIS 2 - Variables visuales
            'C': {
                'truncada': [0.0, 0.0, 0.2, 0.4],
                'parcial': [0.3, 0.5, 0.7],
                'completa': [0.6, 0.8, 1.0, 1.0]
            },
            'A': {
                'superficial': [0.0, 0.0, 0.2, 0.4],
                'moderada': [0.3, 0.5, 0.7],
                'profunda': [0.6, 0.8, 1.0, 1.0]
            },
            
            # Salidas FIS 1 y FIS 2
            'SG': {
                'baja': [0, 0, 20, 40],
                'media': [30, 50, 70],
                'alta': [60, 80, 100, 100]
            },
            'SV': {
                'baja': [0, 0, 20, 40],
                'media': [30, 50, 70],
                'alta': [60, 80, 100, 100]
            },
            
            # Salida FIS 3
            'SF': {
                'leve': [0, 0, 20, 35],
                'moderada': [25, 50, 75],
                'critica': [65, 85, 100, 100]
            }
        }
        
        # ============================================================
        # 3. CONFIGURACIÓN DE LA FIGURA
        # ============================================================
        
        self.fig = plt.figure(figsize=(18, 12))
        self.fig.canvas.manager.set_window_title('Sistema FIS Jerárquico - Evaluación de Grietas')
        
        # Layout de subplots
        # Fila 1: FIS 1 (W, L, SG)
        self.ax_w = plt.subplot2grid((4, 4), (0, 0))
        self.ax_l = plt.subplot2grid((4, 4), (0, 1))
        self.ax_sg = plt.subplot2grid((4, 4), (0, 2))
        self.ax_surf1 = plt.subplot2grid((4, 4), (0, 3), projection='3d')
        
        # Fila 2: FIS 2 (C, A, SV)
        self.ax_c = plt.subplot2grid((4, 4), (1, 0))
        self.ax_a = plt.subplot2grid((4, 4), (1, 1))
        self.ax_sv = plt.subplot2grid((4, 4), (1, 2))
        self.ax_surf2 = plt.subplot2grid((4, 4), (1, 3), projection='3d')
        
        # Fila 3: FIS 3 (SG_in, SV_in, SF)
        self.ax_sg_in = plt.subplot2grid((4, 4), (2, 0))
        self.ax_sv_in = plt.subplot2grid((4, 4), (2, 1))
        self.ax_sf = plt.subplot2grid((4, 4), (2, 2))
        self.ax_surf3 = plt.subplot2grid((4, 4), (2, 3), projection='3d')
        
        # Fila 4: Panel de control y resultado
        self.ax_result = plt.subplot2grid((4, 4), (3, 0), colspan=4)
        self.ax_result.axis('off')
        
        plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.15, 
                          hspace=0.4, wspace=0.3)
        
        # ============================================================
        # 4. SLIDERS PARA VALORES DE ENTRADA
        # ============================================================
        
        # Sliders para FIS 1
        ax_slider_w = plt.axes([0.1, 0.08, 0.15, 0.02])
        self.slider_w = Slider(ax_slider_w, 'Anchura (mm)', 0, 30, valinit=10)
        
        ax_slider_l = plt.axes([0.1, 0.05, 0.15, 0.02])
        self.slider_l = Slider(ax_slider_l, 'Longitud (mm)', 0, 200, valinit=80)
        
        # Sliders para FIS 2
        ax_slider_c = plt.axes([0.4, 0.08, 0.15, 0.02])
        self.slider_c = Slider(ax_slider_c, 'Completitud', 0, 1, valinit=0.7)
        
        ax_slider_a = plt.axes([0.4, 0.05, 0.15, 0.02])
        self.slider_a = Slider(ax_slider_a, 'Apariencia', 0, 1, valinit=0.5)
        
        # Botón de actualización
        ax_btn = plt.axes([0.75, 0.05, 0.15, 0.05])
        self.btn = Button(ax_btn, 'Calcular Severidad', color='#e74c3c', hovercolor='#c0392b')
        self.btn.on_clicked(self.calculate_full_inference)
        
        # Conectar sliders
        self.slider_w.on_changed(self.update_preview)
        self.slider_l.on_changed(self.update_preview)
        self.slider_c.on_changed(self.update_preview)
        self.slider_a.on_changed(self.update_preview)
        
        # ============================================================
        # 5. ESTADO Y EVENTOS
        # ============================================================
        
        self.dragging_point = None
        self.active_ax = None
        self.ax_var_map = {}  # Mapeo de axes a variables
        
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        
        # ============================================================
        # 6. INICIALIZACIÓN
        # ============================================================
        
        self.setup_plots()
        self.update_all_surfaces()
        self.calculate_full_inference(None)
        
        plt.show()
    
    # ================================================================
    # FUNCIONES DE MEMBRESÍA
    # ================================================================
    
    def get_mf(self, universe, params):
        """Genera función de membresía según número de parámetros"""
        if len(params) == 3:
            return fuzz.trimf(universe, params)
        else:
            return fuzz.trapmf(universe, params)
    
    # ================================================================
    # FIS 1: SEVERIDAD GEOMÉTRICA
    # ================================================================
    
    def infer_fis1(self, w_val, l_val):
        """Inferencia del FIS 1: Anchura y Longitud → Severidad Geométrica"""
        p = self.params
        
        # Funciones de membresía de entrada
        mf_w_p = self.get_mf(self.w_universe, p['W']['pequeña'])
        mf_w_m = self.get_mf(self.w_universe, p['W']['media'])
        mf_w_g = self.get_mf(self.w_universe, p['W']['grande'])
        
        mf_l_c = self.get_mf(self.l_universe, p['L']['corta'])
        mf_l_m = self.get_mf(self.l_universe, p['L']['media'])
        mf_l_l = self.get_mf(self.l_universe, p['L']['larga'])
        
        # Fuzzificación
        mu_w_p = fuzz.interp_membership(self.w_universe, mf_w_p, w_val)
        mu_w_m = fuzz.interp_membership(self.w_universe, mf_w_m, w_val)
        mu_w_g = fuzz.interp_membership(self.w_universe, mf_w_g, w_val)
        
        mu_l_c = fuzz.interp_membership(self.l_universe, mf_l_c, l_val)
        mu_l_m = fuzz.interp_membership(self.l_universe, mf_l_m, l_val)
        mu_l_l = fuzz.interp_membership(self.l_universe, mf_l_l, l_val)
        
        # Funciones de membresía de salida
        mf_sg_b = self.get_mf(self.sg_universe, p['SG']['baja'])
        mf_sg_m = self.get_mf(self.sg_universe, p['SG']['media'])
        mf_sg_a = self.get_mf(self.sg_universe, p['SG']['alta'])
        
        # ============================================================
        # REGLAS FIS 1
        # ============================================================
        # R1: IF W=pequeña AND L=corta THEN SG=baja
        r1 = np.fmin(mu_w_p, mu_l_c)
        
        # R2: IF W=pequeña AND L=media THEN SG=baja
        r2 = np.fmin(mu_w_p, mu_l_m)
        
        # R3: IF W=pequeña AND L=larga THEN SG=media
        r3 = np.fmin(mu_w_p, mu_l_l)
        
        # R4: IF W=media AND L=corta THEN SG=baja
        r4 = np.fmin(mu_w_m, mu_l_c)
        
        # R5: IF W=media AND L=media THEN SG=media
        r5 = np.fmin(mu_w_m, mu_l_m)
        
        # R6: IF W=media AND L=larga THEN SG=alta
        r6 = np.fmin(mu_w_m, mu_l_l)
        
        # R7: IF W=grande AND L=corta THEN SG=media
        r7 = np.fmin(mu_w_g, mu_l_c)
        
        # R8: IF W=grande AND L=media THEN SG=alta
        r8 = np.fmin(mu_w_g, mu_l_m)
        
        # R9: IF W=grande AND L=larga THEN SG=alta
        r9 = np.fmin(mu_w_g, mu_l_l)
        
        # Implicación
        out_baja = np.fmin(np.fmax(np.fmax(r1, r2), r4), mf_sg_b)
        out_media = np.fmin(np.fmax(np.fmax(r3, r5), r7), mf_sg_m)
        out_alta = np.fmin(np.fmax(np.fmax(r6, r8), r9), mf_sg_a)
        
        # Agregación
        aggregated = np.fmax(out_baja, np.fmax(out_media, out_alta))
        
        if np.allclose(aggregated, 0):
            return 0.0
        return float(fuzz.defuzz(self.sg_universe, aggregated, 'centroid'))
    
    # ================================================================
    # FIS 2: SEVERIDAD VISUAL
    # ================================================================
    
    def infer_fis2(self, c_val, a_val):
        """Inferencia del FIS 2: Completitud y Apariencia → Severidad Visual"""
        p = self.params
        
        # Funciones de membresía de entrada
        mf_c_t = self.get_mf(self.c_universe, p['C']['truncada'])
        mf_c_p = self.get_mf(self.c_universe, p['C']['parcial'])
        mf_c_c = self.get_mf(self.c_universe, p['C']['completa'])
        
        mf_a_s = self.get_mf(self.a_universe, p['A']['superficial'])
        mf_a_m = self.get_mf(self.a_universe, p['A']['moderada'])
        mf_a_p = self.get_mf(self.a_universe, p['A']['profunda'])
        
        # Fuzzificación
        mu_c_t = fuzz.interp_membership(self.c_universe, mf_c_t, c_val)
        mu_c_p = fuzz.interp_membership(self.c_universe, mf_c_p, c_val)
        mu_c_c = fuzz.interp_membership(self.c_universe, mf_c_c, c_val)
        
        mu_a_s = fuzz.interp_membership(self.a_universe, mf_a_s, a_val)
        mu_a_m = fuzz.interp_membership(self.a_universe, mf_a_m, a_val)
        mu_a_p = fuzz.interp_membership(self.a_universe, mf_a_p, a_val)
        
        # Funciones de membresía de salida
        mf_sv_b = self.get_mf(self.sv_universe, p['SV']['baja'])
        mf_sv_m = self.get_mf(self.sv_universe, p['SV']['media'])
        mf_sv_a = self.get_mf(self.sv_universe, p['SV']['alta'])
        
        # ============================================================
        # REGLAS FIS 2
        # ============================================================
        # Nota: Truncada = incertidumbre = penalización (más severo)
        #       Profunda = más severo
        
        # R1: IF C=completa AND A=superficial THEN SV=baja
        r1 = np.fmin(mu_c_c, mu_a_s)
        
        # R2: IF C=completa AND A=moderada THEN SV=media
        r2 = np.fmin(mu_c_c, mu_a_m)
        
        # R3: IF C=completa AND A=profunda THEN SV=alta
        r3 = np.fmin(mu_c_c, mu_a_p)
        
        # R4: IF C=parcial AND A=superficial THEN SV=baja
        r4 = np.fmin(mu_c_p, mu_a_s)
        
        # R5: IF C=parcial AND A=moderada THEN SV=media
        r5 = np.fmin(mu_c_p, mu_a_m)
        
        # R6: IF C=parcial AND A=profunda THEN SV=alta
        r6 = np.fmin(mu_c_p, mu_a_p)
        
        # R7: IF C=truncada AND A=superficial THEN SV=media (penalización)
        r7 = np.fmin(mu_c_t, mu_a_s)
        
        # R8: IF C=truncada AND A=moderada THEN SV=alta (penalización)
        r8 = np.fmin(mu_c_t, mu_a_m)
        
        # R9: IF C=truncada AND A=profunda THEN SV=alta
        r9 = np.fmin(mu_c_t, mu_a_p)
        
        # Implicación
        out_baja = np.fmin(np.fmax(r1, r4), mf_sv_b)
        out_media = np.fmin(np.fmax(np.fmax(r2, r5), r7), mf_sv_m)
        out_alta = np.fmin(np.fmax(np.fmax(np.fmax(r3, r6), r8), r9), mf_sv_a)
        
        # Agregación
        aggregated = np.fmax(out_baja, np.fmax(out_media, out_alta))
        
        if np.allclose(aggregated, 0):
            return 0.0
        return float(fuzz.defuzz(self.sv_universe, aggregated, 'centroid'))
    
    # ================================================================
    # FIS 3: SEVERIDAD FINAL
    # ================================================================
    
    def infer_fis3(self, sg_val, sv_val):
        """Inferencia del FIS 3: SG y SV → Severidad Final"""
        p = self.params
        
        # Usamos los mismos universos de SG y SV como entradas
        # Funciones de membresía de entrada (reutilizamos parámetros)
        mf_sg_b = self.get_mf(self.sg_universe, p['SG']['baja'])
        mf_sg_m = self.get_mf(self.sg_universe, p['SG']['media'])
        mf_sg_a = self.get_mf(self.sg_universe, p['SG']['alta'])
        
        mf_sv_b = self.get_mf(self.sv_universe, p['SV']['baja'])
        mf_sv_m = self.get_mf(self.sv_universe, p['SV']['media'])
        mf_sv_a = self.get_mf(self.sv_universe, p['SV']['alta'])
        
        # Fuzzificación
        mu_sg_b = fuzz.interp_membership(self.sg_universe, mf_sg_b, sg_val)
        mu_sg_m = fuzz.interp_membership(self.sg_universe, mf_sg_m, sg_val)
        mu_sg_a = fuzz.interp_membership(self.sg_universe, mf_sg_a, sg_val)
        
        mu_sv_b = fuzz.interp_membership(self.sv_universe, mf_sv_b, sv_val)
        mu_sv_m = fuzz.interp_membership(self.sv_universe, mf_sv_m, sv_val)
        mu_sv_a = fuzz.interp_membership(self.sv_universe, mf_sv_a, sv_val)
        
        # Funciones de membresía de salida final
        mf_sf_l = self.get_mf(self.sf_universe, p['SF']['leve'])
        mf_sf_m = self.get_mf(self.sf_universe, p['SF']['moderada'])
        mf_sf_c = self.get_mf(self.sf_universe, p['SF']['critica'])
        
        # ============================================================
        # REGLAS FIS 3 (Matriz completa 3x3)
        # ============================================================
        #                    SV_Baja    SV_Media   SV_Alta
        # SG_Baja            Leve       Leve       Moderada
        # SG_Media           Leve       Moderada   Crítica
        # SG_Alta            Moderada   Crítica    Crítica
        
        # R1: IF SG=baja AND SV=baja THEN SF=leve
        r1 = np.fmin(mu_sg_b, mu_sv_b)
        
        # R2: IF SG=baja AND SV=media THEN SF=leve
        r2 = np.fmin(mu_sg_b, mu_sv_m)
        
        # R3: IF SG=baja AND SV=alta THEN SF=moderada
        r3 = np.fmin(mu_sg_b, mu_sv_a)
        
        # R4: IF SG=media AND SV=baja THEN SF=leve
        r4 = np.fmin(mu_sg_m, mu_sv_b)
        
        # R5: IF SG=media AND SV=media THEN SF=moderada
        r5 = np.fmin(mu_sg_m, mu_sv_m)
        
        # R6: IF SG=media AND SV=alta THEN SF=crítica
        r6 = np.fmin(mu_sg_m, mu_sv_a)
        
        # R7: IF SG=alta AND SV=baja THEN SF=moderada
        r7 = np.fmin(mu_sg_a, mu_sv_b)
        
        # R8: IF SG=alta AND SV=media THEN SF=crítica
        r8 = np.fmin(mu_sg_a, mu_sv_m)
        
        # R9: IF SG=alta AND SV=alta THEN SF=crítica
        r9 = np.fmin(mu_sg_a, mu_sv_a)
        
        # Implicación
        out_leve = np.fmin(np.fmax(np.fmax(r1, r2), r4), mf_sf_l)
        out_moderada = np.fmin(np.fmax(np.fmax(r3, r5), r7), mf_sf_m)
        out_critica = np.fmin(np.fmax(np.fmax(r6, r8), r9), mf_sf_c)
        
        # Agregación
        aggregated = np.fmax(out_leve, np.fmax(out_moderada, out_critica))
        
        if np.allclose(aggregated, 0):
            return 0.0
        return float(fuzz.defuzz(self.sf_universe, aggregated, 'centroid'))
    
    # ================================================================
    # VISUALIZACIÓN
    # ================================================================
    
    def setup_plots(self):
        """Configura todos los gráficos de funciones de membresía"""
        # FIS 1
        self.draw_variable(self.ax_w, 'W', self.w_universe, 'Anchura (mm)')
        self.draw_variable(self.ax_l, 'L', self.l_universe, 'Longitud (mm)')
        self.draw_variable(self.ax_sg, 'SG', self.sg_universe, 'Sev. Geométrica')
        
        # FIS 2
        self.draw_variable(self.ax_c, 'C', self.c_universe, 'Completitud')
        self.draw_variable(self.ax_a, 'A', self.a_universe, 'Apariencia')
        self.draw_variable(self.ax_sv, 'SV', self.sv_universe, 'Sev. Visual')
        
        # FIS 3
        self.draw_variable(self.ax_sg_in, 'SG', self.sg_universe, 'SG (entrada)')
        self.draw_variable(self.ax_sv_in, 'SV', self.sv_universe, 'SV (entrada)')
        self.draw_variable(self.ax_sf, 'SF', self.sf_universe, 'Sev. Final')
        
        # Mapeo de axes a variables
        self.ax_var_map = {
            self.ax_w: ('W', self.w_universe),
            self.ax_l: ('L', self.l_universe),
            self.ax_c: ('C', self.c_universe),
            self.ax_a: ('A', self.a_universe),
            self.ax_sg: ('SG', self.sg_universe),
            self.ax_sv: ('SV', self.sv_universe),
            self.ax_sg_in: ('SG', self.sg_universe),
            self.ax_sv_in: ('SV', self.sv_universe),
            self.ax_sf: ('SF', self.sf_universe)
        }
    
    def draw_variable(self, ax, var_key, universe, title):
        """Dibuja las funciones de membresía de una variable"""
        ax.clear()
        colors = ['#3498db', '#e67e22', '#e74c3c']
        
        for (name, p), color in zip(self.params[var_key].items(), colors):
            mf = self.get_mf(universe, p)
            y_vals = [0, 1, 0] if len(p) == 3 else [0, 1, 1, 0]
            
            ax.plot(universe, mf, label=name, lw=2, color=color, alpha=0.7)
            ax.fill_between(universe, mf, alpha=0.2, color=color)
            
            for i, px in enumerate(p):
                ax.plot(px, y_vals[i], 'o', color=color, markersize=7, 
                       markeredgecolor='black', alpha=0.8, picker=True, 
                       pickradius=8, gid=f"{var_key}:{name}:{i}")
        
        ax.set_title(title, fontsize=9, fontweight='bold')
        ax.set_ylim(-0.1, 1.15)
        ax.legend(fontsize='x-small', loc='upper right')
        ax.grid(alpha=0.3)
    
    def update_all_surfaces(self):
        """Actualiza todas las superficies 3D"""
        res = 20
        
        # Superficie FIS 1
        w_range = np.linspace(0, 30, res)
        l_range = np.linspace(0, 200, res)
        W, L = np.meshgrid(w_range, l_range)
        SG = np.zeros_like(W)
        for i in range(res):
            for j in range(res):
                SG[i,j] = self.infer_fis1(W[i,j], L[i,j])
        
        self.ax_surf1.clear()
        self.ax_surf1.plot_surface(W, L, SG, cmap='Blues', alpha=0.8)
        self.ax_surf1.set_title('FIS 1: Sev. Geométrica', fontsize=8)
        self.ax_surf1.set_xlabel('W', fontsize=7)
        self.ax_surf1.set_ylabel('L', fontsize=7)
        self.ax_surf1.set_zlabel('SG', fontsize=7)
        
        # Superficie FIS 2
        c_range = np.linspace(0, 1, res)
        a_range = np.linspace(0, 1, res)
        C, A = np.meshgrid(c_range, a_range)
        SV = np.zeros_like(C)
        for i in range(res):
            for j in range(res):
                SV[i,j] = self.infer_fis2(C[i,j], A[i,j])
        
        self.ax_surf2.clear()
        self.ax_surf2.plot_surface(C, A, SV, cmap='Oranges', alpha=0.8)
        self.ax_surf2.set_title('FIS 2: Sev. Visual', fontsize=8)
        self.ax_surf2.set_xlabel('C', fontsize=7)
        self.ax_surf2.set_ylabel('A', fontsize=7)
        self.ax_surf2.set_zlabel('SV', fontsize=7)
        
        # Superficie FIS 3
        sg_range = np.linspace(0, 100, res)
        sv_range = np.linspace(0, 100, res)
        SG_in, SV_in = np.meshgrid(sg_range, sv_range)
        SF = np.zeros_like(SG_in)
        for i in range(res):
            for j in range(res):
                SF[i,j] = self.infer_fis3(SG_in[i,j], SV_in[i,j])
        
        self.ax_surf3.clear()
        self.ax_surf3.plot_surface(SG_in, SV_in, SF, cmap='Reds', alpha=0.8)
        self.ax_surf3.set_title('FIS 3: Sev. Final', fontsize=8)
        self.ax_surf3.set_xlabel('SG', fontsize=7)
        self.ax_surf3.set_ylabel('SV', fontsize=7)
        self.ax_surf3.set_zlabel('SF', fontsize=7)
    
    def update_preview(self, val):
        """Actualiza la vista previa cuando cambian los sliders"""
        pass  # Se calculará al presionar el botón
    
    def calculate_full_inference(self, event):
        """Calcula la inferencia completa del sistema jerárquico"""
        # Obtener valores de los sliders
        w_val = self.slider_w.val
        l_val = self.slider_l.val
        c_val = self.slider_c.val
        a_val = self.slider_a.val
        
        # Inferencia en cascada
        sg_result = self.infer_fis1(w_val, l_val)
        sv_result = self.infer_fis2(c_val, a_val)
        sf_result = self.infer_fis3(sg_result, sv_result)
        
        # Determinar nivel de severidad
        if sf_result < 35:
            nivel = "LEVE"
            color = '#27ae60'
        elif sf_result < 65:
            nivel = "MODERADA"
            color = '#f39c12'
        else:
            nivel = "CRÍTICA"
            color = '#e74c3c'
        
        # Mostrar resultados
        self.ax_result.clear()
        self.ax_result.axis('off')
        
        result_text = (
            f"═══════════════════════════════════════════════════════════════════════════════════════\n"
            f"  ENTRADAS:  Anchura={w_val:.1f}mm  |  Longitud={l_val:.1f}mm  |  "
            f"Completitud={c_val:.2f}  |  Apariencia={a_val:.2f}\n"
            f"───────────────────────────────────────────────────────────────────────────────────────\n"
            f"  FIS 1 → Severidad Geométrica: {sg_result:.1f}%    |    "
            f"FIS 2 → Severidad Visual: {sv_result:.1f}%\n"
            f"───────────────────────────────────────────────────────────────────────────────────────\n"
            f"  FIS 3 → SEVERIDAD FINAL: {sf_result:.1f}%  →  {nivel}\n"
            f"═══════════════════════════════════════════════════════════════════════════════════════"
        )
        
        self.ax_result.text(0.5, 0.5, result_text, transform=self.ax_result.transAxes,
                          fontsize=10, fontfamily='monospace', verticalalignment='center',
                          horizontalalignment='center',
                          bbox=dict(boxstyle='round', facecolor=color, alpha=0.3))
        
        self.fig.canvas.draw_idle()
    
    # ================================================================
    # INTERACTIVIDAD (ARRASTRE DE PUNTOS)
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
        
        # Determinar límites según la variable
        if var == 'W':
            limit = 30.0
        elif var == 'L':
            limit = 200.0
        elif var in ['SG', 'SV', 'SF']:
            limit = 100.0
        else:
            limit = 1.0
        
        new_x = max(0.0, min(new_x, limit))
        self.params[var][name][idx] = new_x
        self.params[var][name].sort()
        
        # Redibujar
        var_key, universe = self.ax_var_map[self.active_ax]
        title = self.active_ax.get_title()
        self.draw_variable(self.active_ax, var_key, universe, title)
        self.fig.canvas.draw_idle()
    
    def on_release(self, event):
        if self.dragging_point is not None:
            self.update_all_surfaces()
            self.calculate_full_inference(None)
        self.dragging_point = None


# ================================================================
# EJECUCIÓN
# ================================================================
if __name__ == "__main__":
    HierarchicalFIS()