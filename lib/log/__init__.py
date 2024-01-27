import logging
import logging.config
import os
import pathlib
import yaml

class LoggingClass:
    _logger: logging.Logger
    _logging_class_parameters: dict = {
        'logconfig_use': pathlib.Path,
        'logconfig_file': pathlib.Path,
    }

    def __init__(self, **kwargs) -> None:
        for kw in self._logging_class_parameters:
            assert(kw in kwargs)
            assert(type(kwargs[kw] == self._logging_class_parameters[kw]))

        assert(os.path.exists(kwargs['logconfig_file']))

        with open(kwargs['logconfig_file'], 'r') as fd:
            log_config = yaml.unsafe_load(fd.read())

        assert(type(log_config) == dict)
        assert('loggers' in log_config)
        assert(type(log_config['loggers']) == dict)
        assert(kwargs['logconfig_use'] in log_config['loggers'])

        logging.config.dictConfig(log_config)
        self._logger = logging.getLogger(kwargs['logconfig_use'])

    def print_info(self, *args) -> None:
        assert(self._logger != None)
        assert(len(args) > 0)

        self._logger.info(*args)

    def print_warning(self, *args) -> None:
        assert(self._logger != None)
        assert(len(args) > 0)

        self._logger.warning(*args)
