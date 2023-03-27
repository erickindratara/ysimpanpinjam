# -*- coding : utf-8 -*-
# Author    => Albertus Restiyanto Pramayudha
# email     => xabre0010@gmail.com
# linkedin  => https://www.linkedin.com/in/albertus-restiyanto-pramayudha-470261a8/
# youtube   => https://www.youtube.com/channel/UCCtgLDIfqehJ1R8cohMeTXA

from odoo import models, fields, api, _
import base64

class YudhaLoginImage(models.Model):
    _name = 'yudha.login.image'
    _rec_name = 'name'

    image = fields.Binary("Image", attachment=False)
    name = fields.Char(string="Name")
    image_file  = fields.Char(string='Path Image Tugas',copy = False)

    @api.model
    def create(self,vals):
        res = super(YudhaLoginImage, self).create(vals)
        for alldata in res:
            attached_file = alldata.image
            attachment_id1 = self.env['ir.attachment'].sudo().create({
                'name': alldata.image_file,
                'res_model': 'yudha.login.image',
                'res_id': alldata.id,
                'type': 'binary',
                'datas': base64.b64encode(attached_file),
            })
            attachment = self.env['ir.attachment'].browse(attachment_id1.id)
            if attachment:
                self.env.company.Yudha_background = attachment.datas
        return res

    def write(self,vals):
        res = super(YudhaLoginImage,self).write(vals)
        for alldata in self:
            attached_file = alldata.image
            attachment_id1 = self.env['ir.attachment'].sudo().create({
                'name': alldata.image_file,
                'res_model': 'yudha.login.image',
                'res_id': alldata.id,
                'type': 'binary',
                'datas': attached_file,
            })
            attachment = self.env['ir.attachment'].browse(attachment_id1.id)
            if attachment:
                self.env.company.Yudha_background = attachment.datas
        return res