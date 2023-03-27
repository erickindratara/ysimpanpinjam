# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import models, fields, api, _

class YudhaLoginSecurity_settings(models.TransientModel):
    _inherit = 'res.config.settings'

    allowed_login_attempts = fields.Integer('Maximum Login Attempt',default=3,required=True)
    used_blocked = fields.Boolean('Blocked Access')
    blocked_by = fields.Selection([('by_ip','IP Address'),
                                      ('by_country','Country/Login Location'),
                                   ('by_user','User Name')],default='by_ip',string='Blocked By')
    blocked_by_ip = fields.Char('ip Blocked')
    blocked_by_country = fields.Many2one('res.country','Country Blocked')
    blocked_by_username = fields.Many2one('res.users','User Name')

    @api.onchange('used_blocked')
    def onchange_used_blocked(self):
        if self.used_blocked == True:
            self.allowed_login_attempts = 3
            self.blocked_by = 'by_ip'

    @api.model
    def get_values(self):
        res = super(YudhaLoginSecurity_settings, self).get_values()
        ctr_id = int(self.env['ir.config_parameter'].sudo().get_param('blocked_by_country'))
        users_id = int(self.env['ir.config_parameter'].sudo().get_param('blocked_by_username'))
        login_cnt = int(self.env['ir.config_parameter'].sudo().get_param('allowed_login_attempts'))
        res.update(
            allowed_login_attempts= login_cnt,
            used_blocked=self.env['ir.config_parameter'].sudo().get_param('used_blocked'),
            blocked_by=self.env['ir.config_parameter'].sudo().get_param('blocked_by'),
            blocked_by_ip=self.env['ir.config_parameter'].sudo().get_param('blocked_by_ip'),
            blocked_by_country=ctr_id,
            blocked_by_username = users_id,
        )
        return res

    def set_values(self):
        super(YudhaLoginSecurity_settings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('allowed_login_attempts', self.allowed_login_attempts or False)
        param.set_param('used_blocked', self.used_blocked or False)
        param.set_param('blocked_by', self.blocked_by or False)
        param.set_param('blocked_by_ip', self.blocked_by_ip or False)
        param.set_param('blocked_by_country',self.blocked_by_country.id or False)
        param.set_param('blocked_by_username', self.blocked_by_username.id or False)

class YudhaLoginSecurity_loger(models.Model):
    _inherit = 'res.users'

    login_attempt = fields.Integer('User Login Count',default=0)