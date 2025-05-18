from logging import DEBUG
from typing import Any

import pytest
from pyventus.core.loggers import Logger, StdOutLogger


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
        StdOutLogger.config(level=DEBUG)
        logger = Logger(source=source, debug=True)

        # Assert
        assert logger and logger.debug_enabled
        logger.critical("critical")
        logger.error("error")
        logger.warning("warning")
        logger.info("info")
        logger.debug("debug")
