# Support for gvariant library
#
# Copyright (C) 2021 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>

__all__ = [
    'array',
    'quote',
    'unquote',
]

import ast
import os.path
import sys

try:
    from gi.repository import GLib
except ImportError:
    GLib = None


STRINGS  = ('s', 'o', 'g')
INTEGERS = ('y', 'n', 'q', 'i', 'u', 'x', 't', 'h')
BASIC_TYPES = {
    'd': float,
    'b': lambda x: x == 'true'
}
BASIC_TYPES.update({_: str for _ in STRINGS})
BASIC_TYPES.update({_: int for _ in INTEGERS})


# Exported methods, must have (*args) signature -------------------------------

def quote(*args):
    """Print the GVariant textual representation of a string"""
    if not len(args) == 1:
        return usage(f"Missing or extra arguments: {args}", "STRING")
    print(repr(args[0]))  # print(gvariant_repr(args[0], 's'))


def unquote(*args):
    """Print a string given its GVariant textual representation"""
    if not len(args) == 1:
        return usage(f"Missing or extra arguments: {args}", "STRING")
    print(parse_repr(args[0], str))  # print(parse_gvariant(args[0], 's'))


def array(*args):
    if len(args) < 3:
        return usage(f"Missing required arguments in {args}",
                     "OPERATION ITEM_TYPE LIST_STRING [ITEMS...]")
    newlist = _array(*args)
    # strictly speaking, GVariant only includes type annotation for empty arrays,
    # but since we're not thoroughly testing each item, add it as safety measure
    print(f'@a{args[1]} {newlist!r}')  # print(gvariant_repr(newlist, 'a' + args[1]))


def _array(op: str, itemtype: str, strlist: str, *items) -> list:
    if itemtype not in BASIC_TYPES:
        raise GVariantError("Not a supported item type"
                            f" {BASIC_TYPES.keys()}: {itemtype!r}")

    # Shortcut for clear/new, as it ignores items
    # (maybe should raise exception if there are items?)
    if op in ('clear', 'new'):
        return []

    items = list(map(BASIC_TYPES[itemtype], items))

    # Shortcut for 'set', as it doesn't handle strlist
    if op == 'set':
        return items

    # Type annotation. For empty arrays of strings, '@as []'
    if strlist.startswith('@'):
        vartype, strlist = strlist.split(' ', 1)
        if vartype != typeanno:
            raise GVariantError(f"Array type mismatch: LIST_STRING has {vartype!r},"
                                f" but ITEM_TYPE implies {annotation!r}")

    curlist = parse_repr(strlist, list)  # parse_gvariant(strlist, 'a'+itemtype)

    # Use list instead of set to preserve order
    if op == 'remove':
        return [_ for _ in curlist if _ not in items]
    elif op == 'include':
        return curlist + [_ for _ in items if _ not in curlist]

    raise GVariantError(f"Not a valid list operation: {op!r}")


# Supporting functions ---------------------------------------------------------

def parse_repr(text, cls=None):
    """Return a Python builtin object from a literal expression string

    Useful for reverting repr(obj) if obj is a Python builtin, as the textual
    representation of all builtins, as given by their repr(), is always a literal
    expression evaluating back to themselves. Hence the function name.
    """
    try:
        obj = ast.literal_eval(text)
    except (SyntaxError, ValueError):
        raise GVariantError(f"Malformed literal: {text!r}")
    if cls and not isinstance(obj, cls):
        raise GVariantError(f"Not a {cls.__name__} literal: {text!r}")
    return obj


def parse_gvariant(text: str, vartype: str or None = None):
    """Return a Python builtin object from a GVariant textual representation

    To revert, in the general case vartype is reused and must not be None:
    text == str(GLib.Variant(vartype, parse_gvariant(text, vartype)))
        In some cases can be reverted simply by: text == repr(parse_gvariant(text))

    GVariant mini-reference:

    GLib.Variant(type: str, value: object) -> GLib.Variant
        - type must not be falsy and is not inferred from object
        - Not all objects are valid values. Most if not all Python builtins are.
          Heterogeneous lists are not.

    GLib.Variant.parse(type: VariantType or None, text: str) -> GLib.Variant
        - If type is None it infers from text, in which case if text represents
          an empty array it must be prefixed with type annotation: '@as []'

    str(GLib.Variant.parse(None, repr(obj))) == repr(obj)
        - Unless obj is an empty list, when its str() prepends the type annotation
          (and in this case can't pass None as type anyway)
        - Assuming a valid obj and also a repr(obj) that evaluates as itself.

    str(gvariant) == gvariant.print_(True)
        - Despite the docs, only actually include type annotation for empty arrays
    """
    if not GLib:
        raise GVariantError(f"Support for parsing GVariants"
                            " requires Python GLib bindings")
    if vartype:
        vartype = GLib.VariantType.new(vartype)
    else:
        vartype = None  # covers the case when vartype is empty string

    return parse_repr(GLib.Variant.parse(vartype, text).print_(False))


def gvariant_repr(obj: object, vartype: str):
    """Return the GVariant textual representation of an object"""
    if not GLib:
        raise GVariantError(f"Support for parsing GVariants"
                            " requires Python GLib bindings")
    return str(GLib.Variant(vartype, obj))


# Dispatching engine -----------------------------------------------------------

class GVariantError(ValueError):
    def __repr__(self): return str(self)


def usage(msg="", sig=""):
    msg = f"{msg}\n" if msg else ""
    if sig:
        sig = f"{sys.argv[1]} {sig}"
    else:
        msg = f"{msg}Available methods: {', '.join(__all__)}\n"
        sig = "METHOD [ARGS...]"
    return f"{msg}Usage: {os.path.basename(sys.argv[0])} {sig}"


# Dispatcher
def main(argv):
    if not argv:
        return usage("Missing required METHOD")

    name, *args = argv
    if name in ('-h', '--help', 'help'):
        print(usage())
        return

    if name not in __all__:
        # nice try, smartass
        return usage(f"Invalid method: {name}")

    return globals()[name](*args)


try:
    sys.exit(main(sys.argv[1:]))
except Exception as e:
    sys.exit(f'GVariant error: {e!r}')
