#See LICENSE file for full copyright and licensing details.

import logging

from odoo import http

_logger = logging.getLogger(__name__)

class CalendlyWeb(http.Controller):
    
    @http.route("/calendly", auth="public", type= 'http')
    def get_result(self, **kwargs):
        _logger.warning(**kwargs)
        print(**kwargs)
        return
