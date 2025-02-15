#!/usr/bin/env python3
import environs
from structlog import get_logger
from pathlib import Path

from common import log_config as log_config
from egress.egress.egress import Egress


def main() -> None:
    env = environs.Env()
    data_path: Path = env.path('DATA_PATH')
    out_path: Path = env.path('OUT_PATH')
    log_level: str = env.log_level('LOG_LEVEL')
    log_config.configure(log_level)
    log = get_logger()
    log.debug(f'data_dir: {data_path}')
    log.debug(f'out_dir: {out_path}')

    egress = Egress(data_path, out_path)
    egress.upload()


if __name__ == '__main__':
    main()
