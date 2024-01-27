#!/usr/bin/env python3

import argparse
import os
import pathlib
import yaml
import yaml.parser

from lib.server import NURDpasteAPI # pyright: ignore
from lib.backend import RedisBackend # pyright: ignore

DEFAULT_CONFIG = 'config.yml'

def load_and_validate_config(config_file: pathlib.Path) -> dict:
    assert config_file != ""
    assert os.path.exists(config_file)

    config = None
    with open(config_file, 'r') as fd:
        try:
            config = yaml.load(fd, yaml.SafeLoader)
        except yaml.parser.ParserError as errmsg:
            print(f'Failed to parse {config_file}: {errmsg}')
            return {}

    assert type(config) == dict
    assert 'api' in config
    assert 'redis' in config
    assert 'logging' in config

    assert 'bind_address' in config['api']
    assert type(config['api']['bind_address']) == str

    assert 'bind_port' in config['api']
    assert type(config['api']['bind_port']) == int

    assert 'max_size' in config['api']
    assert type(config['api']['max_size']) == int

    assert 'default_ttl' in config['api']
    assert type(config['api']['default_ttl']) == int

    assert 'host' in config['redis']
    assert type(config['redis']['host']) == str

    assert 'port' in config['redis']
    assert type(config['redis']['port']) == int

    assert 'logger' in config['logging']
    assert type(config['logging']['logger']) == str
    assert config['logging']['logger'] != ""

    assert 'config' in config['logging']
    assert type(config['logging']['config']) == str

    return config

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', dest='config_file', type=pathlib.Path, default=DEFAULT_CONFIG, help=f'Config file to use ({DEFAULT_CONFIG})')
    args = parser.parse_args()

    config = load_and_validate_config(args.config_file)

    redis_backend = RedisBackend(
        host=config['redis']['host'],
        port=config['redis']['port'],
        logconfig_use=config['logging']['logger'],
        logconfig_file=config['logging']['config'],
    )

    nurdpaste_api = NURDpasteAPI(
        bind_ip=config['api']['bind_address'],
        bind_port=config['api']['bind_port'],
        max_size=config['api']['max_size'],
        default_ttl=config['api']['default_ttl'],
        logconfig_use=config['logging']['logger'],
        logconfig_file=config['logging']['config'],
        frontend=config['api']['frontend'],
        backend=redis_backend,
    )

    try:
        nurdpaste_api.run()
    except KeyboardInterrupt:
        pass
