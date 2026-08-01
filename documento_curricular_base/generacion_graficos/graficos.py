"""Genera los gráficos curriculares a partir de los datos locales."""

from pathlib import Path

import pandas as pd

import funciones as fun


BASE = Path(__file__).resolve().parent
DATOS = BASE / "datos"
SALIDA = BASE / "salida"
SALIDA.mkdir(parents=True, exist_ok=True)
for archivo_anterior in SALIDA.iterdir():
    if archivo_anterior.is_file() and archivo_anterior.suffix.lower() in {".pdf", ".png"}:
        archivo_anterior.unlink()

saberes = pd.read_csv(DATOS / "saberes.csv")
areas = pd.read_csv(DATOS / "areas.csv")

list_trc = ["CIB", "FPH", "CYD", "IEE", "IMM", "AUT", "ADD"]
trc = areas[areas["codArea"].isin(list_trc)]
cat_trc = trc["codArea"].to_list()
val_trc = trc["porcTRC"].to_list()

list_enf = ["CIB", "FPH", "CYD", "IEE", "IMM", "AUT", "ADD", "ENF"]
enf = areas[areas["codArea"].isin(list_enf)]
cat_enf = enf["codArea"].to_list()
val_enf = enf["porcENF"].to_list()

fun.radar("TRC", areas, cat_trc, val_trc, "", 14, 18, 20, 5, 30, SALIDA)
fun.multiradar(list_trc, saberes, areas, "porcTRC", 10, 12, 12, 4, 20, SALIDA)
fun.radar_saberes("INS", saberes, areas, "porcINS", 14, 18, 12, 3, 30, SALIDA)
fun.radar_saberes("AER", saberes, areas, "porcAER", 14, 18, 12, 3, 30, SALIDA)
fun.radar_saberes("SCF", saberes, areas, "porcSCF", 14, 18, 12, 3, 30, SALIDA)
fun.radar("ENF", areas, cat_enf, val_enf, "", 14, 18, 25, 5, 30, SALIDA)

print(f"Gráficos PDF vectoriales generados en: {SALIDA}")
