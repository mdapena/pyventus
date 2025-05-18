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
        logger.critical(action="Action", msg="Critical%(levelcolor)scolor")
        logger.error(action="Action", msg="Error %(levelcolor)s color")
        logger.warning(action="Action", msg="Warning %(levelcolor)scolor")
        logger.info(action="Action", msg="Info%(levelcolor)s color")
        logger.debug(action="Action", msg=f"Debug %(levelcolor)scolor ({'Extra'}).")
