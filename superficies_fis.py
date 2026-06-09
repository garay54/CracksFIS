import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import skfuzzy as fuzz

class SuperficiesFIS:
    def __init__(self):
        # ============================================================
        # 1. UNIVERSOS DE DISCURSO
        # ============================================================
        self.w_universe = np.linspace(0, 30, 301)
        self.l_universe = np.linspace(0, 200, 401)
        self.c_universe = np.linspace(0, 1, 201)
        self.a_universe = np.linspace(0, 1, 201)
        self.sg_universe = np.linspace(0, 100, 201)
        self.sv_universe = np.linspace(0, 100, 201)
        self.sf_universe = np.linspace(0, 100, 201)
        
        # ============================================================
        # 2. PARÁMETROS DE FUNCIONES DE MEMBRESÍA
        # ============================================================
        self.params = {
            'W': {'pequeña': [0.0, 0.0, 3.0, 8.0], 'media': [5.0, 12.0, 18.0], 'grande': [15.0, 22.0, 30.0, 30.0]},
            'L': {'corta': [0.0, 0.0, 30.0, 60.0], 'media': [40.0, 80.0, 120.0], 'larga': [100.0, 150.0, 200.0, 200.0]},
            'C': {'truncada': [0.0, 0.0, 0.2, 0.4], 'parcial': [0.3, 0.5, 0.7], 'completa': [0.6, 0.8, 1.0, 1.0]},
            'A': {'superficial': [0.0, 0.0, 0.2, 0.4], 'moderada': [0.3, 0.5, 0.7], 'profunda': [0.6, 0.8, 1.0, 1.0]},
            'SG': {'baja': [0, 0, 20, 40], 'media': [30, 50, 70], 'alta': [60, 80, 100, 100]},
            'SV': {'baja': [0, 0, 20, 40], 'media': [30, 50, 70], 'alta': [60, 80, 100, 100]},
            'SF': {'leve': [0, 0, 20, 35], 'moderada': [25, 50, 75], 'critica': [65, 85, 100, 100]}
        }
        
        # ============================================================
        # 3. CONFIGURACIÓN DE LA FIGURA
        # ============================================================
        self.fig = plt.figure(figsize=(18, 6))
        self.fig.canvas.manager.set_window_title('Superficies de Control FIS')
        
        # Subplots para las superficies 3D
        self.ax_surf1 = self.fig.add_subplot(131, projection='3d')
        self.ax_surf2 = self.fig.add_subplot(132, projection='3d')
        self.ax_surf3 = self.fig.add_subplot(133, projection='3d')
        
        plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.2, wspace=0.3)
        
        # Vistas iniciales (elevación, azimut)
        self.init_elev = 30
        self.init_azim = -60

        # Botón de reinicio de vista
        ax_btn_reset = plt.axes([0.45, 0.05, 0.1, 0.05])
        self.btn_reset = Button(ax_btn_reset, 'Resetear Posición', color='#3498db', hovercolor='#2980b9')
        self.btn_reset.label.set_color('white')
        self.btn_reset.label.set_fontweight('bold')
        self.btn_reset.on_clicked(self.reset_views)

        # Generar y dibujar las superficies
        print("Calculando superficies... Por favor espere.")
        self.draw_surfaces()
        
        # Forzar la vista inicial
        self.reset_views(None)
        
        print("Superficies listas para visualizar.")
        plt.show()

    def reset_views(self, event):
        """Reinicia la rotación de las 3 superficies a su posición original"""
        self.ax_surf1.view_init(elev=self.init_elev, azim=self.init_azim)
        self.ax_surf2.view_init(elev=self.init_elev, azim=self.init_azim)
        self.ax_surf3.view_init(elev=self.init_elev, azim=self.init_azim)
        self.fig.canvas.draw_idle()

    def get_mf(self, universe, params):
        if len(params) == 3:
            return fuzz.trimf(universe, params)
        else:
            return fuzz.trapmf(universe, params)

    def infer_fis1(self, w_val, l_val):
        p = self.params
        
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
        
        mf_sg_b = self.get_mf(self.sg_universe, p['SG']['baja'])
        mf_sg_m = self.get_mf(self.sg_universe, p['SG']['media'])
        mf_sg_a = self.get_mf(self.sg_universe, p['SG']['alta'])
        
        r1 = np.fmin(mu_w_p, mu_l_c)
        r2 = np.fmin(mu_w_p, mu_l_m)
        r3 = np.fmin(mu_w_p, mu_l_l)
        r4 = np.fmin(mu_w_m, mu_l_c)
        r5 = np.fmin(mu_w_m, mu_l_m)
        r6 = np.fmin(mu_w_m, mu_l_l)
        r7 = np.fmin(mu_w_g, mu_l_c)
        r8 = np.fmin(mu_w_g, mu_l_m)
        r9 = np.fmin(mu_w_g, mu_l_l)
        
        out_baja = np.fmin(np.fmax(np.fmax(r1, r2), r4), mf_sg_b)
        out_media = np.fmin(np.fmax(np.fmax(r3, r5), r7), mf_sg_m)
        out_alta = np.fmin(np.fmax(np.fmax(r6, r8), r9), mf_sg_a)
        
        aggregated = np.fmax(out_baja, np.fmax(out_media, out_alta))
        
        if np.allclose(aggregated, 0):
            return 0.0
        return float(fuzz.defuzz(self.sg_universe, aggregated, 'centroid'))

    def infer_fis2(self, c_val, a_val):
        p = self.params
        
        mf_c_t = self.get_mf(self.c_universe, p['C']['truncada'])
        mf_c_p = self.get_mf(self.c_universe, p['C']['parcial'])
        mf_c_c = self.get_mf(self.c_universe, p['C']['completa'])
        
        mf_a_s = self.get_mf(self.a_universe, p['A']['superficial'])
        mf_a_m = self.get_mf(self.a_universe, p['A']['moderada'])
        mf_a_p = self.get_mf(self.a_universe, p['A']['profunda'])
        
        mu_c_t = fuzz.interp_membership(self.c_universe, mf_c_t, c_val)
        mu_c_p = fuzz.interp_membership(self.c_universe, mf_c_p, c_val)
        mu_c_c = fuzz.interp_membership(self.c_universe, mf_c_c, c_val)
        
        mu_a_s = fuzz.interp_membership(self.a_universe, mf_a_s, a_val)
        mu_a_m = fuzz.interp_membership(self.a_universe, mf_a_m, a_val)
        mu_a_p = fuzz.interp_membership(self.a_universe, mf_a_p, a_val)
        
        mf_sv_b = self.get_mf(self.sv_universe, p['SV']['baja'])
        mf_sv_m = self.get_mf(self.sv_universe, p['SV']['media'])
        mf_sv_a = self.get_mf(self.sv_universe, p['SV']['alta'])
        
        r1 = np.fmin(mu_c_c, mu_a_s)
        r2 = np.fmin(mu_c_c, mu_a_m)
        r3 = np.fmin(mu_c_c, mu_a_p)
        r4 = np.fmin(mu_c_p, mu_a_s)
        r5 = np.fmin(mu_c_p, mu_a_m)
        r6 = np.fmin(mu_c_p, mu_a_p)
        r7 = np.fmin(mu_c_t, mu_a_s)
        r8 = np.fmin(mu_c_t, mu_a_m)
        r9 = np.fmin(mu_c_t, mu_a_p)
        
        out_baja = np.fmin(np.fmax(r1, r4), mf_sv_b)
        out_media = np.fmin(np.fmax(np.fmax(r2, r5), r7), mf_sv_m)
        out_alta = np.fmin(np.fmax(np.fmax(np.fmax(r3, r6), r8), r9), mf_sv_a)
        
        aggregated = np.fmax(out_baja, np.fmax(out_media, out_alta))
        
        if np.allclose(aggregated, 0):
            return 0.0
        return float(fuzz.defuzz(self.sv_universe, aggregated, 'centroid'))

    def infer_fis3(self, sg_val, sv_val):
        p = self.params
        
        mf_sg_b = self.get_mf(self.sg_universe, p['SG']['baja'])
        mf_sg_m = self.get_mf(self.sg_universe, p['SG']['media'])
        mf_sg_a = self.get_mf(self.sg_universe, p['SG']['alta'])
        
        mf_sv_b = self.get_mf(self.sv_universe, p['SV']['baja'])
        mf_sv_m = self.get_mf(self.sv_universe, p['SV']['media'])
        mf_sv_a = self.get_mf(self.sv_universe, p['SV']['alta'])
        
        mu_sg_b = fuzz.interp_membership(self.sg_universe, mf_sg_b, sg_val)
        mu_sg_m = fuzz.interp_membership(self.sg_universe, mf_sg_m, sg_val)
        mu_sg_a = fuzz.interp_membership(self.sg_universe, mf_sg_a, sg_val)
        
        mu_sv_b = fuzz.interp_membership(self.sv_universe, mf_sv_b, sv_val)
        mu_sv_m = fuzz.interp_membership(self.sv_universe, mf_sv_m, sv_val)
        mu_sv_a = fuzz.interp_membership(self.sv_universe, mf_sv_a, sv_val)
        
        mf_sf_l = self.get_mf(self.sf_universe, p['SF']['leve'])
        mf_sf_m = self.get_mf(self.sf_universe, p['SF']['moderada'])
        mf_sf_c = self.get_mf(self.sf_universe, p['SF']['critica'])
        
        r1 = np.fmin(mu_sg_b, mu_sv_b)
        r2 = np.fmin(mu_sg_b, mu_sv_m)
        r3 = np.fmin(mu_sg_b, mu_sv_a)
        r4 = np.fmin(mu_sg_m, mu_sv_b)
        r5 = np.fmin(mu_sg_m, mu_sv_m)
        r6 = np.fmin(mu_sg_m, mu_sv_a)
        r7 = np.fmin(mu_sg_a, mu_sv_b)
        r8 = np.fmin(mu_sg_a, mu_sv_m)
        r9 = np.fmin(mu_sg_a, mu_sv_a)
        
        out_leve = np.fmin(np.fmax(np.fmax(r1, r2), r4), mf_sf_l)
        out_moderada = np.fmin(np.fmax(np.fmax(r3, r5), r7), mf_sf_m)
        out_critica = np.fmin(np.fmax(np.fmax(r6, r8), r9), mf_sf_c)
        
        aggregated = np.fmax(out_leve, np.fmax(out_moderada, out_critica))
        
        if np.allclose(aggregated, 0):
            return 0.0
        return float(fuzz.defuzz(self.sf_universe, aggregated, 'centroid'))

    def draw_surfaces(self):
        """Calcula y dibuja las superficies 3D"""
        res = 30 # Resolución (mayor = más suave pero más lento)
        
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
        self.ax_surf1.set_title('FIS 1: Severidad Geométrica', fontsize=10, fontweight='bold')
        self.ax_surf1.set_xlabel('Anchura (W)', fontsize=9)
        self.ax_surf1.set_ylabel('Longitud (L)', fontsize=9)
        self.ax_surf1.set_zlabel('SG', fontsize=9)
        
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
        self.ax_surf2.set_title('FIS 2: Severidad Visual', fontsize=10, fontweight='bold')
        self.ax_surf2.set_xlabel('Completitud (C)', fontsize=9)
        self.ax_surf2.set_ylabel('Apariencia (A)', fontsize=9)
        self.ax_surf2.set_zlabel('SV', fontsize=9)
        
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
        self.ax_surf3.set_title('FIS 3: Severidad Final', fontsize=10, fontweight='bold')
        self.ax_surf3.set_xlabel('SG', fontsize=9)
        self.ax_surf3.set_ylabel('SV', fontsize=9)
        self.ax_surf3.set_zlabel('SF', fontsize=9)

if __name__ == "__main__":
    app = SuperficiesFIS()
