# Larimar values in lldb (and VS Code with CodeLLDB): String as text, lists with their elements,
# optionals as their value or null, Any by what it holds, enums as Variant(fields), objects with their
# real class and the fields of every level.
#
#   (lldb) command script import $LARIMAR_HOME/debug/larimar_lldb.py
#
# The program must be built with larimar build --debug (or -g): the formatters read the generated C types.

import json

import lldb

MAX_ITEMS = 10000
MAX_TEXT = 4000

ANY_KINDS = ["null", "int8", "int16", "int32", "int64", "byte", "uint16", "uint32", "uint64",
             "float32", "float64", "bool", "String", "table", "object", "value"]


# ---------------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------------

def _raw(v):
    """The value without our own synthetic children (to read the C fields)."""
    return v.GetNonSyntheticValue() if v is not None and v.IsValid() else v


def _deref(v):
    """The value a pointer points to (or the value itself); None for a null pointer."""
    if v is None or not v.IsValid():
        return None
    v = _raw(v)
    if v.TypeIsPointerType():
        if v.GetValueAsUnsigned() == 0:
            return None
        return _raw(v.Dereference())
    return v


def _field(v, name):
    if v is None or not v.IsValid():
        return None
    c = _raw(v).GetChildMemberWithName(name)
    return c if c.IsValid() else None


def _text(process, ptr, length):
    if ptr == 0 or length <= 0:
        return ""
    cut = length > MAX_TEXT
    err = lldb.SBError()
    data = process.ReadMemory(ptr, min(length, MAX_TEXT), err)
    if not err.Success():
        return None
    s = data.decode("utf-8", "replace")
    return s + "…" if cut else s


def _string_value(v):
    """The text of an RtString value, or None."""
    v = _deref(v)
    if v is None:
        return None
    ptr = _field(v, "ptr")
    ln = _field(v, "len")
    if ptr is None or ln is None:
        return None
    return _text(v.GetProcess(), ptr.GetValueAsUnsigned(), ln.GetValueAsSigned())


def _quote(s):
    return json.dumps(s, ensure_ascii=False)


def _short(v):
    """A one-line view of any value, for summaries of containers."""
    if v is None or not v.IsValid():
        return "?"
    s = v.GetSummary()
    if s:
        return s
    val = v.GetValue()
    if val is not None:
        return val
    n = v.GetNumChildren()
    if 0 < n <= 4:
        return "{%s}" % ", ".join("%s=%s" % (v.GetChildAtIndex(i).GetName(), _short_leaf(v.GetChildAtIndex(i)))
                                  for i in range(n))
    return "{...}"


def _short_leaf(v):
    s = v.GetSummary() or v.GetValue()
    return s if s is not None else "{...}"


def _type_name(t):
    return t.GetUnqualifiedType().GetName() or ""


def _struct_type(t):
    t = t.GetCanonicalType()
    if t.IsPointerType():
        t = t.GetPointeeType().GetCanonicalType()
    return t


def _field_names(t):
    return [t.GetFieldAtIndex(i).GetName() for i in range(t.GetNumberOfFields())]


# ---------------------------------------------------------------------------------------------
# String
# ---------------------------------------------------------------------------------------------

def string_summary(valobj, internal_dict):
    s = _string_value(valobj)
    if s is None:
        return "null" if valobj.TypeIsPointerType() else "<unreadable>"
    return _quote(s)


# ---------------------------------------------------------------------------------------------
# Lists (T[*]), slices and fixed arrays (T[])
# ---------------------------------------------------------------------------------------------

