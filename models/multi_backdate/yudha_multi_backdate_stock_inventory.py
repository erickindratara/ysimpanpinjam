# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, fields, models, _
from  datetime import datetime
from odoo.exceptions import UserError,Warning
from odoo.tools import float_compare, float_is_zero

class yudha_multi_backdate_stock_inventory_update(models.Model):
    _inherit = 'stock.inventory'

    transfer_date = fields.Date('Inventory Date')
    remark = fields.Char('Remark')

    def action_validate(self):
        self.ensure_one()
        context = {
            'default_inventory_id': self.id,
        }
        action = {
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('yudha_multi_backdate.yudha_multi_backdate_view_change_invadjust_item').id, 'form')],
            'view_mode': 'form',
            'name': _('Inventory Lines Backdate'),
            'target': 'new',
            'res_model': 'change.inventory.adjust',
        }
        action['context'] = context
        return action

    def action_validate2(self):
        if not self.exists():
            return False
        self.ensure_one()
        if not self.user_has_groups('stock.group_stock_manager'):
            raise UserError(_("Only a stock manager can validate an inventory adjustment."))
        if self.state != 'confirm':
            raise UserError(_(
                "You can't validate the inventory '%s', maybe this inventory " +
                "has been already validated or isn't ready.") % (self.name))
        inventory_lines = self.line_ids.filtered(lambda l: l.product_id.tracking in ['lot', 'serial'] and not l.prod_lot_id and l.theoretical_qty != l.product_qty)
        lines = self.line_ids.filtered(lambda l: float_compare(l.product_qty, 1, precision_rounding=l.product_uom_id.rounding) > 0 and l.product_id.tracking == 'serial' and l.prod_lot_id)
        if inventory_lines and not lines:
            wiz_lines = [(0, 0, {'product_id': product.id, 'tracking': product.tracking}) for product in inventory_lines.mapped('product_id')]
            wiz = self.env['stock.track.confirmation'].create({'inventory_id': self.id, 'tracking_line_ids': wiz_lines})
            return {
                'name': _('Tracked Products in Inventory Adjustment'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'views': [(False, 'form')],
                'res_model': 'stock.track.confirmation',
                'target': 'new',
                'res_id': wiz.id,
            }
        self._action_done()
        self.line_ids._check_company()
        self._check_company()
        return True
