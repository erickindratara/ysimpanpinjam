# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime


class yudhaProductProduct(models.Model):
    _inherit = 'product.product'

    state = fields.Selection([('draft', "Draft"), ('to_approve', "To Approve"),
                              ('approve', "Approved"), ('reject', "Rejected")], default='draft')
    is_raw_material = fields.Boolean(string='Is Raw Material', default=False)
    list_approver_ids = fields.One2many('approver.approver', 'product_id',
                                        String='List of Approver')
    is_product_template = fields.Boolean('Is Product Template', compute='compute_state_visibility', compute_sudo=True)

    def compute_state_visibility(self):
        for res in self:
            if self._name == 'product.template':
                res.is_product_template = True
            else:
                res.is_product_template = False

    def change_state_to_approve(self, product, state):
        if product.state != 'to_approve':
            product.state = state
        return product

    def change_state_approve(self, product, state):
        if product.state != 'approve':
            product.state = state
        return product

    def change_state_to_reject(self, product, state):
        if product.state != 'reject':
            product.state = state
        return product

    def change_state_to_draft(self, product, state):
        if product.state != 'draft':
            product.state = state
        return product

    def reject(self):
        for line in self.list_approver_ids:
            line.update({
                'user_id': self.env.user.id,
                'state': 'reject',
                'date': datetime.now()})
        self.change_state_to_reject(self, 'reject')

    def set_to_draft(self):
        self.change_state_to_draft(self, 'draft')
        self.active = False
        self.product_tmpl_id.active = False

    def request_for_approval(self):
        approver_list = []
        approve_notification_id = False
        mail_message = self.env['mail.message']
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        action_id = self.env['ir.model.data'].\
            get_object_reference('purchase', 'product_product_action')[1]
        body_html = _('Please Check at this Product : <a href="%s/web#id=%s&action=%s&'
                      'model=product.product&view_type=form>%s</a>". '
                      'You may Approve the product if it fits the requirements'
                      ' and please Reject the product if it does not.') % \
                    (base_url, self.id, action_id, self.name)

        for groups in self.categ_id.total_group_ids:
            approver_list.append(
                (0, 0, {
                    'user_id': '',
                    'group_id': groups.id,
                    'state': 'waiting',
                    'date': False
                })
            )

        if self.list_approver_ids:
            self.list_approver_ids = False
        self.list_approver_ids = approver_list
        self.change_state_to_approve(self, 'to_approve')

        purchase_quality_ids = []
        for groups in self.list_approver_ids.group_id:
            for user_id in groups.users:
                purchase_quality_ids.append(user_id)

        approve_notification_id = mail_message.create({
            'message_type': 'notification',
            'subject': 'Product Approval',
            'record_name': 'Product Approval',
            'date': datetime.now(),
            'author_id': self.env.user.partner_id.id,
            'model': self._name,
            'res_id': self.id,
            'body': body_html,
        })                

        for this in list(set(purchase_quality_ids)):
            approve_notification_id.update({'partner_ids': [(4, this.partner_id.id)],
                                            'notification_ids': [
                                                (0, 0, {
                                                    'res_partner_id': this.partner_id.id,
                                                    'is_read': False,
                                                    'notification_status': 'sent'})],
                                            })

    def approve(self):
        active_user = self.env.user
        line_to_approve = self.list_approver_ids.filtered(
            lambda l: l.state == 'waiting' and l.group_id in [group for group in active_user.groups_id]
            )
        line_approved = self.list_approver_ids.filtered(
            lambda l: l.state == 'approve' and l.group_id in [group for group in active_user.groups_id]
            )
        if line_to_approve:
            line_to_approve.update({
                'user_id': self.env.user.id,
                'state': 'approve',
                'date': datetime.now()
                })
        elif line_approved:
            raise UserError('Has been approved by other user who are still in the same group.')
        else:
            raise UserError('You dont have the access to Approve this product.')
        if all(line.state == 'approve' for line in self.list_approver_ids):
            self.change_state_approve(self, 'approve')
            self.active = True
            self.product_tmpl_id.active = True

class YudhaProductCategory(models.Model):
    _inherit = "product.category"

    group_ids = fields.Many2many("res.groups", "res_group_categ_rel", "categ_id", "group_id", string="Approver")
    total_group_ids = fields.Many2many("res.groups", string="Total Groups", compute="_compute_total_group_ids")

    def _compute_total_group_ids(self):
        for category in self:
            base_cat = category
            groups = category.group_ids
            while base_cat.parent_id:
                base_cat = base_cat.parent_id
                groups |= base_cat.group_ids
            category.total_group_ids = groups
