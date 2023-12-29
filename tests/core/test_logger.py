from pyventus.core.loggers import Logger


class TestLogger:
    def test_creation(self):
        # Arrange | Act
        logger = Logger(name="New Logger", debug=True)

        # Assert
        assert logger
        assert logger.debug_enabled
        logger.info("info")
        logger.debug("debug")
        logger.error("error")
        logger.warning("warning")
