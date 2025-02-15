#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import datetime
import dateutil
from dateutil.relativedelta import relativedelta
import pandas as pd

from structlog import get_logger

log = get_logger()


class Egress:

    def __init__(self, data_path: Path, out_path: Path) -> None:
        """
        Constructor.

        :param data_path: The data path.
        :param out_path: The output path for writing results.
        """
        self.data_path = data_path
        self.out_path = out_path
        self.idq_length = 6
        self.domain_index = 1
        self.site_index = 2
        self.date_index = 10
        self.package_index = 11
        self.filename_delimiter = "."
        self.domain_generic = "DOM"
        self.site_generic = "SITE"
        self.date_delimiter = "-"
        self.date_format = '%Y%m%dT%H%M%S'
        self.date_range_delimiter = "--"
        self.s3_prefix = "https://" + os.environ['CUSTOM_ENDPOINT'] + "/" + os.environ['AMAZON_BUCKET'] + "/"

    def upload(self) -> None:
        
        # object IDs by file
        objectIdByFile = {}

        try:
            for root, dirs, files in os.walk(str(self.data_path)):
                for filename in files:
                    # load the manifest
                    if 'manifest' in filename:
                        manifest = pd.read_csv(os.path.join(root, filename))
                        continue
                    file_path = Path(root, filename)
                    filename_parts = filename.split(self.filename_delimiter)
                    site = filename_parts[self.site_index]
                    # parse out the idq
                    filename_parts[self.domain_index] = self.domain_generic
                    filename_parts[self.site_index] = self.site_generic
                    idq = self.filename_delimiter.join(filename_parts[:self.idq_length])
                    # construct date range field
                    date = filename_parts[self.date_index]
                    date_parts = date.split(self.date_delimiter)
                    year = int(date_parts[0])
                    month = int(date_parts[1])
                    start_date = datetime.date(year, month, 1)
                    next_month = start_date + relativedelta(days=+32)
                    end_date = datetime.date(next_month.year, next_month.month, 1)
                    date_range = start_date.strftime(self.date_format) + self.date_range_delimiter + end_date.strftime(self.date_format)
                    package = filename_parts[self.package_index]
                    # construct link filename
                    base_path = os.path.join(idq, site, date_range, package, filename)
                    link_path = Path(self.out_path, base_path)
                    log.debug(f'source_path: {file_path} link_path: {link_path}')
                    link_path.parent.mkdir(parents=True, exist_ok=True)
                    # construct object ID
                    objectIdByFile[filename] = self.s3_prefix + base_path
                    if not link_path.exists():
                        link_path.symlink_to(file_path)
            for key in objectIdByFile:
                manifest.loc[manifest['file'] == key, 'objectId'] = objectIdByFile[key]
            manifest.to_csv(os.path.join(self.out_path, idq, site, date_range, 'manifest.csv'), index=False)
        except Exception:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            log.error("Exception at line " + str(exc_tb.tb_lineno) + ": " + str(sys.exc_info()))
