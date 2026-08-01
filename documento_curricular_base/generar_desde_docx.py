"""Genera contenido.tex y extrae figuras desde el DOCX maestro.

El intervalo 218..975 corresponde, en la versión actual del DOCX, al contenido
que inicia en "Fundamentación del programa" y termina en "Ciberseguridad",
antes de la sección "Recursos".
"""

from pathlib import Path
from io import BytesIO
import re

from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table
from docx.oxml.ns import qn
from PIL import Image


ROOT = Path(__file__).resolve().parent
DOCX = ROOT.parent / "documento_final.docx"
OUT = ROOT / "contenido.tex"
FIGDIR = ROOT / "figuras"
START_BLOCK = 218
END_BLOCK = 975
PDF_FIGURES = {
    275: "porcTRC",
    285: "ENF",
    303: "INS",
    318: "AER",
    336: "SCF",
}


def tex_escape(value: str) -> str:
    value = value.replace("\u00a0", " ").replace("\u202f", " ").replace("\u2011", "-")
    mapping = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(mapping.get(char, char) for char in value)


def inline_text(paragraph: Paragraph) -> str:
    pieces = []
    for run in paragraph.runs:
        text = tex_escape(run.text)
        if not text:
            continue
        if run.bold:
            text = rf"\textbf{{{text}}}"
        if run.italic:
            text = rf"\textit{{{text}}}"
        if run.underline:
            text = rf"\underline{{{text}}}"
        pieces.append(text)
    return "".join(pieces) or tex_escape(paragraph.text)


def numbering_formats(document: Document):
    root = document.part.numbering_part.element
    abstract_by_num = {
        node.get(qn("w:numId")): node.find(qn("w:abstractNumId")).get(qn("w:val"))
        for node in root.findall(qn("w:num"))
    }
    result = {}
    for num_id, abstract_id in abstract_by_num.items():
        abstract = next(
            node
            for node in root.findall(qn("w:abstractNum"))
            if node.get(qn("w:abstractNumId")) == abstract_id
        )
        result[num_id] = {}
        for level in abstract.findall(qn("w:lvl")):
            fmt = level.find(qn("w:numFmt"))
            result[num_id][int(level.get(qn("w:ilvl")))] = (
                fmt.get(qn("w:val")) if fmt is not None else "bullet"
            )
    return result


def list_info(paragraph: Paragraph, formats):
    props = paragraph._p.pPr
    num = props.numPr if props is not None else None
    if num is None or num.numId is None:
        return None
    num_id = str(num.numId.val)
    level = int(num.ilvl.val) if num.ilvl is not None else 0
    fmt = formats.get(num_id, {}).get(level, "bullet")
    return num_id, level, "enumerate" if fmt != "bullet" else "itemize"


def cell_text(cell) -> str:
    parts = []
    for paragraph in cell.paragraphs:
        text = inline_text(paragraph).strip()
        if text:
            parts.append(text)
    return r"\newline ".join(parts)


def merged_cells(row):
    groups = []
    start = 0
    cells = row.cells
    while start < len(cells):
        end = start + 1
        while end < len(cells) and cells[end]._tc is cells[start]._tc:
            end += 1
        groups.append((start, end - start, cells[start]))
        start = end
    return groups


def emit_regular_table(table: Table) -> list[str]:
    cols = len(table.columns)
    if cols == 8:
        spec = r"|>{\RaggedRight\arraybackslash}p{1.25cm}|>{\RaggedRight\arraybackslash}p{5.2cm}|>{\RaggedRight\arraybackslash}p{1.65cm}|p{1.25cm}|p{1.25cm}|c|c|c|"
    else:
        spec = "|" + "l|" * cols
    out = [r"\begin{center}", r"\small", r"\begin{adjustbox}{max width=\textwidth}", rf"\begin{{tabular}}{{{spec}}}", r"\hline"]
    for row_index, row in enumerate(table.rows):
        if row_index == 0:
            out.append(r"\rowcolor{grisEncabezado}")
        elif row_index % 2 == 0:
            out.append(r"\rowcolor{azulTabla}")
        values = []
        for _, span, cell in merged_cells(row):
            value = cell_text(cell)
            if span > 1:
                values.append(rf"\multicolumn{{{span}}}{{|l|}}{{{value}}}")
            else:
                values.append(value)
        out.append(" & ".join(values) + r" \\ \hline")
    out.extend([r"\end{tabular}", r"\end{adjustbox}", r"\end{center}"])
    return out


