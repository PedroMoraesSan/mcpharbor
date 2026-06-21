from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Success(Generic[T]):
    value: T


@dataclass(frozen=True, slots=True)
class Failure:
    error: str
    code: str = "error"


Result = Success[T] | Failure


def is_success(result: Result[T]) -> bool:
    return isinstance(result, Success)


def is_failure(result: Result[T]) -> bool:
    return isinstance(result, Failure)
