from odoo import models, fields, api


class CommonLogLinesEpt(models.Model):
    _inherit = "common.log.lines.ept"
    _order = 'id desc'

    tracking_no = fields.Char(string="Tracking No")