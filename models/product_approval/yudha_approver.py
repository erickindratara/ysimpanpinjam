# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class YudhaListApprover(models.Model):
    _name = 'approver.approver'

    group_id = fields.Many2one('res.groups', string="Groups")
    user_id = fields.Many2one('res.users', String="User")
    date = fields.Datetime(String="Datetime")
    state = fields.Selection([('waiting', "Waiting to Approve"), ('approve', "Approved"),
                              ('reject', "Rejected")], default='waiting')
    product_id = fields.Many2one('product.product', String='Product ID')
    product_tmpl_id = fields.Many2one('product.template', string='Product Template ID')
