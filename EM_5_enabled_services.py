#!/usr/bin/env python
# EM-5 collect all services and present the Enabled services to the end user
# Collecting all services here to present all services in the dashboard

import pandas as pd
import json
import utils.common_functions as cf
from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

from utils.database_class import DatabaseManager

logger.info('Getting the Enabled Services data')

powershell_command = 'Get-Service | Select-Object DisplayName, ServiceName, StartType | ConvertTo-Csv | ConvertFrom-Csv | ConvertTo-Json'
output = cf.run_powershell_command(powershell_command)

try:
    df = pd.DataFrame(json.loads(output['output']))
except Exception as e:
    logger.error(f'Could not load dataframe from returned enabled services: {e}')

with DatabaseManager() as db:
    db.add_new_rows('em_5_enabled_services', df, ['DisplayName', 'ServiceName', 'StartType'])
    db.remove_old_rows('em_5_enabled_services', df, ['DisplayName', 'ServiceName', 'StartType'])

logger.info('Finished collecting the Enabled Services data')