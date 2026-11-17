"""Andorinha is a modified version of Sellbird.

This package only keeps the ``sellbird`` command and ``python -m sellbird``
working for people whose checkout ran under the upstream name before the
fork, including clones that pulled without reinstalling. Everything lives in
``andorinha``.
"""

NOTICE = ("This checkout is now Andorinha, a modified version of Sellbird. Run "
          "`pip install -e .` once, then use `andorinha` instead of `sellbird`.")
