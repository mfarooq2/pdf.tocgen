"""Extract metadata for a string in a pdf file"""

from toml.encoder import _dump_str, _dump_float

import re

from fitz import Document, Page
from typing import Optional, List


def extract_meta(doc: Document,
                 pattern: str,
                 page: Optional[int] = None,
                 ign_case: bool = False
                 ) -> List[dict]:
    """Extract meta for a `pattern` on `page` in a pdf document

    Arguments
      doc: document from pymupdf
      pattern: a regular expression pattern
      page: page number (1-based index), if None is given, search for the
            entire document, but this is highly discouraged.
      ign_case: ignore case?
    """
    result = []

    if page is None:
        pages = doc.pages()
    elif 1 <= page <= doc.page_count:
        pages = [doc[page - 1]]
    else:  # page out of range
        return result

    regex = re.compile(
        pattern,
        re.IGNORECASE
    ) if ign_case else re.compile(pattern)

    # we could parallelize this, but I don't see a reason
    # to *not* specify a page number
    for p in pages:
        result.extend(search_in_page(regex, p))

    return result


def search_in_page(regex: re.Pattern, page: Page) -> List[dict]:
    """Search for `text` in `page` and extract meta

    Arguments
      needle: the text to search for
      page: page number (1-based index)
    Returns
      a list of meta
    """
    result = []

    page_meta = page.get_textpage().extractDICT()

    # we are using get(key, []) to bypass any missing key errors
    for blk in page_meta.get('blocks', []):
        for ln in blk.get('lines', []):
            for spn in ln.get('spans', []):
                text = spn.get('text', "")
                # the current search algorithm is very naive and doesn't handle
                # line breaks and more complex layout. might want to take a
                # look at `page.searchFor`, but the current algorithm should be
                # enough for TeX-generated pdf
                if regex.search(text):
                    result.append(spn)
    return result

def blk_to_str(blk: dict) -> str:
    """Extract all the text inside a block"""
    return " ".join([
        spn.get('text', "").strip()
        for line in blk.get('lines', [])
        for spn in line.get('spans', [])
    ])


def to_bools(var: int) -> str:
    """Convert int to lowercase bool string"""
    return str(var != 0).lower()


def dump_meta(spn: dict) -> str:
    """Dump the span dict from PyMuPDF to TOML compatible string"""
    result = []

    result.append(f"font.name = {_dump_str(spn['font'])}")
    result.append(f"font.size = {_dump_float(spn['size'])}")
    result.append(f"font.color = {spn['color']:#08x}")

    flags = spn['flags']

    result.append(f"font.superscript = {to_bools(flags & 0b00001)}")
    result.append(f"font.italic = {to_bools(flags & 0b00010)}")
    result.append(f"font.serif = {to_bools(flags & 0b00100)}")
    result.append(f"font.monospace = {to_bools(flags & 0b01000)}")
    result.append(f"font.bold = {to_bools(flags & 0b10000)}")

    bbox = spn['bbox']

    result.append(f"bbox.left = {_dump_float(bbox[0])}")
    result.append(f"bbox.top = {_dump_float(bbox[1])}")
    result.append(f"bbox.right = {_dump_float(bbox[2])}")
    result.append(f"bbox.bottom = {_dump_float(bbox[3])}")

    return '\n'.join(result)

def generate_recipe(doc: Document, recipe_file: str, page: Optional[int] = None, ign_case: bool = False) -> List[dict]:
    """Generate a recipe based on the pdf document."""
    
    def get_spans(doc: Document, page: Optional[int] = None) -> List[dict]:
      """Extract all spans in the document"""
      all_spans = []
      if page is None:
        pages = doc.pages()
      elif 1 <= page <= doc.page_count:
          pages = [doc[page - 1]]
      else:  # page out of range
          return result
      for p in pages:
        page_meta = p.get_textpage().extractDICT()
        for blk in page_meta.get('blocks', []):
            for ln in blk.get('lines', []):
              all_spans.extend(ln.get('spans', []))
      return all_spans
    spans = get_spans(doc, page)
    
    if not spans:
      return []

    spans_by_size = {}
    for sp in spans:
        font_size = sp['size']
        spans_by_size.setdefault(font_size, []).append(sp)
    
    spans_by_size_sorted = sorted(spans_by_size.items(), key=lambda item: item[0])

    recipe = []
    if len(spans_by_size_sorted) >= 1:
      for i in range(len(spans_by_size_sorted)):
        sp = spans_by_size_sorted[i]
        result.append("[[heading]]")
        result.append(f"level = {i+1}")
        result.append(f"font.name = {_dump_str(sp['font'])}")
        result.append(f"font.size = {_dump_float(sp['size'])}")

    return result
    

    
    