class ListProvider:
    def __init__(self, valobj, internal_dict):
        self.valobj = valobj
        self.update()

    def update(self):
        self.items = None
        self.count = 0
        self.fixed = False
        v = _deref(self.valobj)
        if v is None:
            return False
        items = _field(v, "items")
        length = _field(v, "length")
        if items is None or length is None:
            return False
        self.items = items
        self.fixed = items.GetType().IsArrayType()
        self.count = max(0, min(length.GetValueAsSigned(), MAX_ITEMS))
        if not self.fixed and items.GetValueAsUnsigned() == 0:
            self.count = 0
        self.elem = items.GetType().GetArrayElementType() if self.fixed else items.GetType().GetPointeeType()
        return False

    def num_children(self):
        return self.count

    def get_child_index(self, name):
        try:
            return int(name.lstrip("[").rstrip("]"))
        except ValueError:
            return -1

    def get_child_at_index(self, index):
        if index < 0 or index >= self.count or self.items is None:
            return None
        if self.fixed:
            c = self.items.GetChildAtIndex(index)
            return c.Clone("[%d]" % index) if c.IsValid() else None
        size = self.elem.GetByteSize()
        addr = self.items.GetValueAsUnsigned() + index * size
        return self.valobj.CreateValueFromAddress("[%d]" % index, addr, self.elem)

    def has_children(self):
        return True


def list_summary(valobj, internal_dict):
    v = _deref(valobj)
    if v is None:
        return "null"
    length = _field(v, "length")
    n = length.GetValueAsSigned() if length is not None else 0
    p = ListProvider(valobj, internal_dict)
    shown = [_short(p.get_child_at_index(i)) for i in range(min(p.count, 5))]
    more = ", …" if n > 5 else ""
    return "[%d] [%s%s]" % (n, ", ".join(shown), more)


# ---------------------------------------------------------------------------------------------
# Optionals (T? as a struct: { has, value }; class types are plain pointers)
# ---------------------------------------------------------------------------------------------

class OptionalProvider:
    def __init__(self, valobj, internal_dict):
        self.valobj = valobj
        self.update()

    def update(self):
        self.value = None
        has = _field(self.valobj, "has")
        if has is not None and has.GetValueAsUnsigned() != 0:
            self.value = _field(self.valobj, "value")
        return False

    def num_children(self):
        if self.value is None:
            return 0
        return self.value.GetNumChildren()

    def get_child_index(self, name):
        return self.value.GetIndexOfChildWithName(name) if self.value is not None else -1

    def get_child_at_index(self, index):
        return self.value.GetChildAtIndex(index) if self.value is not None else None

    def has_children(self):
        return self.value is not None and self.value.MightHaveChildren()


def optional_summary(valobj, internal_dict):
    has = _field(valobj, "has")
    if has is None:
        return None
    if has.GetValueAsUnsigned() == 0:
        return "null"
    return _short(_field(valobj, "value"))


# ---------------------------------------------------------------------------------------------
# Objects of a class (the real class, and the fields of every level, without the header)
# ---------------------------------------------------------------------------------------------

def _class_name_of(obj):
    """The C struct name of the real class of an object (a value of some class struct)."""
    head = obj
    while True:
        names = _field_names(head.GetType().GetCanonicalType())
        if not names:
            return None
        if names[0] == "_h":
            head = _field(head, "_h")
            break
        if names[0] == "_super":
            head = _field(head, "_super")
            continue
        return None
    vt = _field(head, "vt")
    if vt is None or vt.GetValueAsUnsigned() == 0:
        return None
    process = obj.GetProcess()
    err = lldb.SBError()
    ptr_size = obj.GetTarget().GetAddressByteSize()
    cls = process.ReadPointerFromMemory(vt.GetValueAsUnsigned(), err)            # RtVTableHead.cls
    if not err.Success() or cls == 0:
        return None
    name_ptr = process.ReadPointerFromMemory(cls, err)                           # RtClass.name
    if not err.Success() or name_ptr == 0:
        return None
    name = process.ReadCStringFromMemory(name_ptr, 256, err)
    return name if err.Success() else None


def _real_object(valobj):
    """The object with its real class's type (an Animal* that is a Dog is shown as a Dog)."""
    v = _deref(valobj)
    if v is None:
        return None
    name = _class_name_of(v)
    if name and name != _type_name(v.GetType().GetCanonicalType()):
        t = valobj.GetTarget().FindFirstType(name)
        if t.IsValid():
            return valobj.CreateValueFromAddress(v.GetName() or "object", v.GetLoadAddress(), t)
    return v


