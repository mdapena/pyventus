from pyventus.core.loggers import Logger


class TestLogger:
    # =================================
    # Test Cases for creation
    # =================================

    def test_creation(self) -> None:
        # Arrange | Act
        logger = Logger(name="New Logger", debug=True)

        # Assert
        assert logger and logger.debug_enabled
        logger.info("info")
        logger.debug("debug")
        logger.error("error")
        logger.warning("warning")
