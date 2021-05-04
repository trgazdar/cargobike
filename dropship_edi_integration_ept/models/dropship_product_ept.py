from odoo import models, fields
import requests
import base64


class DropshipProductEpt(models.Model):
    _name = "dropship.product.ept"
    _description = "Dropship Product"
    _inherit = ['mail.thread', 'image.mixin']
    _order = 'id desc'

    name = fields.Char(string='Product Name', help='Name of the dropship product.')
    main_product_id = fields.Char(string="Main Product ID",
                                  help='Product will be defined as unique by Main product ID.')
    partner_id = fields.Many2one('res.partner', 'Customer',
                                 help='Name of the supplier who supplies this product.')
    is_processed = fields.Boolean(string="Is Processed?", default=False,
                                  help='Checked if this product is created in odoo.')
    filename = fields.Char("File Name", help='Name of the file by which this product is imported.')
    default_code = fields.Char(string="Internal Reference",
                               help='By this code product will be identified in odoo.')
    vendor_code = fields.Char(string="Vendor Code",
                              help='By this code vendor has imported this product. '
                                   'This code may be same for different supplier.')
    description = fields.Text(string="Description",
                              help='A product description is the important information'
                                   ' about the features and benefits of the product ')
    attribute_name = fields.Char(string="Attributes Name",
                                 help='Name of the attributes for the product.')
    attribute_value = fields.Char(string="Attributes Value",
                                  help='Values of the attributes for the product.')
    price = fields.Float(string="Price",
                         help='Product cost price, the product will be supply with this price.')
    quantity = fields.Float(string="Quantity", help='Product Quantity')
    category = fields.Char(string="Category", help='Product category')
    product_id = fields.Many2one('product.product', 'Product',
                                 help='Product will be identified by this name in odoo.')
    barcode = fields.Char(string="Barcode", help='Product barcode')
    image_url = fields.Text(string="Image URL", help='Product image')
    weight = fields.Float(string="Weight", help='Weight of the product.')

    def write(self, values):
        """
        It will process the image_url in b64encode format and store in image_1920 field to display
         product image in dropship product form view.
        :param values:
        :return:
        """
        if values.get('image_url') and values.get('image_url') != self.image_url:
            try:
                image_data = requests.get(values.get('image_url'))
                if image_data.status_code == 200:
                    image_1920 = base64.b64encode(image_data.content)
                    values.update({'image_1920': image_1920})
                else:
                    values.update({'image_1920': False})
            except:
                values.update({'image_1920': False})
        res = super(DropshipProductEpt, self).write(values)
        return res