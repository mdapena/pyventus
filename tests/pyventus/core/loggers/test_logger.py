from typing import Any

import pytest
from pyventus.core.loggers import Logger


class TestLogger:
    # =================================
    # Test Cases for creation
    # =================================

    @pytest.mark.parametrize(
        ["source"],
        [
            (None,),
            ("String",),
            (object,),
            (object(),),
        ],
    )
    def test_creation(self, source: Any) -> None:
        # Arrange | Act
        logger = Logger(source=source, debug=True)

        # Assert
        assert logger and logger.debug_enabled
        logger.info("info")
        logger.debug("debug")
        logger.error("error")
        logger.warning("warning")
