"""Harvey is now Andorinha.

This package only keeps the old ``harvey`` command and ``python -m harvey``
working for a while after the rename, including for clones that ran
``git pull`` without reinstalling. Everything lives in ``andorinha``.
"""

NOTICE = ("Harvey is now Andorinha. Run `pip install -e .` once, then use `andorinha` "
          "instead of `harvey`. The `harvey` command will be removed in a later release.")
