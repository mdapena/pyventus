import pytest

from pyventus.core.utils import is_loop_running


class TestAsyncIOUtils:

    def test_is_loop_running_when_no_running_loop(self) -> None:
        # Arrange, Act, Assert
        loop_running: bool = is_loop_running()
        assert not loop_running

    @pytest.mark.asyncio
    async def test_is_loop_running_when_running_loop(self) -> None:
        # Arrange, Act, Assert
        loop_running: bool = is_loop_running()
        assert loop_running
