# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import fields, models, _


class WizardStockRequestOrderKanbanAbstract(models.TransientModel):
    _name = "wizard.stock.inventory.kanban"
    _inherit = "wizard.stock.request.kanban.abstract"

    inventory_kanban_id = fields.Many2one(
        'stock.inventory.kanban',
        readonly=True,
    )

    def barcode_ending(self):
        super().barcode_ending()
        self.inventory_kanban_id.write({
            'scanned_kanban_ids': [(4, self.kanban_id.id)]
        })

    def validate_kanban(self, barcode):
        res = super().validate_kanban(barcode)
        if not self.inventory_kanban_id.kanban_ids.filtered(
            lambda r: r == self.kanban_id
        ):
            self.status = _("Barcode %s is not in the inventory") % barcode
            self.status_state = 1
            return False
        if self.inventory_kanban_id.scanned_kanban_ids.filtered(
            lambda r: r == self.kanban_id
        ):
            self.status = _("Barcode %s is already scanned") % barcode
            self.status_state = 1
            return False
        return res