def _object_fields(obj, out):
    """The fields of an object, the parents' first, without _h and _super."""
    obj = _raw(obj)
    for i in range(obj.GetNumChildren()):
        c = obj.GetChildAtIndex(i)
        n = c.GetName()
        if n == "_h":
            continue
        if n == "_super":
            _object_fields(c, out)
            continue
        out.append(c)


class ObjectProvider:
    def __init__(self, valobj, internal_dict):
        self.valobj = valobj
        self.update()

    def update(self):
        self.fields = []
        obj = _real_object(self.valobj)
        if obj is not None:
            _object_fields(obj, self.fields)
        return False

    def num_children(self):
        return len(self.fields)

    def get_child_index(self, name):
        for i, f in enumerate(self.fields):
            if f.GetName() == name:
                return i
        return -1

    def get_child_at_index(self, index):
        return self.fields[index] if 0 <= index < len(self.fields) else None

    def has_children(self):
        return True


def object_summary(valobj, internal_dict):
    obj = _real_object(valobj)
    if obj is None:
        return "null"
    fields = []
    _object_fields(obj, fields)
    parts = ["%s=%s" % (f.GetName(), _short(f)) for f in fields[:4]]
    more = ", …" if len(fields) > 4 else ""
    name = _type_name(obj.GetType().GetCanonicalType()).replace("__", ".")
    return "%s {%s%s}" % (name, ", ".join(parts), more)


def is_class(sbtype, internal_dict):
    t = _struct_type(sbtype)
    if t.GetTypeClass() != lldb.eTypeClassStruct or t.GetNumberOfFields() == 0:
        return False
    f = t.GetFieldAtIndex(0)
    if f.GetName() == "_h":
        return _type_name(f.GetType()) == "RtObjHead"
    if f.GetName() == "_super":
        return is_class(f.GetType(), internal_dict)
    return False


# ---------------------------------------------------------------------------------------------
# Interface values ({ obj, t }): the object behind them
# ---------------------------------------------------------------------------------------------

def _interface_object(valobj):
    obj = _field(valobj, "obj")
    if obj is None or obj.GetValueAsUnsigned() == 0:
        return None
    # the object's real class: read through RtObjHead.vt at the start of the object
    process = valobj.GetProcess()
    err = lldb.SBError()
    addr = obj.GetValueAsUnsigned()
    vt = process.ReadPointerFromMemory(addr, err)
    cls = process.ReadPointerFromMemory(vt, err) if err.Success() and vt else 0
    name_ptr = process.ReadPointerFromMemory(cls, err) if err.Success() and cls else 0
    name = process.ReadCStringFromMemory(name_ptr, 256, err) if name_ptr else None
    if not name:
        return None
    t = valobj.GetTarget().FindFirstType(name)
    if not t.IsValid():
        return None
    return valobj.CreateValueFromAddress("object", addr, t)


class InterfaceProvider(ObjectProvider):
    def update(self):
        self.fields = []
        obj = _interface_object(self.valobj)
        if obj is not None:
            _object_fields(obj, self.fields)
        return False


def interface_summary(valobj, internal_dict):
    obj = _interface_object(valobj)
    if obj is None:
        return "null"
    return object_summary(obj, internal_dict)


def is_interface(sbtype, internal_dict):
    t = _struct_type(sbtype)
    if t.GetTypeClass() != lldb.eTypeClassStruct:
        return False
    if _field_names(t) != ["obj", "t"]:
        return False
    return _type_name(t.GetFieldAtIndex(1).GetType().GetPointeeType()).endswith("_Table")


# ---------------------------------------------------------------------------------------------
# Enums ({ tag, as }): Variant(field=value, ...)
# ---------------------------------------------------------------------------------------------

def _variant(valobj):
    """(variant name, payload value or None)."""
    tag = _field(valobj, "tag")
    if tag is None:
        return None, None
    enum_name = _type_name(valobj.GetType().GetCanonicalType())
    shown = tag.GetValue() or str(tag.GetValueAsSigned())
    variant = shown[len(enum_name) + 1:] if shown.startswith(enum_name + "_") else shown
    payload = None
    union = _field(valobj, "as")
    if union is not None:
        p = _field(union, variant)
        if p is not None and p.GetNumChildren() > 0:
            payload = p
    return variant, payload