def emit_mapping_table(table: Table) -> list[str]:
    rows = table.rows
    cols = len(table.columns)
    is_axis_profile_mapping = cell_text(rows[0].cells[0]).strip().lower() == "rasgos / ejes"
    chunk_size = 23 if len(rows) > 30 else len(rows) - 1
    out = []
    for first in range(1, len(rows), chunk_size):
        chunk = rows[first : first + chunk_size]
        spec = r"|l|p{4.6cm}|" + "c|" * max(0, cols - 2)
        if cols == 22:
            spec = r"|l|" + "c|" * (cols - 1)
        out.extend([r"\begin{center}", r"\scriptsize"])
        if is_axis_profile_mapping:
            out.append(r"\arrayrulecolor{azulTEC}")
        out.extend([r"\begin{adjustbox}{max width=\textwidth,max totalheight=.82\textheight}", rf"\begin{{tabular}}{{{spec}}}", r"\hline"])
        out.append(r"\rowcolor{azulTEC}" if is_axis_profile_mapping else r"\rowcolor{grisEncabezado}")
        header = []
        for index, cell in enumerate(rows[0].cells):
            text = cell_text(cell)
            if index >= (1 if cols == 22 else 2):
                text = rf"\rotatebox{{90}}{{\strut {text}}}"
            elif is_axis_profile_mapping and index == 0:
                text = rf"\rule{{0pt}}{{1.35cm}}{text}"
            header_cell = rf"\textbf{{{text}}}"
            if is_axis_profile_mapping:
                header_cell = rf"\textcolor{{white}}{{{header_cell}}}"
            header.append(header_cell)
        out.append(" & ".join(header) + r" \\ \hline")
        for row_index, row in enumerate(chunk):
            if is_axis_profile_mapping:
                out.append(r"\rowcolor{azulClaro}")
            elif row_index % 2 == 1:
                out.append(r"\rowcolor{azulTabla}")
            row_values = [cell_text(cell) for cell in row.cells]
            if is_axis_profile_mapping and row_values:
                row_values[0] = rf"\textcolor{{azulTEC}}{{\textbf{{{row_values[0]}}}}}"
            out.append(" & ".join(row_values) + r" \\ \hline")
        out.extend([r"\end{tabular}", r"\end{adjustbox}", r"\end{center}"])
        if is_axis_profile_mapping:
            out.append(r"\arrayrulecolor{black}")
    return out


def extract_image(document: Document, paragraph_node, block_index: int) -> Path:
    blip = paragraph_node.xpath(".//a:blip")[0]
    part = document.part.related_parts[blip.get(qn("r:embed"))]
    FIGDIR.mkdir(parents=True, exist_ok=True)
    image = Image.open(BytesIO(part.blob))
    path = FIGDIR / f"figura_{block_index}.png"
    image.save(path)
    return path


