from typing import Any, Callable, Optional, TypeVar

from rx.core import Observable, GroupedObservable, typing
from rx.subject import Subject

_T = TypeVar("_T")
_TKey = TypeVar("_TKey")
_TValue = TypeVar("_TValue")

# pylint: disable=import-outside-toplevel


def group_by_(
    key_mapper: typing.Mapper[_T, _TKey],
    element_mapper: Optional[typing.Mapper[_T, _TValue]] = None,
    subject_mapper: Optional[Callable[[], Subject[_TValue]]] = None,
) -> Callable[[Observable[_T]], Observable[GroupedObservable[_TKey, _TValue]]]:
    from rx import operators as ops

    def duration_mapper(_: GroupedObservable[Any, Any]) -> Observable[Any]:
        import rx

        return rx.never()

    return ops.group_by_until(
        key_mapper, element_mapper, duration_mapper, subject_mapper
    )


__all__ = ["group_by_"]
