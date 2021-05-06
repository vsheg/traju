'''Small but useful.'''

from __future__ import annotations

__all__ = ['apart', 'vector_like']

from typing import *
import logging

logger = logging.getLogger(__name__)


def vector_like(arg) -> list:  # TODO: add type annotation
    '''Convert any object to vector-like.'''

    if not isinstance(arg, Iterable) or isinstance(arg, str):
        return [arg]
    return list(arg)


def apart(func: Callable[..., bool], it: Iterable) -> tuple[Iterable, Iterable]:
    '''Apply test function `func` to every elements in iterable collection `it` and
    return tuple of 2 lists with negative and positive outcomes respectively.'''

    it = iter(it)
    positives = []
    negatives = []
    for el in it:
        if func(el):
            positives.append(el)
        else:
            negatives.append(el)
    return (negatives, positives)
