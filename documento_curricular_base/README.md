# Documento curricular base

Este proyecto contiene en LaTeX el contenido comprendido entre las páginas 25 y 80 de `../00_documento_final.pdf`. El texto, las tablas y las figuras se recuperan desde la versión más reciente de `../documento_final.docx`.

## Edición y compilación

1. Abra la carpeta `documento_curricular_base` como carpeta de trabajo en VS Code.
2. Instale las extensiones LaTeX Workshop y un ejecutable de Tectonic si todavía no están disponibles.
3. Edite `main.tex` para el formato general y `contenido.tex` para el contenido transcrito. La configuración incluida compila al guardar y abre el PDF en una pestaña.
4. También puede compilar desde la terminal con:

   ```powershell
   tectonic --synctex --keep-logs main.tex
   ```

El resultado esperado es `main.pdf`.

## Regenerar desde el DOCX

Si cambia el documento maestro, ejecute `generar_desde_docx.py` con el Python incluido en el entorno de trabajo. El script vuelve a crear `contenido.tex` y extrae las figuras correspondientes.

## Gráficos curriculares

La subcarpeta `generacion_graficos` contiene una copia autocontenida del código y de todos los datos necesarios para regenerar los gráficos de radar. Puede copiarse junto con este proyecto sin depender de archivos ubicados en la raíz original de `CLIE`. Las figuras de radar usadas por `main.tex` son fuentes TikZ incluidas mediante `\input`, no imágenes rasterizadas.
