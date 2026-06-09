import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, RadioButtons
import skfuzzy as fuzz

class InteractiveFIS:
    def __init__(self):
        # 1. Universos
        self.w_universe = np.linspace(0, 30, 401)
        self.a_universe = np.linspace(0, 1, 401)
        self.c_universe = np.linspace(0, 1, 401)
        self.s_universe = np.linspace(0, 100, 501)

        # 2. Parámetros iniciales de las funciones
        self.params = {
            'W': {
                'estrecha': [0.0, 0.0, 4.0, 8.0],
                'media': [6.0, 12.0, 20.0],
                'ancha': [18.0, 22.0, 30.0, 30.0]
            },
            'A': {
                'ninguno': [0.0, 0.0, 0.05, 0.15],
                'moderado': [0.10, 0.30, 0.55],
                'severo': [0.45, 0.65, 1.0, 1.0]
            },
            'C': {
                'truncada': [0.0, 0.0, 0.2, 0.6],
                'completa': [0.4, 0.8, 1.0, 1.0]
            }
        }
        
        # Salida S fija
        self.s_baja = fuzz.trapmf(self.s_universe, [0, 0, 20, 40])
        self.s_media = fuzz.trimf(self.s_universe, [30, 50, 70])
        self.s_alta = fuzz.trapmf(self.s_universe, [60, 80, 100, 100])

        # Configuración de la figura
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.canvas.manager.set_window_title('FIS Editor Interactivo Avanzado')
        
        # Layout de subplots
        self.ax_w = plt.subplot2grid((2, 3), (0, 0))
        self.ax_a = plt.subplot2grid((2, 3), (0, 1))
        self.ax_c = plt.subplot2grid((2, 3), (0, 2))
        self.ax_s = plt.subplot2grid((2, 3), (1, 0), colspan=3, projection='3d')
        plt.subplots_adjust(bottom=0.15, hspace=0.3, wspace=0.3)

        # Estado
        self.dragging_point = None
        self.active_ax = None
        self.surface_mode = 1.0 # Por defecto C=1 (Completa)
        
        # Widgets
        ax_btn = plt.axes([0.75, 0.03, 0.15, 0.06])
        self.btn = Button(ax_btn, 'Actualizar 3D', color='#2ecc71', hovercolor='#27ae60')
        self.btn.on_clicked(self.update_surface)

        ax_radio = plt.axes([0.1, 0.02, 0.2, 0.08], facecolor='#f0f0f0')
        self.radio = RadioButtons(ax_radio, ('C=1 (Completa)', 'C=0 (Truncada)'))
        self.radio.on_clicked(self.change_mode)

        self.setup_plots()
        
        # Eventos cruciales para la interactividad
        self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

        plt.show()

    def change_mode(self, label):
        self.surface_mode = 1.0 if 'C=1' in label else 0.0
        # No actualizar automáticamente para no congelar el arrastre si el usuario lo pulsa rápido
        print(f"Modo cambiado a C={self.surface_mode}. Pulsa 'Actualizar 3D' para ver el cambio.")

    def setup_plots(self):
        self.draw_variable(self.ax_w, 'W', self.w_universe)
        self.draw_variable(self.ax_a, 'A', self.a_universe)
        self.draw_variable(self.ax_c, 'C', self.c_universe)
        self.update_surface(None)

    def draw_variable(self, ax, var_key, universe):
        ax.clear()
        colors = ['#3498db', '#e67e22', '#e74c3c'] if var_key != 'C' else ['#9b59b6', '#2ecc71']
        for (name, p), color in zip(self.params[var_key].items(), colors):
            if len(p) == 3:
                mf = fuzz.trimf(universe, p)
                y_vals = [0, 1, 0]
            else:
                mf = fuzz.trapmf(universe, p)
                y_vals = [0, 1, 1, 0]
            
            # Dibujar la línea de la función
            ax.plot(universe, mf, label=name, lw=2, color=color, alpha=0.7)
            # Dibujar los puntos arrastrables con un gid único para identificarlos
            for i, px in enumerate(p):
                ax.plot(px, y_vals[i], 'o', color=color, markersize=8, markeredgecolor='black', 
                        alpha=0.8, picker=True, pickradius=10, gid=f"{var_key}:{name}:{i}")
        
        ax.set_title(f"Ajustar Membresía: {var_key}")
        ax.set_ylim(-0.1, 1.1)
        ax.legend(fontsize='small', loc='upper right')
        ax.grid(alpha=0.3)

    def on_press(self, event):
        if event.inaxes not in [self.ax_w, self.ax_a, self.ax_c]: return
        self.active_ax = event.inaxes
        
        # Buscar el punto más cercano al clic
        for line in self.active_ax.get_lines():
            gid = line.get_gid()
            if gid:
                # Verificar si el clic está sobre este punto
                cont, ind = line.contains(event)
                if cont:
                    self.dragging_point = gid
                    return

    def on_motion(self, event):
        if self.dragging_point is None or event.xdata is None: return
        
        var, name, idx = self.dragging_point.split(':')
        idx = int(idx)
        new_x = float(event.xdata)
        
        # Limitar desplazamiento según el universo
        limit = 30.0 if var == 'W' else 1.0
        new_x = max(0.0, min(new_x, limit))
        
        # Actualizar el valor del parámetro
        self.params[var][name][idx] = new_x
        # Mantener el orden lógico de los puntos del conjunto difuso (no se pueden cruzar)
        self.params[var][name].sort()
        
        # Redibujar inmediatamente el eje que se está modificando
        universe = getattr(self, f"{var.lower()}_universe")
        self.draw_variable(self.active_ax, var, universe)
        self.fig.canvas.draw_idle()

    def on_release(self, event):
        self.dragging_point = None

    def infer(self, w_val, a_val, c_val):
        p = self.params
        
        # Generar funciones de membresía actuales a partir de los parámetros modificados
        mf_w_e = fuzz.trapmf(self.w_universe, p['W']['estrecha'])
        mf_w_m = fuzz.trimf(self.w_universe, p['W']['media'])
        mf_w_a = fuzz.trapmf(self.w_universe, p['W']['ancha'])
        
        mf_a_n = fuzz.trapmf(self.a_universe, p['A']['ninguno'])
        mf_a_m = fuzz.trimf(self.a_universe, p['A']['moderado'])
        mf_a_s = fuzz.trapmf(self.a_universe, p['A']['severo'])
        
        mf_c_t = fuzz.trapmf(self.c_universe, p['C']['truncada'])
        mf_c_c = fuzz.trapmf(self.c_universe, p['C']['completa'])

        # Fuzzificación puntual
        mu_w_e = fuzz.interp_membership(self.w_universe, mf_w_e, w_val)
        mu_w_m = fuzz.interp_membership(self.w_universe, mf_w_m, w_val)
        mu_w_a = fuzz.interp_membership(self.w_universe, mf_w_a, w_val)
        
        mu_a_n = fuzz.interp_membership(self.a_universe, mf_a_n, a_val)
        mu_a_m = fuzz.interp_membership(self.a_universe, mf_a_m, a_val)
        mu_a_s = fuzz.interp_membership(self.a_universe, mf_a_s, a_val)
        
        mu_c_t = fuzz.interp_membership(self.c_universe, mf_c_t, c_val)

        # REGLAS DINÁMICAS:
        # 1. Lógica Base (Completa)
        r_baja = np.fmin(mu_w_e, mu_a_n)
        r_media = np.fmax(mu_w_m, np.fmin(mu_w_e, mu_a_m))
        r_alta = np.fmax(mu_w_a, mu_a_s)
        
        # 2. IMPACTO DE TRUNCAMIENTO (C=0):
        # Si está truncada, penalizamos subiendo la severidad
        # Lo que era Estrecha ahora tiene peso en Media
        r_boost_media = np.fmin(mu_c_t, mu_w_e)
        # Lo que era Media ahora tiene peso en Alta
        r_boost_alta = np.fmin(mu_c_t, mu_w_m)

        # Implicación
        out_baja = np.fmin(r_baja, self.s_baja)
        out_media = np.fmax(np.fmin(r_media, self.s_media), np.fmin(r_boost_media, self.s_media))
        out_alta = np.fmax(np.fmin(r_alta, self.s_alta), np.fmin(r_boost_alta, self.s_alta))

        # Agregación
        aggregated = np.fmax(out_baja, np.fmax(out_media, out_alta))
        
        if np.allclose(aggregated, 0): return 0
        return float(fuzz.defuzz(self.s_universe, aggregated, 'centroid'))

    def update_surface(self, event):
        # Resolución para el cálculo (25x25 es un buen compromiso velocidad/calidad)
        res = 25
        w_range = np.linspace(0, 30, res)
        a_range = np.linspace(0, 1, res)
        W, A = np.meshgrid(w_range, a_range)
        
        # Calcular S para cada punto de la malla usando el modo seleccionado (surface_mode)
        S = np.zeros_like(W)
        for i in range(res):
            for j in range(res):
                S[i,j] = self.infer(W[i,j], A[i,j], self.surface_mode)

        self.ax_s.clear()
        surf = self.ax_s.plot_surface(W, A, S, cmap='viridis', edgecolor='none', antialiased=True)
        self.ax_s.set_title(f"Interpretación de Severidad con C={self.surface_mode}")
        self.ax_s.set_xlabel("Ancho (W)")
        self.ax_s.set_ylabel("Daño (A)")
        self.ax_s.set_zlabel("Severidad (S)")
        self.ax_s.set_zlim(0, 100)
        self.fig.canvas.draw_idle()

if __name__ == "__main__":
    InteractiveFIS()