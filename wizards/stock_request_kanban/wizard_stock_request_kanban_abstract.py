# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import fields, models, _


class WizardStockRequestOrderKanbanAbstract(models.AbstractModel):
    _name = "wizard.stock.request.kanban.abstract"
    _inherit = "barcodes.barcode_events_mixin"

    kanban_id = fields.Many2one(
        'stock.request.kanban',
        readonly=True,
    )
    status = fields.Text(
        readonly=True,
        default="Start scanning",
    )
    status_state = fields.Integer(
        default=0,
        readonly=True,
    )

    def on_barcode_scanned(self, barcode):
        self.kanban_id = self.env['stock.request.kanban'].search_barcode(
            barcode)
        if not self.kanban_id:
            self.status = _("Barcode %s does not correspond to any "
                            "Kanban. Try with another barcode or "
                            "press Close to finish scanning.") % barcode
            self.status_state = 1
            return
        if self.validate_kanban(barcode):
            self.status_state = 0
            self.barcode_ending()

    def barcode_ending(self):
        pass

    def validate_kanban(self, barcode):
        '''
        It must return True if the kanban is valid, False otherwise
        :param barcode:
        :return:
        '''
        return True
