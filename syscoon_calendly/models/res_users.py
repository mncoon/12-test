#See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit= 'res.users'

    calendly_token = fields.Char('Calendly Token')
    calendly_token_active = fields.Boolean('Calendly Token Active')
    calendly_email = fields.Char('Calendly Email')
    calendly_webkooks_id = fields.Char('Webook ID')
    calendly_url = fields.Char('Calendly URL')

    def calendly_activate_token(self):
        calendly = Calendly(self.calendly_token)
        result = calendly.echo()
        if result.get('email'):
            self.write({
                'calendly_token_active': True,
                'calendly_email': result['email']
            })
        return

    def calendly_activate_webhooks(self):
        IrConfig = self.env['ir.config_parameter'].sudo()
        calendly = Calendly(self.calendly_token)
        result = calendly.create_webhook('https://syscoon.com/calendly')
        #result = calendly.create_webhook(IrConfig.get_param('web.base.url') + '/calendly')
        if result.get('id'):
            self.write({
                'calendly_webkooks_id': result['id'],
            })
        elif result.get('message'):
            raise UserError(_('Error: %s' % result['message']))
        return

    def calendly_about(self):
        calendly = Calendly(self.calendly_token)
        hooks = calendly.list_webhooks()
        about = calendly.about()
        vals = {}
        if hooks['data']:
            vals['calendly_webkooks_id'] = hooks['data']['id']
        if about['data'].get('attributes'):
            if about['data']['attributes'].get('url'):
                vals['calendly_url'] = about['data']['attributes']['url']
            if about['data']['attributes'].get('email'):
                vals['calendly_email'] = about['data']['attributes']['email']
        if vals:
            self.write(vals)
        else:
            raise UserError(_('No Values received. Please use "Activate Token" first.'))
        return

    def calendly_deactivate_webhooks(self):
        calendly = Calendly(self.calendly_token)
        result = calendly.remove_webhook(self.calendly_webkooks_id)
        if result.get('success') and result['success'] == True:
            self.write({
                'calendly_webkooks_id': '',
                'calendly_email': '',
                'calendly_token_active': False,
                'calendly_url': '',
            })
        elif result.get('message'):
            raise UserError(_('Error: %s' % result['message']))
        return



#See LICENSE file for full copyright and licensing details.

import requests
from json import JSONDecodeError

BASE="https://calendly.com/api/v1"
WEBHOOK=f"{BASE}/hooks"
ME=f"{BASE}/users/me"
ECHO=f"{BASE}/echo"


class Calendly(object):

    event_types_def = {
        "canceled": "invitee.canceled",
        "created": "invitee.created"
    }

    def __init__(self, api_key):
        self.request = CaRequest(api_key)

    def create_webhook(self, user_url, event_types=["canceled", "created"]):
        events = [self.event_types_def[event_type] for event_type in event_types]
        data = {'url': user_url, 'events': events}
        response = self.request.post(WEBHOOK, data)
        return response.json()

    def list_webhooks(self):
        response = self.request.get(WEBHOOK)
        return response.json()

    def remove_webhook(self, id):
        dict_response = {'success': True}
        response = self.request.delete(f'{WEBHOOK}/{id}')
        dict_response['success'] = response.status_code == 200
        if response.status_code == 200:
            json_response = {}
        else:
            try:
                json_response = response.json()
            except JSONDecodeError:
                json_response = {}
        dict_response.update(json_response)
        return dict_response

    def get_webhook(self, id):
        response = self.request.get(f'{WEBHOOK}/{id}')
        return response.json()

    def about(self):
        response = self.request.get(ME)
        return response.json()

    def event_types(self):
        response = self.request.get(f'{ME}/event_types')
        return response.json()

    def echo(self):
        response = self.request.get(ECHO)
        return response.json()


class CaRequest(object):

    def __init__(self, token):
        self.headers = {'X-TOKEN': token}

    def process_request(self, method, url, data=None):
        request_method = getattr(requests, method)
        return request_method(url, json=data, headers=self.headers)

    def get(self, url, data=None):
        return self.process_request('get', url, data)

    def post(self, url, data=None):
        return self.process_request('post', url, data)

    def delete(self, url, data=None):
        return self.process_request('delete', url, data)

    def put(self, url, data=None):
        return self.process_request('put', url, data)

