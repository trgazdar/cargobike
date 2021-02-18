from odoo import models, fields, _


class DropshipOperationWizard(models.TransientModel):
    _name = "dropship.operation.wizard"
    _description = 'Dropship Operations'

    partner_ids = fields.Many2many('res.partner', string="Suppliers",
                                   help='Select the supplier whose FTP server will be'
                                        ' used to perform the dropship operation.')
    picking_ids = fields.Many2many('stock.picking', string="Purchase Orders")
    operations = fields.Selection([('import', 'Import Operations'), ('export', 'Export Operations')],
                                  string='Operations')
    import_operations = fields.Selection([('import_products', 'Import Products'),
                                          ('import_stock', 'Import Stock'),
                                          ('import_shipment_orders', 'Import Shipment Orders')],
                                         string='Import Operations',
                                         help="Import Product: Perform the product import operation from CSV file to dropship product."
                                              "Import Stock: Perform the stock import operation from CSV file to odoo actual product."
                                              "Import Shipment Orders: Import the shipment orders with tracking information to odoo.")
    export_operations = fields.Selection([('export_shipment_orders', 'Export Shipment Orders')],
                                         string='Export Operations',
                                         help="Export Orders: This option will export the purchase orders to FTP server.")

    def perform_edi_operations(self):
        product_obj = self.env['product.product']
        stock_picking_obj = self.env['stock.picking']

        if self.import_operations == 'import_products':
            product_obj.import_products_from_ftp(self.partner_ids)
        elif self.import_operations == 'import_stock':
            product_obj.import_stock_from_ftp(self.partner_ids)
        elif self.export_operations == 'export_shipment_orders':
            stock_picking_obj.export_shipment_orders_to_ftp(self.picking_ids, self.partner_ids)
        elif self.import_operations == 'import_shipment_orders':
            stock_picking_obj.import_shipment_orders_from_ftp(self.partner_ids)
        return {
            'name': _('Common Log Book'),
            'type': 'ir.actions.act_window',
            'res_model': 'common.log.book.ept',
            'view_mode': 'tree,form',
            'target': 'current',
        }

    def create_update_products_to_catalog(self):
        """
        Create / Update products to odoo catalog.
        :return: True
        """
        product_template = self.env['product.template']
        active_ids = self._context.get('active_ids')
        dropship_product_obj = self.env['dropship.product.ept']
        dropship_product_ids = dropship_product_obj.search([('id', 'in', active_ids)])
        partner_ids = dropship_product_ids.mapped('partner_id')
        if dropship_product_ids and partner_ids:
            product_template.create_or_update_products(dropship_product_ids, partner_ids,
                                                       is_cron=False)
        return True
