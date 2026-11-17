"""The old ``harvey`` command: says it moved, then runs ``andorinha``."""

import sys
from pathlib import Path

from harvey import NOTICE


def _find_andorinha():
    """An editable install made before the rename only maps the ``harvey``
    package, so after a plain ``git pull`` Python can't see ``andorinha``
    until ``pip install -e .`` runs again. It sits next to this package in
    the same checkout, so point Python at the checkout."""
    try:
        import andorinha  # noqa: F401
    except ModuleNotFoundError:
        checkout = Path(__file__).resolve().parent.parent
        if (checkout / "andorinha" / "__init__.py").is_file():
            sys.path.insert(0, str(checkout))


def main():
    print(NOTICE, file=sys.stderr)
    _find_andorinha()
    from andorinha.cli import main as andorinha_main
    sys.argv[0] = "andorinha"
    return andorinha_main()
