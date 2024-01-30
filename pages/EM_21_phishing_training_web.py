#!/usr/bin/env python
# EM - 21 - Phishing training

import dash
from dash import html

from utils.logger_config  import configure_logger

logger = configure_logger(__name__)

logger.info('inside em 21')

'''
layout = html.Div([
    html.Iframe(src="assets/external/cyber-security-for-small-organisations-scorm12/scormcontent/index.html", target="_blank", width="100%", height="800")
])
'''
from flask import request
import json
from app import app

@app.server.route('/track_scorm', methods=['POST'])
def track_scorm():
    data = json.loads(request.data)
    # Process and store data
    print(data)
    logger.info(f'Inside scorm')
    return 'Success'
