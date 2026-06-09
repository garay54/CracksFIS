"""
Sistema de Inferencia Difusa (FIS) tipo Mamdani para evaluar severidad de grietas en pavimentos.

Requisitos implementados:
1) Variables de entrada/salida y funciones de membresía según especificación.
2) Reglas R1..R8 usando operador AND=min.
3) Agregación de salidas por máximo.
4) Defuzzificación por centroide.
5) Gráficas:
   - Todas las funciones de membresía.
   - Superficie 3D S(W, A) con C=1 (Completa).
   - Superficie 3D S(W, A) con C=0 (Truncada).
6) Ejemplos de inferencia para 3 casos (leve, medio, severo).
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import skfuzzy as fuzz


# =========================
# 1) UNIVERSOS DE DISCURSO
# =========================
# Se definen mallas suficientemente finas para representar bien las funciones.
w_universe = np.linspace(0, 30, 601)   # Ancho de grieta W [mm]
a_universe = np.linspace(0, 1, 601)    # Daño adyacente A [0,1]
c_universe = np.linspace(0, 1, 601)    # Completitud C [0,1]
s_universe = np.linspace(0, 100, 1001) # Severidad S [0,100]


# ===================================
# 2) FUNCIONES DE MEMBRESÍA DEL SISTEMA
# ===================================
# Entrada W
w_estrecha = fuzz.trapmf(w_universe, [0, 0, 4, 8])
w_media = fuzz.trimf(w_universe, [6, 12, 20])
w_ancha = fuzz.trapmf(w_universe, [18, 22, 30, 30])

# Entrada A
a_ninguno = fuzz.trapmf(a_universe, [0, 0, 0.05, 0.15])
a_moderado = fuzz.trimf(a_universe, [0.10, 0.30, 0.55])
a_severo = fuzz.trapmf(a_universe, [0.45, 0.65, 1, 1])

# Entrada C
c_truncada = fuzz.trapmf(c_universe, [0, 0, 0.2, 0.6])
c_completa = fuzz.trapmf(c_universe, [0.4, 0.8, 1, 1])

# Salida S
s_baja = fuzz.trapmf(s_universe, [0, 0, 20, 40])
s_media = fuzz.trimf(s_universe, [30, 50, 70])
s_alta = fuzz.trapmf(s_universe, [60, 80, 100, 100])


def infer_severidad_mamdani(w_val: float, a_val: float, c_val: float):
    """
    Ejecuta la inferencia Mamdani para una muestra (W, A, C).

    Parámetros:
        w_val: ancho de grieta en mm (0..30)
        a_val: daño adyacente normalizado (0..1)
        c_val: completitud (0..1)

    Retorna:
        s_crisp: valor crisp de severidad (defuzzificación centroide).
        aggregated: función de salida agregada sobre s_universe.
        activaciones: diccionario con activaciones de reglas R1..R8.
    """
    # -------------------------
    # 2.1) Fuzzificación puntual
    # -------------------------
    # Se evalúan los grados de pertenencia de cada entrada en sus conjuntos.
    mu_w_estrecha = fuzz.interp_membership(w_universe, w_estrecha, w_val)
    mu_w_media = fuzz.interp_membership(w_universe, w_media, w_val)
    mu_w_ancha = fuzz.interp_membership(w_universe, w_ancha, w_val)

    mu_a_ninguno = fuzz.interp_membership(a_universe, a_ninguno, a_val)
    mu_a_moderado = fuzz.interp_membership(a_universe, a_moderado, a_val)
    mu_a_severo = fuzz.interp_membership(a_universe, a_severo, a_val)

    mu_c_truncada = fuzz.interp_membership(c_universe, c_truncada, c_val)
    # Nota: mu_c_completa no se usa en reglas explícitas, pero se deja por claridad.
    _ = fuzz.interp_membership(c_universe, c_completa, c_val)

    # ------------------------
    # 2.2) Evaluación de reglas
    # ------------------------
    # AND = mínimo, conforme al requisito.
    # R1: SI W es Estrecha Y A es Ninguno ENTONCES S es Baja
    r1 = np.fmin(mu_w_estrecha, mu_a_ninguno)
    # R2: SI W es Media ENTONCES S es Media
    r2 = mu_w_media
    # R3: SI W es Ancha ENTONCES S es Alta
    r3 = mu_w_ancha
    # R4: SI W es Estrecha Y A es Moderado ENTONCES S es Media
    r4 = np.fmin(mu_w_estrecha, mu_a_moderado)
    # R5: SI W es Estrecha Y A es Severo ENTONCES S es Alta
    r5 = np.fmin(mu_w_estrecha, mu_a_severo)
    # R6: SI W es Media Y A es Severo ENTONCES S es Alta
    r6 = np.fmin(mu_w_media, mu_a_severo)
    # R7: SI C es Truncada Y W es Ancha ENTONCES S es Alta
    r7 = np.fmin(mu_c_truncada, mu_w_ancha)
    # R8: SI C es Truncada Y W es Estrecha Y A es Ninguno ENTONCES S es Baja
    r8 = np.fmin(np.fmin(mu_c_truncada, mu_w_estrecha), mu_a_ninguno)

    activaciones = {
        "R1": r1,
        "R2": r2,
        "R3": r3,
        "R4": r4,
        "R5": r5,
        "R6": r6,
        "R7": r7,
        "R8": r8,
    }

    # -----------------------------------
    # 2.3) Implicación y agregación Mamdani
    # -----------------------------------
    # Implicación por recorte (min): salida_regla = min(activación, consecuente).
    out_r1 = np.fmin(r1, s_baja)
    out_r2 = np.fmin(r2, s_media)
    out_r3 = np.fmin(r3, s_alta)
    out_r4 = np.fmin(r4, s_media)
    out_r5 = np.fmin(r5, s_alta)
    out_r6 = np.fmin(r6, s_alta)
    out_r7 = np.fmin(r7, s_alta)
    out_r8 = np.fmin(r8, s_baja)

    # Agregación por máximo, conforme al requisito.
    aggregated = np.fmax(
        np.fmax(np.fmax(out_r1, out_r2), np.fmax(out_r3, out_r4)),
        np.fmax(np.fmax(out_r5, out_r6), np.fmax(out_r7, out_r8)),
    )

    # -----------------------------------
    # 2.4) Defuzzificación (centroide)
    # -----------------------------------
    # Si por alguna razón no hay activación, se devuelve 0 para evitar fallo numérico.
    if np.allclose(aggregated, 0):
        s_crisp = 0.0
    else:
        s_crisp = float(fuzz.defuzz(s_universe, aggregated, "centroid"))

    return s_crisp, aggregated, activaciones


def plot_membership_functions():
    """Grafica todas las funciones de membresía de entradas y salida."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle("Funciones de membresía del FIS de severidad de grietas", fontsize=14)

    # W
    ax = axes[0, 0]
    ax.plot(w_universe, w_estrecha, label="Estrecha", linewidth=2)
    ax.plot(w_universe, w_media, label="Media", linewidth=2)
    ax.plot(w_universe, w_ancha, label="Ancha", linewidth=2)
    ax.set_title("Entrada W: Ancho de grieta (mm)")
    ax.set_xlabel("W [mm]")
    ax.set_ylabel("Membresía")
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.3)
    ax.legend()

    # A
    ax = axes[0, 1]
    ax.plot(a_universe, a_ninguno, label="Ninguno", linewidth=2)
    ax.plot(a_universe, a_moderado, label="Moderado", linewidth=2)
    ax.plot(a_universe, a_severo, label="Severo", linewidth=2)
    ax.set_title("Entrada A: Daño adyacente")
    ax.set_xlabel("A [0-1]")
    ax.set_ylabel("Membresía")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.3)
    ax.legend()

    # C
    ax = axes[1, 0]
    ax.plot(c_universe, c_truncada, label="Truncada", linewidth=2)
    ax.plot(c_universe, c_completa, label="Completa", linewidth=2)
    ax.set_title("Entrada C: Completitud")
    ax.set_xlabel("C [0-1]")
    ax.set_ylabel("Membresía")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.3)
    ax.legend()

    # S
    ax = axes[1, 1]
    ax.plot(s_universe, s_baja, label="Baja", linewidth=2)
    ax.plot(s_universe, s_media, label="Media", linewidth=2)
    ax.plot(s_universe, s_alta, label="Alta", linewidth=2)
    ax.set_title("Salida S: Severidad")
    ax.set_xlabel("S [0-100]")
    ax.set_ylabel("Membresía")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1.05)
    ax.grid(alpha=0.3)
    ax.legend()

    plt.tight_layout(rect=[0, 0.02, 1, 0.96])


