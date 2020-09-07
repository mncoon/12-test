#See LICENSE file for full copyright and licensing details.

import logging
import requests
import json

from odoo import http

_logger = logging.getLogger(__name__)

class CalendlyWeb(http.Controller):
    
    @http.route('/calendly', type='json', auth="none", methods=['POST'], cors="*", csrf=False)
    def get_result(self, **kw):
        _logger.info('CONNECTION SUCCESSFUL')
        _logger.info(http.request.jsonrequest)
        print(http.request.jsonrequest)
        return
