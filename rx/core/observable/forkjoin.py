from typing import Any, List, Optional, Tuple, cast

from rx.core import Observable, abc
from rx.disposable import CompositeDisposable, SingleAssignmentDisposable


def fork_join_(*sources: Observable[Any]) -> Observable[Tuple[Any, ...]]:
    """Wait for observables to complete and then combine last values
    they emitted into a tuple. Whenever any of that observables completes
    without emitting any value, result sequence will complete at that moment as well.

    Examples:
        >>> obs = rx.fork_join(obs1, obs2, obs3)

    Returns:
        An observable sequence containing the result of combining last element from
        each source in given sequence.
    """

    parent = sources[0]

    def subscribe(
        observer: abc.ObserverBase[Tuple[Any, ...]],
        scheduler: Optional[abc.SchedulerBase] = None,
    ) -> abc.DisposableBase:
        n = len(sources)
        values = [None] * n
        is_done = [False] * n
        has_value = [False] * n

        def done(i: int):
            is_done[i] = True

            if not has_value[i]:
                observer.on_completed()
                return

            if all(is_done):
                if all(has_value):
                    observer.on_next(tuple(values))
                    observer.on_completed()
                else:
                    observer.on_completed()

        subscriptions: List[SingleAssignmentDisposable] = [
            cast(SingleAssignmentDisposable, None)
        ] * n

        def _subscribe(i: int):
            subscriptions[i] = SingleAssignmentDisposable()

            def on_next(value: Any) -> None:
                with parent.lock:
                    values[i] = value
                    has_value[i] = True

            def on_completed() -> None:
                with parent.lock:
                    done(i)

            subscriptions[i].disposable = sources[i].subscribe_(
                on_next, observer.on_error, on_completed, scheduler
            )

        for i in range(n):
            _subscribe(i)
        return CompositeDisposable(subscriptions)

    return Observable(subscribe)


__all__ = ["fork_join_"]