def extract_meta(doc: Document,
                 pattern: str,
                 page: Optional[int] = None,
                 ign_case: bool = False
                 ) -> List[dict]:
    """Extract meta for a `pattern` on `page` in a pdf document

    Arguments
      doc: document from pymupdf
      pattern: a regular expression pattern
      page: page number (1-based index), if None is given, search for the
            entire document, but this is highly discouraged.
      ign_case: ignore case?
    """
    result = []

    if page is None:
        pages = doc.pages()
    elif 1 <= page <= doc.page_count:
        pages = [doc[page - 1]]
    else:  # page out of range
        return result

    regex = re.compile(
        pattern,
        re.IGNORECASE
    ) if ign_case else re.compile(pattern)

    # we could parallelize this, but I don't see a reason
    # to *not* specify a page number
    for p in pages:
        result.extend(search_in_page(regex, p))

    return result
    
    
def generate_recipe(doc: Document, recipe_file: str, page: Optional[int] = None, ign_case: bool = False) -> List[dict]:
    """Generate a recipe based on the pdf document."""
    #TODO : Add logic to generate a recipe
    
    
    spans = get_spans(doc,page)
    return generate_recipe_from_spans(spans)

def generate_recipe_from_spans(spans: List[dict]) -> List[dict]:
  """Generate recipe from spans, it creates a basic recipe based on the different spans present in the document."""
  result = []
  spans_by_size = {}
  for sp in spans:
    font_size = sp['size']
    spans_by_size.setdefault(font_size, []).append(sp)

  spans_by_size_sorted = sorted(spans_by_size.items(), key=lambda item: item[0])

  recipe = []
  if len(spans_by_size_sorted) >= 1:
    for i in range(len(spans_by_size_sorted)):
      sp = spans_by_size_sorted[i]
      result.append("[[heading]]")
      result.append(f"level = {i+1}")
      result.append(f"font.name = {_dump_str(sp['font'])}")
      result.append(f"font.size = {_dump_float(sp['size'])}")
      result.append("# font.size_tolerance = 1e-5")
      result.append(f"# font.color = {sp['color']:#08x}")

      flags = sp['flags']

      result.append(f"# font.superscript = {to_bools(flags & 0b00001)}")
      result.append(f"# font.italic = {to_bools(flags & 0b00010)}")
      result.append(f"# font.serif = {to_bools(flags & 0b00100)}")
      result.append(f"# font.monospace = {to_bools(flags & 0b01000)}")
      result.append(f"# font.bold = {to_bools(flags & 0b10000)}")

      bbox = sp['bbox']

      result.append(f"# bbox.left = {_dump_float(bbox[0])}")
      result.append(f"# bbox.top = {_dump_float(bbox[1])}")
      result.append(f"# bbox.right = {_dump_float(bbox[2])}")
      result.append(f"# bbox.bottom = {_dump_float(bbox[3])}")
      result.append("# bbox.tolerance = 1e-5")

      
  return result

def get_spans(doc: Document, page: Optional[int] = None) -> List[dict]:
    """Extract all spans in the document"""
    all_spans = []
    if page is None:
        pages = doc.pages()
    elif 1 <= page <= doc.page_count:
        pages = [doc[page - 1]]
    else:  # page out of range
        return result
    for p in pages:
      page_meta = p.get_textpage().extractDICT()
      for blk in page_meta.get('blocks', []):
          for ln in blk.get('lines', []):
            all_spans.extend(ln.get('spans', []))
    return all_spans


def extract_meta(doc: Document,
                 pattern: str,
                 page: Optional[int] = None,
                 ign_case: bool = False
                 ) -> List[dict]:
    """Extract meta for a `pattern` on `page` in a pdf document

    Arguments
      doc: document from pymupdf
      pattern: a regular expression pattern
      page: page number (1-based index), if None is given, search for the
            entire document, but this is highly discouraged.
      ign_case: ignore case?
    """
    result = []

    if page is None:
        pages = doc.pages()
    elif 1 <= page <= doc.page_count:
        pages = [doc[page - 1]]
    else:  # page out of range
        return result

    regex = re.compile(
        pattern,
        re.IGNORECASE
    ) if ign_case else re.compile(pattern)

    # we could parallelize this, but I don't see a reason
    # to *not* specify a page number
    for p in pages:
        result.extend(search_in_page(regex, p))

    return result
    
    
