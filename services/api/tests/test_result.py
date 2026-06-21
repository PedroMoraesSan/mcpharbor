from shared.result import Failure, Success, is_failure, is_success


def test_success():
    result = Success(value=42)
    assert is_success(result)
    assert not is_failure(result)
    assert result.value == 42


def test_failure():
    result = Failure(error="test error", code="test")
    assert is_failure(result)
    assert not is_success(result)
    assert result.error == "test error"
