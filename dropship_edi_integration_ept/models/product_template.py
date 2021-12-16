import base64
import logging
import requests
from odoo import models, fields, _

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = "product.template"
    main_product_id = fields.Char(string="Main Product ID", readonly=True,
                                  help='Product will be defined as unique by Main product ID.')

    def create_or_update_products(self, dropship_product_ids=False, partner_ids=False,
                                  is_cron=False):
        """
        It will create/update products from dropship products to odoo.
        :param dropship_product_ids: dropship products
        :param partner_ids: suppliers
        :param is_cron: its true if operation performed automatically
        :return: True
        """
        dropship_product_obj = self.env['dropship.product.ept']
        product_obj = self.env['product.product']
        for partner_id in partner_ids:
            job = self.env['common.log.book.ept'].create({
                'application': 'product',
                'type': 'create',
                'partner_id': partner_id.id,
                'module': 'dropship_edi_integration_ept',
            })
            dropship_product_search_obj = dropship_product_obj.search(
                [('partner_id', '=', partner_id.id), ('id', 'in', dropship_product_ids.ids)])
            product_updated = product_created = 0
            for dropship_product in dropship_product_search_obj:
                dropship_route = self.env.ref('stock_dropshipping.route_drop_shipping')
                product_template = self.search([('main_product_id', '=',
                                                 dropship_product.main_product_id)], limit=1)
                if dropship_product.barcode:
                    barcode_product_id = product_obj.search([
                        ('barcode', '=', dropship_product.barcode)], limit=1)
                    if barcode_product_id:
                        log_message = (_("Barcode %s has been skipped due to duplication."
                                         " Product - %s") % (dropship_product.barcode or '',
                                                             dropship_product.name))
                        self._create_common_log_line(job, log_message)
                        dropship_product.barcode = False
                image_url = dropship_product.image_url
                category = dropship_product.category
                if image_url:
                    try:
                        image_data = requests.get(image_url)
                        if image_data.status_code == 200:
                            image_url = base64.b64encode(image_data.content)
                        else:
                            image_url = False
                    except:
                        image_url = False
                categ_id = False
                if category:
                    categ_id = self.env['product.category'].search([
                        ('name', '=', category)], limit=1)
                    if not categ_id:
                        if is_cron and partner_id.auto_create_category:
                            categ_id = self.env['product.category'].create(
                                {'name': category})
                        elif is_cron and not partner_id.auto_create_category:
                            log_message = (_("Dropship product %s has been skipped"
                                             " due to category %s not found in Odoo.") %
                                           (dropship_product.name, category))
                            self._create_common_log_line(job, log_message)
                            continue
                        else:
                            categ_id = self.env['product.category'].create(
                                {'name': category})
                prepare_product_vals = {
                    'name': dropship_product.name,
                    'main_product_id': dropship_product.main_product_id,
                    'weight': dropship_product.weight or 0.0,
                    'type': 'product',
                    'description_sale': dropship_product.description or False,
                    'barcode': dropship_product.barcode or False,
                    'image_1920': image_url or False,
                    'route_ids': [(6, 0, dropship_route.ids)],
                }
                if categ_id:
                    prepare_product_vals.update({'categ_id': categ_id.id})
                if not product_template:
                    product_id = False
                    if dropship_product.default_code:
                        prepare_product_vals.update({'default_code': dropship_product.default_code
                                                                     or False})
                        product_id = product_obj.create(prepare_product_vals)
                        self.env['product.supplierinfo'].create(
                            {'product_id': product_id.id,
                             'name': dropship_product.partner_id.id,
                             'product_tmpl_id': product_id.product_tmpl_id.id,
                             'price': dropship_product.price or 0.0})
                        self.env['vendor.stock.ept'].create(
                            {'vendor_product_id': product_id.id,
                             'vendor': dropship_product.partner_id.id,
                             'vendor_stock': dropship_product.quantity or 0.0})
                        log_message = (_("Product has been created with internal reference in Odoo."))
                        self._create_common_log_line(job, log_message,
                                                     dropship_product.default_code, product_id.id)
                        product_created = product_created + 1

                    elif dropship_product.vendor_code:
                        product_id = product_obj.create(prepare_product_vals)
                        log_message = (_("Product has been created with vendor product code"
                                         " in Odoo."))
                        self._create_common_log_line(job, log_message,
                                                     dropship_product.vendor_code, product_id.id)
                        product_created = product_created + 1
                        vendor_code_id = self.env['product.supplierinfo'].search([
                            ('product_code', '=', dropship_product.vendor_code),
                            ('name', '=', dropship_product.partner_id.id)], limit=1)
                        if vendor_code_id:
                            vendor_code_id.write(
                                {'product_id': product_id.id,
                                 'product_tmpl_id': product_id.product_tmpl_id.id,
                                 'price': dropship_product.price or 0.0})
                            vendor_stock_id = self.env['vendor.stock.ept'].search([
                                ('vendor_product_id', '=', vendor_code_id.product_id.id),
                                ('vendor', '=', dropship_product.partner_id.id)], limit=1)
                            if vendor_stock_id:
                                vendor_stock_id.write({'vendor_stock': dropship_product.quantity or 0.0})
                        else:
                            self.env['product.supplierinfo'].create(
                                {'product_id': product_id.id,
                                 'name': dropship_product.partner_id.id,
                                 'product_code': dropship_product.vendor_code,
                                 'product_tmpl_id': product_id.product_tmpl_id.id,
                                 'price': dropship_product.price or 0.0})
                            self.env['vendor.stock.ept'].create(
                                {'vendor_product_id': product_id.id,
                                 'vendor': dropship_product.partner_id.id,
                                 'vendor_stock': dropship_product.quantity or 0.0})
                    product_tmpl_id = product_id.product_tmpl_id
                    dropship_product.write({'is_processed': True,
                                            'product_id': product_id and product_id.id})
                    self._assign_attribute_to_product(dropship_product, product_tmpl_id)
                else:
                    self._assign_attribute_to_product(dropship_product, product_template)
                    product_id = self._find_same_attribute_value_product(product_template,
                                                                         dropship_product)
                    if dropship_product.default_code:
                        # product_id = product_obj.search([
                        #     ('default_code', '=', dropship_product.default_code)], limit=1)
                        if not product_id:
                            prepare_product_vals.update(
                                {'product_tmpl_id': product_template and product_template.id,
                                 'default_code': dropship_product.default_code or False})
                            product_id = product_obj.create(prepare_product_vals)
                            log_message = (_("Product has been created with internal reference"
                                             " in Odoo."))
                            self._create_common_log_line(job, log_message,
                                                         dropship_product.default_code,
                                                         product_id.id)
                            product_created = product_created + 1
                        else:
                            product_id.write({
                                'name': dropship_product.name,
                                'weight': dropship_product.weight or 0.0,
                                'description_sale': dropship_product.description or False,
                                'barcode': dropship_product.barcode or False,
                                'type': 'product',
                                'default_code': dropship_product.default_code or False,
                                'image_1920': image_url or False,
                            })
                            if categ_id:
                                product_id.write({'categ_id': categ_id.id})
                            log_message = (_("Product has been updated with internal reference"
                                             " in Odoo."))
                            self._create_common_log_line(job, log_message,
                                                         dropship_product.default_code,
                                                         product_id.id)
                            product_updated = product_updated + 1
                        vendor_code_id = self.env['product.supplierinfo'].search(
                            [('name', '=', dropship_product.partner_id.id),
                             ('product_id', '=', product_id.id)], limit=1)
                        if vendor_code_id:
                            vendor_code_id.write(
                                {'product_id': product_id.id,
                                 'product_tmpl_id': product_id.product_tmpl_id.id,
                                 'price': dropship_product.price or 0.0})
                        else:
                            self.env['product.supplierinfo'].create(
                                {'product_id': product_id.id,
                                 'product_tmpl_id': product_id.product_tmpl_id.id,
                                 'name': dropship_product.partner_id.id,
                                 'price': dropship_product.price or 0.0})
                        vendor_stock_id = self.env['vendor.stock.ept'].search([
                            ('vendor_product_id', '=', product_id.id),
                            ('vendor', '=', dropship_product.partner_id.id)], limit=1)
                        if vendor_stock_id:
                            vendor_stock_id.write({'vendor_stock': dropship_product.quantity or 0.0})
                        else:
                            self.env['vendor.stock.ept'].create(
                                {'vendor_product_id': product_id.id,
                                 'vendor': dropship_product.partner_id.id,
                                 'vendor_stock': dropship_product.quantity or 0.0})

                    elif dropship_product.vendor_code:
                        if not product_id:
                            prepare_product_vals.update(
                                {'product_tmpl_id': product_template and product_template.id})
                            product_id = product_obj.create(prepare_product_vals)
                            log_message = (_("Product has been created with vendor product code"
                                             " in Odoo."))
                            self._create_common_log_line(job, log_message,
                                                         dropship_product.vendor_code,
                                                         product_id.id)
                            product_created = product_created + 1
                        else:
                            product_id.write({
                                'product_tmpl_id': product_id.product_tmpl_id.id,
                                'name': dropship_product.name,
                                'weight': dropship_product.weight or 0.0,
                                'description_sale': dropship_product.description or False,
                                'barcode': dropship_product.barcode or False,
                                'type': 'product',
                                'image_1920': image_url or False,
                            })
                            if categ_id:
                                product_id.write({'categ_id': categ_id.id})
                            log_message = (_("Product has been updated with vendor product code"
                                             " in Odoo."))
                            self._create_common_log_line(job, log_message,
                                                         dropship_product.vendor_code,
                                                         product_id.id)
                            product_updated = product_updated + 1
                        vendor_code_id = self.env['product.supplierinfo'].search(
                            [('product_code', '=', dropship_product.vendor_code),
                             ('name', '=', dropship_product.partner_id.id)], limit=1)
                        if not vendor_code_id:
                            self.env['product.supplierinfo'].create(
                                {'product_id': product_id.id,
                                 'name': dropship_product.partner_id.id,
                                 'product_code': dropship_product.vendor_code,
                                 'product_tmpl_id': product_id.product_tmpl_id.id,
                                 'price': dropship_product.price or 0.0})
                        else:
                            vendor_code_id.write(
                                {'product_id': product_id.id,
                                 'product_tmpl_id': product_id.product_tmpl_id.id,
                                 'price': dropship_product.price or 0.0})
                        vendor_stock_id = self.env['vendor.stock.ept'].search([
                            ('vendor_product_id', '=', product_id.id),
                            ('vendor', '=', dropship_product.partner_id.id)], limit=1)
                        if vendor_stock_id:
                            vendor_stock_id.write({'vendor_stock': dropship_product.quantity or 0.0})
                        else:
                            self.env['vendor.stock.ept'].create(
                                {'vendor_product_id': product_id.id,
                                 'vendor': dropship_product.partner_id.id,
                                 'vendor_stock': dropship_product.quantity or 0.0})
                    dropship_product.write({'is_processed': True,
                                            'product_id': product_id and product_id.id})
                _logger.info("Dropship Product [%s]%s created/updated in odoo. | Total - %s ",
                             dropship_product.main_product_id, dropship_product.name,
                             (product_updated + product_created))

            if product_updated or product_created:
                job.write({'message': "Dropship products created/updated in Odoo successfully."})
                log_message = (_("Total %s products have been created/updated in Odoo. |"
                                 " Total Created - %s | Total Updated - %s") %
                               ((product_updated + product_created), product_created,
                                product_updated))
                self._create_common_log_line(job, log_message)

        return True

    def _create_common_log_line(self, job, log_message, product_code='', product_id=''):
        """
        It will create the common log line for the dropship operations.
        :param job: job id
        :param log_message: message for the process
        :param product_code: product code
        :param product_id: product id
        :return: True
        """
        self.env['common.log.lines.ept'].create(
            {'log_line_id': job.id, 'message': log_message,
             'default_code': product_code, 'product_id': product_id})
        return True

    def _find_same_attribute_value_product(self, product_template, dropship_product):
        """
        It will find the product variant with same attribute and attribute values.
        :param product_template: product template object
        :param dropship_product: dropship product
        :return: product_id
        """
        vendor_product_obj = self.env['product.product'].search(
            [('product_tmpl_id', '=', product_template.id)])
        product_id = False
        for vendor_pro in vendor_product_obj:
            product_attribute_ids = vendor_pro.product_template_attribute_value_ids
            attr_matched = True
            if dropship_product.attribute_name and dropship_product.attribute_value:
                for product_attr in product_attribute_ids:
                    attribute_name = product_attr.attribute_id.name
                    attribute_value = product_attr.product_attribute_value_id.name
                    dropship_pro_attr_name = dropship_product.attribute_name.split(',')
                    dropship_pro_attr_value = dropship_product.attribute_value.split(',')
                    if (attribute_name, attribute_value) not in \
                           zip(dropship_pro_attr_name, dropship_pro_attr_value):
                        attr_matched = False
                        continue
            if attr_matched:
                product_id = vendor_pro
                break
        return product_id

    def _assign_attribute_to_product(self, dropship_product=False, product_tmpl_id=False):
        """
        It will assign the attribute and attribute values to product.
        :param dropship_product: drosphip product object
        :param product_tmpl_id: product template object
        :return: True
        """
        product_attribute_obj = self.env['product.attribute']
        product_attribute_value_obj = self.env['product.attribute.value']
        product_attribute_line_obj = self.env['product.template.attribute.line']
        product_template_attribute_value_obj = self.env['product.template.attribute.value']
        if dropship_product.attribute_name and dropship_product.attribute_value:
            for attr_name, attr_value in zip(dropship_product.attribute_name.split(','),
                                             dropship_product.attribute_value.split(',')):
                attribute_id = product_attribute_obj.search([
                    ('name', '=', attr_name)], limit=1)
                if not attribute_id:
                    attribute_id = product_attribute_obj.create({'name': attr_name})
                attrib_value_id = product_attribute_value_obj.search([
                    ('attribute_id', '=', attribute_id.id),
                    ('name', '=', attr_value)], limit=1)
                if not attrib_value_id:
                    attrib_value_id = product_attribute_value_obj.create(
                        {'attribute_id': attribute_id.id, 'name': attr_value})
                product_attribute_line_id = product_attribute_line_obj.search([
                    ('product_tmpl_id', '=', product_tmpl_id.id),
                    ('attribute_id', '=', attribute_id.id)])
                if not product_attribute_line_id:
                    product_attribute_line_id = product_attribute_line_obj.create(
                        {'product_tmpl_id': product_tmpl_id.id,
                         'attribute_id': attribute_id.id,
                         'value_ids': [(6, 0, attrib_value_id.ids)]})
                else:
                    product_attribute_id = product_attribute_line_obj.search([
                        ('product_tmpl_id', '=', product_tmpl_id.id),
                        ('attribute_id', '=', attribute_id.id),
                        ('value_ids', 'in', attrib_value_id.ids)], limit=1)
                    if not product_attribute_id:
                        value_ids = product_attribute_line_id.value_ids.ids or []
                        value_ids += attrib_value_id.ids
                        product_attribute_line_id.write(
                            {'value_ids': [(6, 0, list(set(value_ids)))]})
                product_tmpl_attribute_value_id = product_template_attribute_value_obj.search([
                    ('product_tmpl_id', '=', product_tmpl_id.id),
                    ('attribute_id', '=', attribute_id.id),
                    ('attribute_line_id', '=', product_attribute_line_id.id),
                    ('product_attribute_value_id', '=', attrib_value_id.id)
                ])
                if not product_tmpl_attribute_value_id:
                    product_template_attribute_value_obj.create(
                        {'product_tmpl_id': product_tmpl_id.id,
                         'attribute_id': attribute_id.id,
                         'attribute_line_id': product_attribute_line_id.id,
                         'product_attribute_value_id': attrib_value_id.id})
        return True

    def auto_create_or_update_products(self, ctx={}):
        """
        It will create or update products from dropship products to odoo as per the
        supplier's schedule.
        :param ctx: context to fetch that operation is performed by which supplier.
        :return: True
        """
        partner_obj = self.env['res.partner']
        dropship_product_ept_obj = self.env['dropship.product.ept']
        if not isinstance(ctx, dict) or 'partner_id' not in ctx:
            return True
        partner_id = ctx.get('partner_id', False)
        partner_ids = partner_obj.browse(partner_id)

        product_ids = dropship_product_ept_obj.search([('partner_id', 'in', partner_ids.ids)])

        if product_ids and partner_ids:
            self.create_or_update_products(product_ids, partner_ids, is_cron=True)
        return True
