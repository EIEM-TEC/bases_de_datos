# Generación autocontenida de gráficos

Esta carpeta contiene el generador y todas sus entradas:

- `graficos.py`: flujo principal con Matplotlib.
- `funciones.py`: funciones de los gráficos de radar.
- `datos/areas.csv`: nombres y porcentajes por área.
- `datos/saberes.csv`: saberes y porcentajes por programa.
- `requirements.txt`: dependencias de Python.
- `salida/`: gráficos PDF vectoriales usados directamente por Tectonic.

Las rutas se calculan desde la ubicación de `graficos.py`; por eso la carpeta
puede moverse sin cambiar rutas internas.

## Generar los gráficos

```powershell
python graficos.py
```

La ejecución genera `TRC`, `porcTRC`, `INS`, `AER`, `SCF` y `ENF` en PDF
vectorial. LaTeX incorpora directamente esos mismos archivos.