def main():
    # Evita conservar imágenes extraídas que ya no correspondan al DOCX actual.
    FIGDIR.mkdir(parents=True, exist_ok=True)
    for old_figure in FIGDIR.glob("figura_*.png"):
        old_figure.unlink()

    document = Document(DOCX)
    body = list(document.element.body.iterchildren())
    formats = numbering_formats(document)
    output = [
        "% Archivo generado desde ../documento_final.docx.",
        "% Edite el DOCX maestro o este archivo según el flujo de trabajo acordado.",
        "",
    ]
    list_stack = []
    active_num_id = None
    boxed_transversal_codes = set()
    boxed_profile_counts = {}

    def close_lists(target_depth=0):
        nonlocal list_stack
        while len(list_stack) > target_depth:
            output.append(rf"\end{{{list_stack.pop()}}}")

    block_index = START_BLOCK
    while block_index <= END_BLOCK:
        node = body[block_index]
        tag = node.tag.split("}")[-1]
        if tag == "tbl":
            close_lists()
            table = Table(node, document)
            output.extend(emit_mapping_table(table) if len(table.columns) >= 9 else emit_regular_table(table))
            output.append("")
            block_index += 1
            continue

        if tag != "p":
            block_index += 1
            continue

        paragraph = Paragraph(node, document)
        image_nodes = node.xpath(".//a:blip")
        if image_nodes:
            close_lists()
            image_block_index = block_index
            caption = ""
            if block_index + 1 <= END_BLOCK and body[block_index + 1].tag.endswith("}p"):
                next_paragraph = Paragraph(body[block_index + 1], document)
                if next_paragraph.style and next_paragraph.style.name == "Caption":
                    # Todos los captions usan un estilo uniforme; no se heredan
                    # negritas o itálicas parciales del DOCX.
                    caption = tex_escape(next_paragraph.text.strip())
                    block_index += 1
            if image_block_index in PDF_FIGURES:
                output.extend([r"\begin{figure}[H]", r"\centering"])
                graph_name = PDF_FIGURES[image_block_index]
                width = r"\textwidth" if graph_name == "porcTRC" else r".58\textwidth"
                output.append(
                    rf"\includegraphics[width={width},height=.70\textheight,keepaspectratio]"
                    rf"{{generacion_graficos/salida/{graph_name}.pdf}}"
                )
            else:
                output.extend([r"\begin{figure}[htbp]", r"\centering"])
                path = extract_image(document, node, image_block_index)
                output.append(rf"\includegraphics[width=\textwidth,height=.78\textheight,keepaspectratio]{{figuras/{path.name}}}")
            if caption:
                output.extend([
                    r"\par\vspace{2mm}",
                    rf"{{\centering\small {caption}\par}}",
                ])
            output.extend([r"\end{figure}", ""])
            block_index += 1
            continue

        text = inline_text(paragraph).strip()
        if not text:
            close_lists()
            active_num_id = None
            block_index += 1
            continue

        transversal_match = re.match(r"^\[((?:EJT|ODS|MCA)\d{2})\]\s*(.*)$", text)
        if transversal_match:
            code, definition = transversal_match.groups()
            if code not in boxed_transversal_codes:
                close_lists()
                active_num_id = None
                definition = re.sub(r"^(?:\\textbf\{\s*\}\s*)+", "", definition).strip()
                output.extend([
                    rf"\begin{{cuadrocafe}}[{code}]",
                    definition,
                    r"\end{cuadrocafe}",
                    "",
                ])
                boxed_transversal_codes.add(code)
                block_index += 1
                continue

        profile_match = re.match(
            r"^\[((?:CIB|FPH|CYD|IEE|IMM|AUT|ADD|INS|LID|SYC|IPR|AER|SCF)\d{2})\]\s*(.*)$",
            text,
        )
        if profile_match:
            code, definition = profile_match.groups()
            box_limit = 3 if code in {"LID01", "SYC01", "IPR01"} else 1
            current_count = boxed_profile_counts.get(code, 0)
            if current_count < box_limit:
                close_lists()
                active_num_id = None
                output.extend([
                    rf"\begin{{cuadroazul}}[{code}]",
                    definition.strip(),
                    r"\end{cuadroazul}",
                    "",
                ])
                boxed_profile_counts[code] = current_count + 1
                block_index += 1
                continue

        info = list_info(paragraph, formats)
        if info:
            num_id, level, environment = info
            if active_num_id != num_id:
                close_lists()
                active_num_id = num_id
            wanted_depth = level + 1
            while len(list_stack) < wanted_depth:
                list_stack.append(environment)
                output.append(rf"\begin{{{environment}}}")
            close_lists(wanted_depth)
            output.append(rf"\item {text}")
            block_index += 1
            continue

        close_lists()
        active_num_id = None
        style = paragraph.style.name if paragraph.style else "Normal"
        if block_index == START_BLOCK:
            output.append(rf"\section*{{{text}}}")
        elif style == "Heading 1":
            output.append(rf"\section*{{{text}}}")
        elif style == "Heading 2":
            output.append(rf"\subsection*{{{text}}}")
        elif style == "Heading 3":
            output.append(rf"\subsubsection*{{{text}}}")
        elif style == "Heading 4":
            output.append(rf"\paragraph{{{text}}}")
        elif style == "Caption":
            output.append(rf"\begin{{center}}\small {text}\end{{center}}")
        else:
            output.append(text + r"\par")
        output.append("")
        block_index += 1

    close_lists()
    OUT.write_text("\n".join(output) + "\n", encoding="utf-8")
    print(f"Generado: {OUT}")
    print(f"Figuras: {len(list(FIGDIR.glob('*.png')))}")


if __name__ == "__main__":
    main()
