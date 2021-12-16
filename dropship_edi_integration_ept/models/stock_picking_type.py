from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    is_dropship_process = fields.Boolean(string="Is Dropshipping?", default=False)
