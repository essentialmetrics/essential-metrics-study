#!/usr/bin/env python
# EM-13 - Ensure antivirus is working with EICAR file
# The EICAR file is used to validate antivirus software is working as expected
# It contains a known string which most antivirus providers have implemented as a known bad file for testing
# See more here: https://www.eicar.org/download-anti-malware-testfile/

import pandas as pd
from datetime import datetime
import pytz

import utils.common_functions as cf
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

from utils.database_class import DatabaseManager

cf.check_data_freshness('em_13_eicar_removed')

logger.info('Writing the EICAR file to the filesystem')

local_timestamp = datetime.now()
utc_timestamp = local_timestamp.astimezone(pytz.utc)
timestamp = utc_timestamp.strftime("%Y-%m-%d_%H-%M-%S")

eicar_file = f'EICAR-{timestamp}.txt'

with open(f'C:\\opt\\essential-metrics\\{eicar_file}', 'w') as file:
    file.write(r'X5O!P%@AP[4\PZX54(P^)7CC)7}$' + 'EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*')

try:
    with open(f'C:\\opt\\essential-metrics\\EICAR-{timestamp}.txt', 'r') as file:
        file_contents = file.read()
        logger.info(f'File was ALLOWED to be open, Antivirus is NOT working')
        eicar_removed = 'Failed'
except Exception as e:
    logger.info(f'File was not allowed to be open, Antivirus working: {e}')
    eicar_removed = 'Success'

try:
    data = [{'File': eicar_file, 'Removed': eicar_removed}]
    df = pd.DataFrame(data)
except Exception as e:
    logger.error(f'Could not convert data into dataframe: {e}')

with DatabaseManager() as db:
    df.to_sql('em_13_eicar_removed', db.conn, if_exists='append', index=False)