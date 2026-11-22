from __future__ import annotations

from pathlib import Path

from lxml import etree

from pdf.pdf_reader import PDFDocument, PDFPage


# Elements whose text is not article prose.
_SKIP_TAGS = {"ref-list", "inline-formula", "disp-formula", "tex-math", "graphic", "object-id"}


def _local(tag) -> str:
    return etree.QName(tag).localname if isinstance(tag, str) else ""


def _text(element) -> str:
    parts: list[str] = []

    def walk(node):
        if _local(node.tag) in _SKIP_TAGS:
            if node.tail:
                parts.append(node.tail)
            return
        if node.text:
            parts.append(node.text)
        for child in node:
            walk(child)
        if node is not element and node.tail:
            parts.append(node.tail)

    walk(element)
    return " ".join(" ".join(parts).split())


class JATSReader:
    """Read a JATS/NLM article XML (PMC, Europe PMC) into the PDFDocument shape.

    There are no pages in XML, so each top-level unit becomes one "page":
    front matter (title, abstract), every top-level body section, the figure /
    table captions, and the back matter (data availability, acknowledgements).
    The reference list is dropped.
    """

    def read(self, path: str | Path) -> PDFDocument:
        path = Path(path)
        parser = etree.XMLParser(recover=True, resolve_entities=False, no_network=True, huge_tree=True)
        root = etree.parse(str(path), parser).getroot()

        blocks: list[str] = []

        title = root.find(".//{*}article-meta//{*}article-title")
        if title is None:
            title = root.find(".//article-meta//article-title")
        doi = None
        for article_id in root.iter():
            if _local(article_id.tag) == "article-id" and article_id.get("pub-id-type") == "doi":
                doi = (article_id.text or "").strip()
                break
        journal = next((_text(e) for e in root.iter() if _local(e.tag) == "journal-title"), "")
        authors = []
        for contrib in root.iter():
            if _local(contrib.tag) == "contrib" and contrib.get("contrib-type") == "author":
                surname = next((e.text for e in contrib.iter() if _local(e.tag) == "surname"), None)
                if surname:
                    authors.append(surname.strip())
        year = next(
            (e.text for e in root.iter() if _local(e.tag) == "year" and _local(e.getparent().tag) == "pub-date"),
            None,
        )
        head = [
            f"TITLE: {_text(title) if title is not None else ''}",
            f"AUTHORS: {', '.join(authors)}",
            f"JOURNAL: {journal} {year or ''}".strip(),
            f"DOI: {doi or ''}",
        ]
        for abstract in root.iter():
            if _local(abstract.tag) == "abstract":
                head.append("ABSTRACT: " + _text(abstract))
        # PLOS / RSOS put the data availability statement in custom-meta.
        for meta in root.iter():
            if _local(meta.tag) == "custom-meta":
                name = next((_text(c) for c in meta if _local(c.tag) == "meta-name"), "")
                value = next((_text(c) for c in meta if _local(c.tag) == "meta-value"), "")
                if value and "availab" in name.lower():
                    head.append(f"{name.upper()}: {value}")
        blocks.append("\n".join(head))

        body = next((e for e in root.iter() if _local(e.tag) == "body"), None)
        if body is not None:
            loose: list[str] = []
            for child in body:
                name = _local(child.tag)
                if name == "sec":
                    sec_title = next((c for c in child if _local(c.tag) == "title"), None)
                    heading = _text(sec_title) if sec_title is not None else ""
                    blocks.append(f"SECTION: {heading}\n{_text(child)}")
                elif name in {"p", "list", "table-wrap", "fig"}:
                    loose.append(_text(child))
            if loose:
                blocks.insert(1, "BODY:\n" + "\n".join(loose))

        captions = []
        for element in root.iter():
            if _local(element.tag) in {"fig", "table-wrap"}:
                label = next((c for c in element if _local(c.tag) == "label"), None)
                caption = next((c for c in element if _local(c.tag) == "caption"), None)
                if caption is not None:
                    captions.append(f"{_text(label) if label is not None else ''}: {_text(caption)}")
        if captions:
            blocks.append("CAPTIONS:\n" + "\n".join(captions))

        back = next((e for e in root.iter() if _local(e.tag) == "back"), None)
        if back is not None:
            pieces = [_text(child) for child in back if _local(child.tag) not in _SKIP_TAGS]
            pieces = [p for p in pieces if p]
            if pieces:
                blocks.append("BACK MATTER:\n" + "\n".join(pieces))

        pages = [PDFPage(page_number=i + 1, text=text) for i, text in enumerate(blocks) if text.strip()]
        return PDFDocument(source_file=str(path), pages=pages)


def read_paper(path: str | Path) -> PDFDocument:
    """PDF via PyMuPDF, ``.xml``/``.nxml`` via JATS."""
    path = Path(path)
    if path.suffix.lower() in {".xml", ".nxml"}:
        return JATSReader().read(path)
    from pdf.pdf_reader import PDFReader

    return PDFReader().read(path)