def compute_surface(c_fixed: float, n_w: int = 61, n_a: int = 61):
    """
    Calcula la superficie S(W, A) para un valor fijo de C.

    Retorna:
        Wg, Ag, Sg: mallas para graficar superficie 3D.
    """
    w_vals = np.linspace(0, 30, n_w)
    a_vals = np.linspace(0, 1, n_a)
    Wg, Ag = np.meshgrid(w_vals, a_vals)
    Sg = np.zeros_like(Wg, dtype=float)

    # Se evalúa el FIS en cada punto de la malla.
    for i in range(Wg.shape[0]):
        for j in range(Wg.shape[1]):
            s_val, _, _ = infer_severidad_mamdani(Wg[i, j], Ag[i, j], c_fixed)
            Sg[i, j] = s_val

    return Wg, Ag, Sg


def plot_surface(Wg, Ag, Sg, title: str):
    """Grafica una superficie 3D de severidad."""
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(Wg, Ag, Sg, cmap=cm.viridis, linewidth=0, antialiased=True)
    ax.set_title(title)
    ax.set_xlabel("W [mm]")
    ax.set_ylabel("A [0-1]")
    ax.set_zlabel("S [0-100]")
    fig.colorbar(surf, shrink=0.7, aspect=12, label="Severidad S")
    plt.tight_layout()


