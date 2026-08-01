"""Funciones de Matplotlib para generar los gráficos curriculares."""

from pathlib import Path
import textwrap

import numpy as np
from matplotlib import pyplot as plt


def radar_clie(ax, cat, val, title, fontsize, tfontsize, rpmax, mult, textw):
    valores = list(val)
    numero_categorias = len(cat)
    valores += valores[:1]
    angulos = np.linspace(0, 2 * np.pi, numero_categorias, endpoint=False).tolist()
    angulos += angulos[:1]

    ax.plot(angulos, valores, linewidth=2, linestyle="solid", color="teal")
    ax.fill(angulos, valores, color="teal", alpha=0.4)
    ax.set_ylim(0, rpmax)
    ax.set_rlabel_position(0)

    marcas = list(range(mult, rpmax + 1, mult))
    etiquetas = [f"{numero}%" for numero in marcas]
    ax.set_yticks(marcas, etiquetas, color="grey", size=fontsize)
    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels([])

    for angulo, etiqueta in zip(angulos[:-1], cat):
        grados = np.degrees(angulo)
        if 90 <= grados <= 270:
            alineacion = "right"
            rotacion = grados + 180
        else:
            alineacion = "left"
            rotacion = grados
        ax.text(
            angulo,
            ax.get_ylim()[1] * 0.4,
            textwrap.fill(str(etiqueta), width=int(textw)),
            size=fontsize,
            horizontalalignment=alineacion,
            verticalalignment="top",
            rotation=rotacion,
            rotation_mode="anchor",
        )

    ax.set_title(textwrap.fill(title, width=tfontsize * 4), size=tfontsize, color="blue", y=1.1)
    ax.grid(color="grey", linestyle="dashed", linewidth=0.5)
    ax.spines["polar"].set_visible(False)
    ax.set_facecolor("#f7f7f7")


def guardar(figura, nombre, salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    # Se conserva el tamaño completo del lienzo. Un recorte "tight" produciría
    # cajas distintas según la longitud de las etiquetas y LaTeX escalaría los
    # círculos a diámetros diferentes.
    figura.savefig(salida / f"{nombre}.pdf")
    plt.close(figura)


def multiradar(lista, saberes, areas, columna_porc, fontsize, tfontsize, rpmax, mult, textw, salida):
    figura = plt.figure(figsize=(15, 13.5))
    cuadricula = figura.add_gridspec(3, 3)
    posiciones = [
        (0, 0), (0, 1), (0, 2),
        (1, 0), (1, 1), (1, 2),
        (2, 1),
    ]
    ejes = [
        figura.add_subplot(cuadricula[fila, columna], projection="polar")
        for fila, columna in posiciones[:len(lista)]
    ]
    for area, eje in zip(lista, ejes):
        nombre = areas[areas["codArea"] == area].nombre.item()
        saberes_area = saberes[saberes["codArea"] == area]
        categorias = saberes_area["nombre"].to_list()
        valores = saberes_area[columna_porc].to_list()
        radar_clie(eje, categorias, valores, nombre, fontsize, tfontsize, rpmax, mult, textw)
    figura.tight_layout(pad=0.6, w_pad=0.2, h_pad=0.7)
    guardar(figura, columna_porc, salida)


def radar(nombre, areas, cat, val, title, fontsize, tfontsize, rpmax, mult, textw, salida):
    nombres = areas[areas["codArea"].isin(cat)]["nombre"]
    figura, eje = plt.subplots(subplot_kw=dict(projection="polar"), figsize=(10, 10))
    radar_clie(eje, nombres, val, title, fontsize, tfontsize, rpmax, mult, textw)
    guardar(figura, nombre, salida)


def radar_saberes(nombre, saberes, areas, columna_porc, fontsize, tfontsize, rpmax, mult, textw, salida):
    saberes_area = saberes[saberes["codArea"] == nombre]
    categorias = saberes_area["nombre"].to_list()
    valores = saberes_area[columna_porc].to_list()
    figura, eje = plt.subplots(subplot_kw=dict(projection="polar"), figsize=(10, 10))
    radar_clie(eje, categorias, valores, "", fontsize, tfontsize, rpmax, mult, textw)
    guardar(figura, nombre, salida)
