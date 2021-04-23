# Support for gvariant library
#
# Copyright (C) 2021 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later. See <http://www.gnu.org/licenses/gpl.html>

__all__ = [
    'array',
]

import ast
import os.path
import sys

TYPES = ('s', 'u')


# Exported methods, must have (*args) signature -------------------------------


def array(*args):
    if len(args) < 3:
        return usage(f"Missing required arguments in {args}",
                     "OPERATION ITEM_TYPE LIST_STRING [ITEMS...]")
    itemtype, newlist = _array(*args)
    print(f'@a{itemtype} {newlist!r}')


def _array(op: str, itemtype: str, strlist: str, *items) -> 'Tuple[str, list]':
    if itemtype not in TYPES:
        raise GVariantError(f"Not a supported item type {TYPES}: {itemtype}")

    if itemtype == 'u':
        items = list(map(int, items))

    # Shortcut for 'set' and 'clear', as they don't require handling strlist
    if op == 'set':
        return itemtype, list(items)
    elif op in ('clear', 'new'):
        return itemtype, []

    # type annotation for empty lists: '@as []'
    if strlist.startswith('@'):
        strlist = strlist.split(' ', 1)[1]
        # TODO: maybe set itemtype too?

    try:
        curlist = ast.literal_eval(strlist)
    except (SyntaxError, ValueError):
        raise GVariantError(f"Malformed list literal: {strlist!r}")
    if not isinstance(curlist, list):
        raise GVariantError(f"Not a list literal: {strlist!r}")

    # Use list instead of set to preserve order
    if op == 'remove':
        newlist = [_ for _ in curlist if _ not in items]
    elif op == 'include':
        newlist = curlist + [_ for _ in items if _ not in curlist]
    else:
        raise GVariantError(f"Not a valid list operation: {op!r}")

    return itemtype, newlist


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