def print_inference_examples():
    """Muestra 3 ejemplos: leve, medio y severo."""
    casos = [
        ("Caso leve", {"W": 3.0, "A": 0.04, "C": 1.0}),
        ("Caso medio", {"W": 12.0, "A": 0.30, "C": 1.0}),
        ("Caso severo", {"W": 24.0, "A": 0.80, "C": 0.0}),
    ]

    print("\n=== Ejemplos de inferencia (Mamdani) ===")
    for nombre, vals in casos:
        s_out, _, activaciones = infer_severidad_mamdani(vals["W"], vals["A"], vals["C"])
        print(f"\n{nombre}:")
        print(f"  Entradas -> W={vals['W']:.2f} mm, A={vals['A']:.2f}, C={vals['C']:.2f}")
        print(f"  Severidad defuzzificada S = {s_out:.2f}")
        print("  Activación de reglas:")
        for rk, rv in activaciones.items():
            print(f"    {rk}: {rv:.3f}")


def main():
    """Punto principal de ejecución."""
    # A) Funciones de membresía
    plot_membership_functions()

    # B) Superficie S(W, A) con C = 1 (Completa)
    Wg_c1, Ag_c1, Sg_c1 = compute_surface(c_fixed=1.0)
    plot_surface(Wg_c1, Ag_c1, Sg_c1, "Superficie de severidad S(W, A) con C = 1 (Completa)")

    # C) Superficie S(W, A) con C = 0 (Truncada)
    Wg_c0, Ag_c0, Sg_c0 = compute_surface(c_fixed=0.0)
    plot_surface(Wg_c0, Ag_c0, Sg_c0, "Superficie de severidad S(W, A) con C = 0 (Truncada)")

    # D) Casos de inferencia
    print_inference_examples()

    # Muestra todas las gráficas.
    plt.show()

    # Interpretación breve solicitada por el enunciado.
    print("\n=== Interpretación breve de las superficies ===")
    print(
        "1) En general, al aumentar W (ancho de grieta), la severidad S tiende a subir "
        "por la influencia de las reglas R2 y R3."
    )
    print(
        "2) Para W estrecha, el daño adyacente A modula la salida: A bajo favorece S baja, "
        "mientras A severo empuja S a alta (R1, R4, R5)."
    )
    print(
        "3) Con C=0 (truncada), se activan más reglas que pueden mantener o elevar severidad "
        "en zonas críticas (R7 y R8), produciendo diferencias locales respecto a C=1."
    )


if __name__ == "__main__":
    main()
