# Larimar values in gdb (and VS Code with the C/C++ extension and gdb): String as text, lists with
# their elements, optionals as their value or null, Any by what it holds, enums as Variant(fields),
# objects with their real class and the fields of every level.
#
#   (gdb) source $LARIMAR_HOME/debug/larimar_gdb.py
#
# The program must be built with larimar build --debug (or -g): the printers read the generated C types.

import re

import gdb

MAX_ITEMS = 10000
MAX_TEXT = 4000

ANY_KINDS = ["null", "int8", "int16", "int32", "int64", "byte", "uint16", "uint32", "uint64",
             "float32", "float64", "bool", "String", "table", "object", "value"]


def _text(ptr, length):
    if int(ptr) == 0 or length <= 0:
        return ""
    n = min(length, MAX_TEXT)
    data = gdb.selected_inferior().read_memory(int(ptr), n).tobytes()
    s = data.decode("utf-8", "replace")
    return s + "\u2026" if length > MAX_TEXT else s


def _quote(s):
    s = '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t") + '"'
    if "utf" not in gdb.host_charset().lower():            # gdb without a UTF-8 terminal: escape the rest
        s = "".join(c if ord(c) < 128 else "\\u{%x}" % ord(c) for c in s)
    return s


def _fields(t):
    t = t.strip_typedefs()
    return [f.name for f in t.fields()] if t.code in (gdb.TYPE_CODE_STRUCT, gdb.TYPE_CODE_UNION) else []


def _name(t):
    t = t.strip_typedefs()
    return t.tag or t.name or ""


def _is_class(t):
    t = t.strip_typedefs()
    names = _fields(t)
    if not names:
        return False
    if names[0] == "_h":
        return _name(t.fields()[0].type) == "RtObjHead"
    if names[0] == "_super":
        return _is_class(t.fields()[0].type)
    return False


def _real_object(obj):
    """obj (a class struct value) with the type of its real class."""
    head = obj
    while _fields(head.type) and _fields(head.type)[0] == "_super":
        head = head["_super"]
    try:
        vt = head["_h"]["vt"]
        cls = vt.cast(gdb.lookup_type("RtVTableHead").pointer()).dereference()["cls"]
        name = cls.dereference()["name"].string()
        t = gdb.lookup_type("struct " + name)
        if t != obj.type.strip_typedefs():
            return obj.address.cast(t.pointer()).dereference()
    except (gdb.error, gdb.MemoryError):
        pass
    return obj


def _object_fields(obj, out):
    for f in obj.type.strip_typedefs().fields():
        if f.name == "_h":
            continue
        if f.name == "_super":
            _object_fields(obj["_super"], out)
            continue
        out.append((f.name, obj[f.name]))


def _short(v):
    try:
        p = gdb.default_visualizer(v)
        if p is not None and hasattr(p, "to_string"):
            s = p.to_string()
            return s if isinstance(s, str) else str(s)
        return str(v)
    except gdb.error:
        return "?"


class StringPrinter:
    def __init__(self, v):
        self.v = v

    def to_string(self):
        try:
            return _quote(_text(self.v["ptr"], int(self.v["len"])))
        except gdb.MemoryError:
            return "<unreadable>"

    def display_hint(self):
        return None


class ListPrinter:
    def __init__(self, v, pointer):
        self.null = pointer and int(v) == 0
        self.v = None if self.null else (v.dereference() if pointer else v)

    def _count(self):
        return 0 if self.v is None else max(0, min(int(self.v["length"]), MAX_ITEMS))

    def to_string(self):
        if self.null:
            return "null"
        n = int(self.v["length"])
        shown = [_short(self.v["items"][i]) for i in range(min(self._count(), 5))]
        return "[%d] [%s%s]" % (n, ", ".join(shown), ", \u2026" if n > 5 else "")

    def children(self):
        for i in range(self._count()):
            yield "[%d]" % i, self.v["items"][i]

    def display_hint(self):
        return "array"


class OptionalPrinter:
    def __init__(self, v):
        self.v = v

    def to_string(self):
        return _short(self.v["value"]) if bool(self.v["has"]) else "null"

    def children(self):
        if bool(self.v["has"]):
            val = self.v["value"]
            if val.type.strip_typedefs().code == gdb.TYPE_CODE_STRUCT:
                for f in val.type.strip_typedefs().fields():
                    yield f.name, val[f.name]


class ObjectPrinter:
    def __init__(self, v, pointer):
        self.null = pointer and int(v) == 0
        self.obj = None if self.null else _real_object(v.dereference() if pointer else v)

    def to_string(self):
        if self.null:
            return "null"
        fields = []
        _object_fields(self.obj, fields)
        parts = ["%s=%s" % (n, _short(x)) for n, x in fields[:4]]
        name = _name(self.obj.type).replace("__", ".")
        return "%s {%s%s}" % (name, ", ".join(parts), ", \u2026" if len(fields) > 4 else "")

    def children(self):
        if self.obj is None:
            return
        fields = []
        _object_fields(self.obj, fields)
        for n, x in fields:
            yield n, x