class EnumProvider:
    def __init__(self, valobj, internal_dict):
        self.valobj = valobj
        self.update()

    def update(self):
        self.payload = _variant(self.valobj)[1]
        return False

    def num_children(self):
        return self.payload.GetNumChildren() if self.payload is not None else 0

    def get_child_index(self, name):
        return self.payload.GetIndexOfChildWithName(name) if self.payload is not None else -1

    def get_child_at_index(self, index):
        return self.payload.GetChildAtIndex(index) if self.payload is not None else None

    def has_children(self):
        return self.payload is not None


def enum_summary(valobj, internal_dict):
    variant, payload = _variant(valobj)
    if variant is None:
        return None
    if payload is None:
        return variant
    parts = ["%s=%s" % (payload.GetChildAtIndex(i).GetName(), _short(payload.GetChildAtIndex(i)))
             for i in range(payload.GetNumChildren())]
    return "%s(%s)" % (variant, ", ".join(parts))


def is_enum(sbtype, internal_dict):
    t = _struct_type(sbtype)
    if t.GetTypeClass() != lldb.eTypeClassStruct or _field_names(t) != ["tag", "as"]:
        return False
    return t.GetFieldAtIndex(0).GetType().GetCanonicalType().GetTypeClass() == lldb.eTypeClassEnumeration


# ---------------------------------------------------------------------------------------------
# Any and its tables
# ---------------------------------------------------------------------------------------------

def _any_kind(v):
    k = _field(v, "kind")
    return k.GetValueAsSigned() if k is not None else -1


def _any_scalar(v, kind):
    a = _field(v, "as")
    if kind == 0:
        return "null"
    if 1 <= kind <= 4:
        return str(_field(a, "i").GetValueAsSigned())
    if 5 <= kind <= 8:
        return str(_field(a, "u").GetValueAsUnsigned())
    if kind in (9, 10):
        return _field(a, "f").GetValue()
    if kind == 11:
        return "true" if _field(a, "b").GetValueAsUnsigned() else "false"
    if kind == 12:
        s = _string_value(_field(a, "s"))
        return _quote(s) if s is not None else "<unreadable>"
    return None


class TableProvider:
    """Children of a table (RtTable* or the table inside an Any): [0], [1]... then the named entries."""

    def __init__(self, valobj, internal_dict):
        self.valobj = valobj
        self.update()

    def _table(self):
        v = self.valobj
        if _type_name(_struct_type(v.GetType())) == "RtAny":
            kind = _any_kind(v)
            if kind == 13:
                return _deref(_field(_field(v, "as"), "t"))
            if kind == 14:
                self.object = _real_object_of_box(v)
            return None
        return _deref(v)

    def update(self):
        self.children = []
        self.object = None
        t = self._table()
        if self.object is not None:
            _object_fields(self.object, self.children)
            return False
        if t is None:
            return False
        any_type = _field(t, "items").GetType().GetPointeeType()
        size = any_type.GetByteSize()
        items = _field(t, "items").GetValueAsUnsigned()
        n = max(0, min(_field(t, "length").GetValueAsSigned(), MAX_ITEMS))
        for i in range(n if items else 0):
            self.children.append(t.CreateValueFromAddress("[%d]" % i, items + i * size, any_type))
        keys = _field(t, "keys").GetValueAsUnsigned()
        values = _field(t, "values").GetValueAsUnsigned()
        count = max(0, min(_field(t, "count").GetValueAsSigned(), MAX_ITEMS))
        key_type = _field(t, "keys").GetType().GetPointeeType()
        for j in range(count if keys and values else 0):
            key = t.CreateValueFromAddress("key", keys + j * key_type.GetByteSize(), key_type)
            name = _string_value(key) or "?"
            self.children.append(t.CreateValueFromAddress(name, values + j * size, any_type))
        return False

    def num_children(self):
        return len(self.children)

    def get_child_index(self, name):
        for i, c in enumerate(self.children):
            if c.GetName() == name:
                return i
        return -1

    def get_child_at_index(self, index):
        return self.children[index] if 0 <= index < len(self.children) else None

    def has_children(self):
        return len(self.children) > 0