def generate_recipe(doc: Document, recipe_file: str, page: Optional[int] = None, ign_case: bool = False) -> List[dict]:
    """Generate a recipe based on the pdf document."""
    
    
    spans = get_spans(doc,page)
    return generate_recipe_from_spans(spans)

def generate_recipe_from_spans(spans: List[dict]) -> List[dict]:
  """Generate recipe from spans, it creates a basic recipe based on the different spans present in the document."""
  result = []
  spans_by_size = {}
  for sp in spans:
    font_size = sp['size']
    spans_by_size.setdefault(font_size, []).append(sp)

  spans_by_size_sorted = sorted(spans_by_size.items(), key=lambda item: item[0])

  recipe = []
  if len(spans_by_size_sorted) >= 1:
    for i in range(len(spans_by_size_sorted)):
      sp = spans_by_size_sorted[i]
      result.append("[[heading]]")
      result.append(f"level = {i+1}")
      result.append(f"font.name = {_dump_str(sp['font'])}")
      result.append(f"font.size = {_dump_float(sp['size'])}")
      result.append("# font.size_tolerance = 1e-5")
      result.append(f"# font.color = {sp['color']:#08x}")

      flags = sp['flags']

      result.append(f"# font.superscript = {to_bools(flags & 0b00001)}")
      result.append(f"# font.italic = {to_bools(flags & 0b00010)}")
      result.append(f"# font.serif = {to_bools(flags & 0b00100)}")
      result.append(f"# font.monospace = {to_bools(flags & 0b01000)}")
      result.append(f"# font.bold = {to_bools(flags & 0b10000)}")

      bbox = sp['bbox']

      result.append(f"# bbox.left = {_dump_float(bbox[0])}")
      result.append(f"# bbox.top = {_dump_float(bbox[1])}")
      result.append(f"# bbox.right = {_dump_float(bbox[2])}")
      result.append(f"# bbox.bottom = {_dump_float(bbox[3])}")
      result.append("# bbox.tolerance = 1e-5")

      
  return result
    
def get_spans(doc: Document, page: Optional[int] = None) -> List[dict]:
    """Extract all spans in the document"""
    all_spans = []
    if page is None:
        pages = doc.pages()
    elif 1 <= page <= doc.page_count:
        pages = [doc[page - 1]]
    else:  # page out of range
        return result
    for p in pages:
      page_meta = p.get_textpage().extractDICT()
      for blk in page_meta.get('blocks', []):
          for ln in blk.get('lines', []):
            all_spans.extend(ln.get('spans', []))
    return all_spans

def dump_toml(spn: dict, level: int, trail_nl: bool = False) -> str:
    """Dump a valid TOML directly usable by pdftocgen

    Argument
      spn: span dict of the heading
      level: heading level
      trail_nl: add trailing new line
    Returns
      a valid toml string
    """
    result = []

    result.append("[[heading]]")
    result.append(f"# {spn.get('text', '')}")
    result.append(f"level = {level}")
    result.append("greedy = true")

    # strip font subset prefix
    # == takeWhile (\c -> c /= '+') str
    before, sep, after = spn['font'].partition('+')
    font = after if sep else before

    result.append(f"font.name = {_dump_str(font)}")
    result.append(f"font.size = {_dump_float(spn['size'])}")
    result.append("# font.size_tolerance = 1e-5")
    result.append(f"# font.color = {spn['color']:#08x}")

    flags = spn['flags']

    result.append(f"# font.superscript = {to_bools(flags & 0b00001)}")
    result.append(f"# font.italic = {to_bools(flags & 0b00010)}")
    result.append(f"# font.serif = {to_bools(flags & 0b00100)}")
    result.append(f"# font.monospace = {to_bools(flags & 0b01000)}")
    result.append(f"# font.bold = {to_bools(flags & 0b10000)}")

    bbox = spn['bbox']

    result.append(f"# bbox.left = {_dump_float(bbox[0])}")
    result.append(f"# bbox.top = {_dump_float(bbox[1])}")
    result.append(f"# bbox.right = {_dump_float(bbox[2])}")
    result.append(f"# bbox.bottom = {_dump_float(bbox[3])}")
    result.append("# bbox.tolerance = 1e-5")

    if trail_nl:
        result.append("")

    return '\n'.join(result)
