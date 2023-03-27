# -*- coding : utf-8 -*-
# Author => Albertus Restiyanto Pramayudha
# email  => xabre0010@gmail.com
# linkedin => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA


from odoo import api, fields, models, _


class YudhaProductTemplate(models.Model):
    _inherit = 'product.template'

    # state_product_variant = fields.Selection(related='product_variant_id.state', string='State')
    state_product_variant = fields.Selection([
        ('draft', "Draft"), ('to_approve', "To Approve"),
        ('approve', "Approved"), ('reject', "Rejected")], default='draft',
        compute='compute_state_position', compute_sudo=True)
    state_product = fields.Selection([
        ('draft', "Draft"), ('to_approve', "To Approve"),
        ('approve', "Approved"), ('reject', "Rejected")], default='draft')
    is_product_template = fields.Boolean('Is Product Template', compute='compute_state_visibility', compute_sudo=True)
    list_approver_ids = fields.One2many('approver.approver', 'product_tmpl_id',
                                        String='List of Approver', compute='compute_approver_list')
    check_approver = fields.Boolean(default=False, compute="compute_check_approver", compute_sudo=True)
    user_can_approve = fields.Boolean(default=False, compute="compute_check_approver", compute_sudo=True)
    allow_variant = fields.Boolean(string="Variant Allowed", compute="compute_allow_variant")
    allow_edit = fields.Boolean(default=False, compute="compute_allow_edit")
    marketing_name = fields.Char()
    marketing_description = fields.Text()
    marketing_ingredients = fields.Text(string="Marketing List of Ingredients")
    ecommerce_ids = fields.Many2many("product.ecommerce", "product_ecommerce_rel", "product_id", "ecommerce_id", string="eCommerce")

    @api.model
    def create(self, vals):
        res = super(YudhaProductTemplate, self).create(vals)
        if res.state_product_variant == 'draft':
            res.active = True
            res.product_variant_id.active = True
        return res

    def compute_state_visibility(self):
        for res in self:
            if self._name == 'product.template':
                res.is_product_template = True
            else:
                res.is_product_template = False

    def get_product(self, template_id):
        product_obj = self.env['product.product']
        if template_id.active is True:
            find_product = product_obj.search([('product_tmpl_id', '=', template_id.id),
                                               ('active', '=', True)], limit=1)
        else:
            find_product = product_obj.search([('product_tmpl_id', '=', template_id.id)], limit=1)

        return find_product

    def compute_approver_list(self):
        for res in self:
            product = self.get_product(res)
            res.write({
                'list_approver_ids': [(6, 0, product.list_approver_ids.ids)]
            })

    def compute_state_position(self):
        for res in self:
            product = self.get_product(res)
            res.state_product_variant = product.state
            res.state_product = res.state_product_variant

    def request_for_approval(self):
        for res in self:
            product = self.get_product(res)
            product.request_for_approval()

    def approve(self):
        for res in self:
            product = self.get_product(res)
            product.approve()

    def reject(self):
        for res in self:
            product = self.get_product(res)
            product.reject()

    def set_to_draft(self):
        for res in self:
            product = self.get_product(res)
            product.set_to_draft()

    def compute_check_approver(self):
        for this in self:
            active_user = self.env.user
            get_list_approver = this.list_approver_ids.filtered(lambda l: l.state == 'approve' and l.user_id)
            if active_user in get_list_approver.user_id:
                this.check_approver = True
            else:
                this.check_approver = False
            line_to_approve = self.list_approver_ids.filtered(
                lambda l: l.state == 'waiting' and l.group_id in [group for group in active_user.groups_id]
                )
            if line_to_approve:
                this.user_can_approve = True
            else:
                this.user_can_approve = False

    def compute_allow_variant(self):
        if self.user_has_groups('base.group_system') or self.user_has_groups('base.group_erp_manager'):
            self.allow_variant = True
        else:
            self.allow_variant = False

    def compute_allow_edit(self):
        active_user = self.env.user
        get_list_approver = self.list_approver_ids.filtered(lambda l: l.group_id)
        check_access = self.list_approver_ids.filtered(
            lambda l: l.group_id in [group for group in active_user.groups_id]
            )
        if check_access:
            self.allow_edit = True
        else:
            self.allow_edit = False
