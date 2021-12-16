from odoo import models, fields, api


class CommonLogBookEpt(models.Model):
    _name = "common.log.book.ept"
    _inherit = ["common.log.book.ept", "mail.thread"]
    _order = 'id desc'

    filename = fields.Char("File Name", help='Name of the processed file.')
    type = fields.Selection(selection_add=[('create', 'Create')])
    module = fields.Selection(
        selection_add=[('dropship_edi_integration_ept', 'Dropshipping EDI Integration Connector')])
    application = fields.Selection([('sales', 'Sales'), ('shipment', 'Delivery'),
                                    ('inventory', 'Stock'), ('product', 'Product'),
                                    ('other', 'Other')], string="Application")
    company_id = fields.Many2one('res.company', string="Company")
    partner_id = fields.Many2one('res.partner', string="Supplier",
                                 help='Name of the supplier by whom this operation has'
                                      ' been performed.')
