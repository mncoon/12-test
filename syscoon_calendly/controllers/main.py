#See LICENSE file for full copyright and licensing details.

import logging
import requests
import json
import dateutil
from datetime import datetime

from odoo import http

_logger = logging.getLogger(__name__)

class CalendlyWeb(http.Controller):
    
    @http.route('/calendly', type='json', auth="none", methods=['POST'], cors="*", csrf=False)
    def get_result(self, **kw):
        _logger.info('CONNECTION SUCCESSFUL')
        _logger.info(http.request.jsonrequest)
        data = http.request.jsonrequest
        event = {}
        if data['event'] == 'invitee.created':
            if data['payload']['event']:
                event['start'] = dateutil.parser.parse(data['payload']['event']['start_time']).strftime('%Y-%m-%d %H:%M:%S')
                event['stop'] = dateutil.parser.parse(data['payload']['event']['end_time']).strftime('%Y-%m-%d %H:%M:%S')
                user_id = http.request.env['res.users'].sudo().search([('calendly_email', '=', data['payload']['event']['extended_assigned_to'][0]['email'])])
                event['user_id'] = user_id.id
            if data['payload']['tracking']['utm_source']:
                source = data['payload']['tracking']['utm_source'].split(',')
                source_id = http.request.env[source[0]].sudo().browse([int(source[1])])
                event['res_id'] = source[1]
                event['opportunity_id'] = source[1]
                event['res_model_id'] = http.request.env['ir.model'].sudo().search([('model', '=', source[0])]).id
                event['partner_id'] = source_id.partner_id.id
                event['partner_ids'] = [(4, user_id.partner_id.id)] 
            if data['payload']['event_type']:
                event['name'] = data['payload']['event_type']['name'] + ' ' + source_id.name
                event['duration'] = float(data['payload']['event_type']['duration']) / 60
                alarm = http.request.env['ir.model.data'].get_object_reference('calendar', 'alarm_notif_1')
                event['alarm_ids'] = [(4, alarm[1])]
        if event:
            http.request.env['calendar.event'].sudo().create(event)
        return http.Response("OK", status=200)
