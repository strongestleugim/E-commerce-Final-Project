import shutil
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", W_NS)


def w_tag(name: str) -> str:
    return f"{{{W_NS}}}{name}"


def ensure_child(parent: ET.Element, name: str) -> ET.Element:
    child = parent.find(w_tag(name))
    if child is None:
        child = ET.SubElement(parent, w_tag(name))
    return child


def set_attr(element: ET.Element, name: str, value: str) -> None:
    element.set(w_tag(name), value)


def normalize_table(tbl: ET.Element) -> None:
    tbl_pr = ensure_child(tbl, "tblPr")

    tbl_layout = ensure_child(tbl_pr, "tblLayout")
    set_attr(tbl_layout, "type", "autofit")

    cell_mar = tbl_pr.find(w_tag("tblCellMar"))
    if cell_mar is None:
        cell_mar = ET.SubElement(tbl_pr, w_tag("tblCellMar"))
    for side in ("top", "left", "bottom", "right"):
        side_el = cell_mar.find(w_tag(side))
        if side_el is None:
            side_el = ET.SubElement(cell_mar, w_tag(side))
        set_attr(side_el, "w", "80")
        set_attr(side_el, "type", "dxa")

    for tr in tbl.findall(w_tag("tr")):
        tr_pr = tr.find(w_tag("trPr"))
        if tr_pr is None:
            tr_pr = ET.Element(w_tag("trPr"))
            tr.insert(0, tr_pr)

        for tr_height in list(tr_pr.findall(w_tag("trHeight"))):
            tr_pr.remove(tr_height)

        cant_split = tr_pr.find(w_tag("cantSplit"))
        if cant_split is not None:
            tr_pr.remove(cant_split)

    for tc in tbl.findall(f".//{w_tag('tc')}"):
        tc_pr = tc.find(w_tag("tcPr"))
        if tc_pr is None:
            tc_pr = ET.Element(w_tag("tcPr"))
            tc.insert(0, tc_pr)

        tc_mar = tc_pr.find(w_tag("tcMar"))
        if tc_mar is None:
            tc_mar = ET.SubElement(tc_pr, w_tag("tcMar"))
        for side in ("top", "left", "bottom", "right"):
            side_el = tc_mar.find(w_tag(side))
            if side_el is None:
                side_el = ET.SubElement(tc_mar, w_tag(side))
            set_attr(side_el, "w", "80")
            set_attr(side_el, "type", "dxa")

        valign = tc_pr.find(w_tag("vAlign"))
        if valign is None:
            valign = ET.SubElement(tc_pr, w_tag("vAlign"))
        set_attr(valign, "val", "center")

        for p in tc.findall(w_tag("p")):
            p_pr = p.find(w_tag("pPr"))
            if p_pr is None:
                p_pr = ET.Element(w_tag("pPr"))
                p.insert(0, p_pr)

            spacing = p_pr.find(w_tag("spacing"))
            if spacing is None:
                spacing = ET.SubElement(p_pr, w_tag("spacing"))
            set_attr(spacing, "before", "0")
            set_attr(spacing, "after", "0")
            set_attr(spacing, "line", "240")
            set_attr(spacing, "lineRule", "auto")


def main() -> None:
    source = Path(r"C:\Users\Jerico\Downloads\CyberTechies_Chapter1-3_LATEST.docx")
    output = Path(r"C:\Users\Jerico\Documents\New project\output\doc\CyberTechies_Chapter1-3_tables-fixed.docx")
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, output)

    with zipfile.ZipFile(output, "r") as zf:
        files = {name: zf.read(name) for name in zf.namelist()}

    root = ET.fromstring(files["word/document.xml"])
    for tbl in root.findall(f".//{w_tag('tbl')}"):
        normalize_table(tbl)
    files["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in files.items():
            zf.writestr(name, data)


if __name__ == "__main__":
    main()