def _real_object_of_box(v):
    box = _field(_field(v, "as"), "box")
    ptr = _field(box, "ptr").GetValueAsUnsigned()
    cls = _field(box, "type").GetValueAsUnsigned()
    if not ptr or not cls:
        return None
    err = lldb.SBError()
    process = v.GetProcess()
    name_ptr = process.ReadPointerFromMemory(cls, err)
    name = process.ReadCStringFromMemory(name_ptr, 256, err) if err.Success() and name_ptr else None
    if not name:
        return None
    t = v.GetTarget().FindFirstType(name)
    return v.CreateValueFromAddress("object", ptr, t) if t.IsValid() else None


def any_summary(valobj, internal_dict):
    kind = _any_kind(valobj)
    if kind < 0 or kind >= len(ANY_KINDS):
        return None
    s = _any_scalar(valobj, kind)
    if s is not None:
        return s
    if kind == 13:
        return table_summary(_field(_field(valobj, "as"), "t"), internal_dict)
    if kind == 14:
        obj = _real_object_of_box(valobj)
        return object_summary(obj, internal_dict) if obj is not None else "object"
    if kind == 15:
        box = _field(_field(valobj, "as"), "box")
        t = _field(box, "type").GetValueAsUnsigned()
        err = lldb.SBError()
        name_ptr = valobj.GetProcess().ReadPointerFromMemory(t, err) if t else 0
        name = valobj.GetProcess().ReadCStringFromMemory(name_ptr, 256, err) if name_ptr else "value"
        return "%s value" % name
    return ANY_KINDS[kind]


def table_summary(valobj, internal_dict):
    t = _deref(valobj)
    if t is None:
        return "null"
    n = _field(t, "length").GetValueAsSigned()
    c = _field(t, "count").GetValueAsSigned()
    if c == 0:
        return "{ %d items }" % n
    if n == 0:
        return "{ %d entries }" % c
    return "{ %d items, %d entries }" % (n, c)


# ---------------------------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------------------------

def __lldb_init_module(debugger, internal_dict):
    m = __name__
    run = debugger.HandleCommand
    run("type category define -e larimar")      # every language: Apple lldb takes "-l c" as C89 only, not the C99 of the program
    run('type summary add -w larimar -F %s.string_summary RtString' % m)
    run('type summary add -w larimar -e -x -F %s.list_summary "^(List|Slice|Arr)_[A-Za-z0-9_]+$"' % m)
    run('type synthetic add -w larimar -x -l %s.ListProvider "^(List|Slice|Arr)_[A-Za-z0-9_]+$"' % m)
    run('type summary add -w larimar -e -x -F %s.optional_summary "^Opt_[A-Za-z0-9_]+$"' % m)
    run('type synthetic add -w larimar -x -l %s.OptionalProvider "^Opt_[A-Za-z0-9_]+$"' % m)
    run('type summary add -w larimar -e -F %s.any_summary RtAny' % m)
    run('type synthetic add -w larimar -l %s.TableProvider RtAny' % m)
    run('type summary add -w larimar -e -F %s.table_summary RtTable' % m)
    run('type synthetic add -w larimar -l %s.TableProvider RtTable' % m)
    # classes, interfaces and enums are recognized by their shape (lldb 16 and later)
    for kind, summary, provider in (("class", "object_summary", "ObjectProvider"),
                                    ("interface", "interface_summary", "InterfaceProvider"),
                                    ("enum", "enum_summary", "EnumProvider")):
        run('type summary add -w larimar -e --recognizer-function -F %s.%s %s.is_%s' % (m, summary, m, kind))
        run('type synthetic add -w larimar --recognizer-function -l %s.%s %s.is_%s' % (m, provider, m, kind))
    run("type category enable larimar")
