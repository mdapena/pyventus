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
        logger.critical(action="Action:", msg="Critical %(levelcolor)slevel%(defaultcolor)s message.")
        logger.error(action="Action:", msg="Error %(levelcolor)slevel%(defaultcolor)s message.")
        logger.warning(action="Action:", msg="Warning %(levelcolor)slevel%(defaultcolor)s message.")
        logger.info(action="Action:", msg="Info %(levelcolor)slevel%(defaultcolor)s message.")
        logger.debug(action="Action:", msg="Debug %(levelcolor)slevel%(defaultcolor)s message.")