class InterfacePrinter:
    def __init__(self, v):
        self.inner = None
        try:
            p = v["obj"]
            if int(p) != 0:
                head = p.cast(gdb.lookup_type("RtObjHead").pointer()).dereference()
                cls = head["vt"].cast(gdb.lookup_type("RtVTableHead").pointer()).dereference()["cls"]
                t = gdb.lookup_type("struct " + cls.dereference()["name"].string())
                self.inner = ObjectPrinter(p.cast(t.pointer()), True)
        except (gdb.error, gdb.MemoryError):
            self.inner = None

    def to_string(self):
        return self.inner.to_string() if self.inner else "null"

    def children(self):
        return self.inner.children() if self.inner else iter(())


class EnumPrinter:
    def __init__(self, v):
        self.v = v
        enum_name = _name(v.type)
        shown = str(v["tag"])
        self.variant = shown[len(enum_name) + 1:] if shown.startswith(enum_name + "_") else shown
        self.payload = None
        try:
            names = _fields(v["as"].type)
            if self.variant in names:
                p = v["as"][self.variant]
                if _fields(p.type):
                    self.payload = p
        except gdb.error:
            pass

    def to_string(self):
        if self.payload is None:
            return self.variant
        parts = ["%s=%s" % (f, _short(self.payload[f])) for f in _fields(self.payload.type)]
        return "%s(%s)" % (self.variant, ", ".join(parts))

    def children(self):
        if self.payload is not None:
            for f in _fields(self.payload.type):
                yield f, self.payload[f]


def _table_children(t):
    n = max(0, min(int(t["length"]), MAX_ITEMS))
    for i in range(n):
        yield "[%d]" % i, t["items"][i]
    c = max(0, min(int(t["count"]), MAX_ITEMS))
    for j in range(c):
        key = t["keys"][j]
        yield _text(key["ptr"], int(key["len"])), t["values"][j]


def _table_summary(t):
    n, c = int(t["length"]), int(t["count"])
    if c == 0:
        return "{ %d items }" % n
    if n == 0:
        return "{ %d entries }" % c
    return "{ %d items, %d entries }" % (n, c)


class AnyPrinter:
    def __init__(self, v):
        self.v = v
        self.kind = int(v["kind"])

    def to_string(self):
        a = self.v["as"]
        k = self.kind
        if k == 0:
            return "null"
        if 1 <= k <= 4:
            return str(int(a["i"]))
        if 5 <= k <= 8:
            return str(int(a["u"]))
        if k in (9, 10):
            return str(float(a["f"]))
        if k == 11:
            return "true" if bool(a["b"]) else "false"
        if k == 12:
            return StringPrinter(a["s"]).to_string()
        if k == 13:
            return _table_summary(a["t"].dereference()) if int(a["t"]) else "null"
        if k == 14:
            return self._object().to_string()
        if k == 15:
            try:
                return "%s value" % a["box"]["type"].cast(gdb.lookup_type("RtValType").pointer()).dereference()["name"].string()
            except gdb.error:
                return "value"
        return ANY_KINDS[k] if 0 <= k < len(ANY_KINDS) else "?"

    def _object(self):
        box = self.v["as"]["box"]
        try:
            name = box["type"].cast(gdb.lookup_type("RtClass").pointer()).dereference()["name"].string()
            t = gdb.lookup_type("struct " + name)
            return ObjectPrinter(box["ptr"].cast(t.pointer()), True)
        except gdb.error:
            return ObjectPrinter(gdb.Value(0).cast(gdb.lookup_type("void").pointer()), True)

    def children(self):
        if self.kind == 13 and int(self.v["as"]["t"]):
            return _table_children(self.v["as"]["t"].dereference())
        if self.kind == 14:
            return self._object().children()
        return iter(())


class TablePrinter:
    def __init__(self, v, pointer):
        self.t = None if pointer and int(v) == 0 else (v.dereference() if pointer else v)

    def to_string(self):
        return _table_summary(self.t) if self.t is not None else "null"

    def children(self):
        return _table_children(self.t) if self.t is not None else iter(())


LIST_NAME = re.compile(r"^(List|Slice|Arr)_[A-Za-z0-9_]+$")
OPT_NAME = re.compile(r"^Opt_[A-Za-z0-9_]+$")


def lookup(v):
    t = v.type.strip_typedefs()
    pointer = t.code == gdb.TYPE_CODE_PTR
    target = t.target().strip_typedefs() if pointer else t
    if target.code != gdb.TYPE_CODE_STRUCT:
        return None
    name = _name(target)
    if name == "RtString" and not pointer:
        return StringPrinter(v)
    if LIST_NAME.match(name):
        return ListPrinter(v, pointer)
    if name == "RtTable":
        return TablePrinter(v, pointer)
    if pointer:
        return ObjectPrinter(v, True) if _is_class(target) else None
    if OPT_NAME.match(name):
        return OptionalPrinter(v)
    if name == "RtAny":
        return AnyPrinter(v)
    names = _fields(target)
    if names == ["tag", "as"] and target.fields()[0].type.strip_typedefs().code == gdb.TYPE_CODE_ENUM:
        return EnumPrinter(v)
    if names == ["obj", "t"] and _name(target.fields()[1].type.target()).endswith("_Table"):
        return InterfacePrinter(v)
    if _is_class(target):
        return ObjectPrinter(v, False)
    return None


gdb.pretty_printers.append(lookup)
