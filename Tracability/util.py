import tree_sitter_java
from tree_sitter import Language, Parser

_JAVA = Language(tree_sitter_java.language())
_PARSER = Parser(_JAVA)
_CLASS_NODES  = {"class_declaration", "interface_declaration", "enum_declaration", "record_declaration"}
_METHOD_NODES = {"method_declaration", "constructor_declaration"}

def extract_methods(path):

    if not path.endswith(".java"):
        with open(path, "rb") as f:
            n_lines = f.read().count(b"\n") + 1
        return [(1, n_lines, os.path.basename(path))]     
    """Return every method in a Java file as (start_line, end_line, id)."""
    with open(path, "rb") as f:
        tree = _PARSER.parse(f.read())
    methods = []

    def name_of(node):
        n = node.child_by_field_name("name")
        return n.text.decode() if n is not None else "<anon>"

    def walk(node, cls):
        if node.type in _CLASS_NODES:
            cname = name_of(node)
            cls = f"{cls}.{cname}" if cls else cname
        elif node.type in _METHOD_NODES:
            s, e = node.start_point[0] + 1, node.end_point[0] + 1
            mid = f"{cls}#{name_of(node)}@{s}" if cls else f"{name_of(node)}@{s}"
            methods.append((s, e, mid))
        for child in node.children:
            walk(child, cls)

    walk(tree.root_node, None)
    return methods


_path_cache = {}

def find_file(file_name):
    """Locate a bare 'PayBillAction.java' somewhere under SOURCE_ROOT."""
    base = os.path.basename(file_name)          # tolerate a bare name or a partial path
    if base in _path_cache:
        return _path_cache[base]
    for root, _, files in os.walk(SOURCE_ROOT):
        if base in files:
            hit = os.path.join(root, base)
            _path_cache[base] = hit
            return hit
    raise FileNotFoundError(f"{base} not found under {SOURCE_ROOT}")

def is_overlapping(start_line, end_line, m_start, m_end):
    """True if [start_line, end_line] and [m_start, m_end] share any line (inclusive)."""
    return start_line <= m_end and m_start <= end_line

import os

SOURCE_ROOT = "/Users/neo/Desktop/Uni/Sepideh/10.hardness/iTrust" 
SOURCE_ROOT = "/Users/neo/Desktop/Uni/Sepideh/10.hardness/iTrust"

def methods_overlapping(file_name, start_line, end_line):
    if file_name.endswith('jsp'):
        return {file_name}
    path = find_file(file_name)
    methods = extract_methods(path)
    hits = set()
    for m_start, m_end, mid in methods:
        if is_overlapping(start_line, end_line, m_start, m_end):
            hits.add(mid)
    return hits


_class_index = {}   # cache so each file is parsed only once

def extract_classes(path):
    """Every class in a file as (start_line, end_line, class_id)."""
    if path in _class_index:
        return _class_index[path]
    with open(path, "rb") as f:
        tree = _PARSER.parse(f.read())
    classes = []

    def name_of(node):
        n = node.child_by_field_name("name")
        return n.text.decode() if n is not None else "<anon>"

    def walk(node, cls):
        if node.type in _CLASS_NODES:
            cname = name_of(node)
            cls = f"{cls}.{cname}" if cls else cname
            s, e = node.start_point[0] + 1, node.end_point[0] + 1
            classes.append((s, e, cls))
        for child in node.children:
            walk(child, cls)

    walk(tree.root_node, None)
    _class_index[path] = classes
    return classes

def innermost_class(classes, line):
    """The smallest class span containing `line` (so inner classes win)."""
    best, best_size = None, None
    for s, e, cid in classes:
        if s <= line <= e:                     # this class contains the line
            size = e - s
            if best_size is None or size < best_size:
                best, best_size = cid, size    # keep the tightest-fitting one
    return best

def dosc(cont):
    """cont = {class_id: line_count}. Returns DOSC in [0,1]."""
    locc = sum(cont.values())          # total concern lines = CONT(s, P)
    T = len(cont)                      # number of classes touched = |T| = CDC
    if T <= 1 or locc == 0:            # one class (or none) -> localized
        return 0.0
    inv = 1.0 / T                      # uniform baseline 1/|T|
    var = sum((c / locc - inv) ** 2 for c in cont.values())
    return 1.0 - (T * var) / (T - 1)


def extract_classes(path):
    """Return every class in a Java file as (start_line, end_line, id)."""
    if not path.endswith(".java"):
        with open(path, "rb") as f:
            n_lines = f.read().count(b"\n") + 1
        return [(1, n_lines, os.path.basename(path))]


    with open(path, "rb") as f:
        tree = _PARSER.parse(f.read())
    classes = []

    def name_of(node):
        n = node.child_by_field_name("name")
        return n.text.decode() if n is not None else "<anon>"

    def walk(node, cls):
        if node.type in _CLASS_NODES:
            cname = name_of(node)
            cls = f"{cls}.{cname}" if cls else cname
            s, e = node.start_point[0] + 1, node.end_point[0] + 1
            classes.append((s, e, cls))
        for child in node.children:
            walk(child, cls)

    walk(tree.root_node, None)
    return classes

def dosm(cont, locc):
    """cont = {method_id: line_count}, locc = total concern lines (incl. non-method).
    DOSM per Eaddy et al. eq. 7, Option B denominator."""
    locc = sum(cont.values()) 
    T = len(cont)                       # number of methods the concern touches
    if T <= 1 or locc == 0:             # 0 or 1 method -> localized (eq.7 undefined)
        return 0.0
    inv = 1.0 / T                       # uniform baseline 1/|T|
    var = sum((c / locc - inv) ** 2 for c in cont.values())
    return 1.0 - (T * var) / (T - 1)