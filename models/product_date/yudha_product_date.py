# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date


class YudhaProductTemplateDate(models.Model):
    _inherit = 'product.template'

    @api.model
    def default_date_domain(self):
        today_date = date.today()

        return [('date', '>=', today_date)]

    product_date = fields.Many2many('product.date', string="Product Date",
                                    domain=default_date_domain)
    outlet = fields.Selection([('all', 'All Unit Location'),
                               ('outlet', 'Unit Location')], string='Apply On', default='all')
    outlet_type_ids = fields.Many2many('stock.warehouse', string='Unit Location')
    is_certain_date = fields.Boolean('Available for Certain Date', default=False, copy=False)


class YudhaProductDate(models.Model):
    _name = 'product.date'
    _description = 'Product Date'
    _order = 'id'

    name = fields.Char(string="Date")
    date = fields.Date(string="Order Date", required=True)
    product_lists = fields.Many2many('product.template', string="Products")

    @api.onchange('date')
    def date_change(self):
        for me in self:
            me.name = str(me.date)
            if me.date:
                if me.date < date.today():
                    raise UserError(_("You can't select an expired date"))

    @api.model
    def create(self, vals):
        get_product_date = self.env['product.date'].search([])
        if any(data.name == vals.get('name') for data in get_product_date):
            raise UserError(_('You already have a record with date %s' % vals.get('name')))

        return super(YudhaProductDate, self).create(vals)

    def write(self, vals):
        get_product_date = self.env['product.date'].search([])
        if 'date' in vals:
            if any(data.name == vals.get('name') for data in get_product_date):
                raise UserError(_('You already have a record with date %s' % vals.get('name')))

        return super(YudhaProductDate, self).write(vals)
