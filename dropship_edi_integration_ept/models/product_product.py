from csv import DictWriter
from io import StringIO
import requests
import base64
import csv
import logging
from odoo import fields, models, _
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # def _select_seller(self, partner_id=False, quantity=0.0, date=None, uom_id=False, params=False):
    #     """
    #     This method is overwrite to check the condition that if vendor having quantity greater
    #      than zero than and than only the purchase order will get created for that vendor.
    #     """
    #     self.ensure_one()
    #     if date is None:
    #         date = fields.Date.context_today(self)
    #     precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #
    #     res = self.env['product.supplierinfo']
    #     sellers = self._prepare_sellers(params)
    #     if self.env.context.get('force_company'):
    #         sellers = sellers.filtered(lambda s: not s.company_id or s.company_id.id == self.env.context['force_company'])
    #     for seller in sellers:
    #         # Set quantity in UoM of seller
    #         quantity_uom_seller = quantity
    #         if quantity_uom_seller and ftp.server.eptuom_id and uom_id != seller.product_uom:
    #             quantity_uom_seller = uom_id._compute_quantity(quantity_uom_seller, seller.product_uom)
    #
    #         if seller.date_start and seller.date_start > date:
    #             continue
    #         if seller.date_end and seller.date_end < date:
    #             continue
    #         if partner_id and seller.name not in [partner_id, partner_id.parent_id]:
    #             continue
    #         if float_compare(quantity_uom_seller, seller.min_qty, precision_digits=precision) == -1:
    #             continue
    #         if seller.product_id and seller.product_id != self:
    #             continue
    #         # This will find the vendor for the product from vendor.stock.ept and check that quantity
    #         # must be greater than zero
    #         vendor = self.env['vendor.stock.ept'].search([('vendor_product_id', '=', self.id),
    #                                                     ('vendor', '=', seller.name.id)], limit=1)
    #         if vendor.vendor_stock <= 0:
    #             continue
    #         if not res or res.name == seller.name:
    #             res |= seller
    #     return res.sorted('price')[:1]

    def _create_droship_product(self, file_reader=[], partner_id=False, server_filename=False,
                                filename=False):
        """
        It will create the dropship product as per the file data.
        :param file_reader: file data
        :param partner_id: supplier
        :param server_filename: name of the file which used to perform import products.
        :param filename: temporary file name.
        :return: True
        """
        row_num = 1
        updated_product = created_product = skip_product = 0
        job = self.env['common.log.book.ept'].create({
            'application': 'product',
            'type': 'import',
            'partner_id': partner_id.id,
            'filename': server_filename,
            'module': 'dropship_edi_integration_ept',
            'message': "FTP connection has been established successfully.",
        })
        # Start CSV Writer
        buffer = StringIO()
        field_name = ['Product_code', 'Log_details']
        csvwriter = DictWriter(buffer, field_name, delimiter=partner_id.csv_delimiter or ';')
        csvwriter.writer.writerow(field_name)
        for line in file_reader:
            missing_values = []
            dropship_product_ept_obj = self.env['dropship.product.ept']
            main_product_id = line.get('Main_product_id', False)
            product_code = line.get('Product_code', False)
            name = line.get('Name', False)
            description = line.get('Description', False)
            attributes = line.get('Attributes', False)
            attribute_values = line.get('Attribute_values', False)
            weight = line.get('Weight', 0.0)
            price = quantity = False
            if line.get('Price'):
                try:
                    price = float(line.get('Price'))
                except ValueError:
                    price = line.get('Price')
            if line.get('Quantity'):
                try:
                    quantity = float(line.get('Quantity'))
                except ValueError:
                    quantity = line.get('Quantity')
            barcode = line.get('Barcode', False)
            image_url = line.get('Image_url', False)
            image_1920 = False
            if image_url:
                try:
                    image_data = requests.get(image_url)
                    if image_data.status_code == 200:
                        image_1920 = base64.b64encode(image_data.content)
                except:
                    image_1920 = False
            category = line.get('Category', False)
            row_num = row_num + 1
            dropship_product_line_vals = {
                'name': name,
                'description': description,
                'attribute_name': attributes,
                'attribute_value': attribute_values,
                'price': price,
                'quantity': quantity,
                'category': category,
                'barcode': barcode,
                'image_url': image_url,
                'image_1920': image_1920,
                'weight': weight,
                'filename': server_filename,
            }
            if not main_product_id:
                missing_values.append('Main_product_id')
            if not product_code:
                missing_values.append('Product_code')
            if not name:
                missing_values.append('Name')
            if missing_values:
                log_message = (_("Missing field(s) values for %s at row Number %s.") % (
                    str(missing_values)[1:-1], row_num))
                self._create_common_log_line(job, csvwriter, log_message)
                continue
            dropship_main_product_obj = dropship_product_ept_obj.search(
                [('main_product_id', '=', main_product_id),
                 ('partner_id', '=', partner_id.id)])
            if partner_id.search_by_vendor_code:
                if not dropship_main_product_obj:
                    try:
                        dropship_product_line_vals.update(
                            {'main_product_id': main_product_id,
                             'partner_id': partner_id.id,
                             'vendor_code': product_code,
                             })
                        dropship_product_ept_obj.create(dropship_product_line_vals)
                        created_product = created_product + 1
                        log_message = (_("Product %s has been created.") % name)
                        self._create_common_log_line(job, csvwriter, log_message, product_code)
                    except:
                        log_message = (_("Product is skipped, due to incorrect field(s)"
                                         " value at row Number %s.") % row_num)
                        self._create_common_log_line(job, csvwriter, log_message, product_code)
                        skip_product = skip_product + 1
                        continue
                else:
                    existing_dropship_product = dropship_main_product_obj.filtered(
                        lambda pro: pro.vendor_code == product_code)
                    if existing_dropship_product:
                        new_dropship_pro_vals = \
                            self._verify_product_data(existing_dropship_product,
                                                      dropship_product_line_vals)
                        if new_dropship_pro_vals:
                            try:
                                existing_dropship_product.write(new_dropship_pro_vals)
                                updated_product = updated_product + 1
                                log_message = (_("Product %s has been updated.") % name)
                                self._create_common_log_line(job, csvwriter, log_message, product_code)
                            except:
                                log_message = (_("Product is skipped, due to incorrect"
                                                 " field(s) value at row number %s.") % row_num)
                                self._create_common_log_line(job, csvwriter, log_message, product_code)
                                skip_product = skip_product + 1
                                continue
                        else:
                            log_message = (_("Product has been skipped. There is no change in"
                                             " product data."))
                            self._create_common_log_line(job, csvwriter, log_message, product_code)
                            skip_product = skip_product + 1
                    else:
                        if attributes and attribute_values:
                            if dropship_main_product_obj.filtered(lambda prod:
                                                                  prod.attribute_name == attributes
                                                                  and prod.attribute_value ==
                                                                  attribute_values):
                                log_message = (_("Product is skipped due to attribute"
                                                 " [%s] and their values [%s] already defined.")) % \
                                              (attributes, attribute_values)
                                self._create_common_log_line(job, csvwriter, log_message, product_code)
                                skip_product = skip_product + 1
                                continue
                        try:
                            dropship_product_line_vals.update(
                                {'main_product_id': main_product_id,
                                 'partner_id': partner_id.id,
                                 'vendor_code': product_code,
                                 })
                            dropship_product_ept_obj.create(dropship_product_line_vals)
                            created_product = created_product + 1
                            log_message = (_("Product %s has been created.") % name)
                            self._create_common_log_line(job, csvwriter, log_message, product_code)
                        except:
                            log_message = (_("Product is skipped, due to incorrect field(s)"
                                             " value at row number %s.") % row_num)
                            self._create_common_log_line(job, csvwriter, log_message, product_code)
                            skip_product = skip_product + 1
                            continue
            else:
                if not dropship_main_product_obj:
                    try:
                        dropship_product_line_vals.update(
                            {'main_product_id': main_product_id,
                             'partner_id': partner_id.id,
                             'default_code': product_code,
                             })
                        dropship_product_ept_obj.create(dropship_product_line_vals)
                        created_product = created_product + 1
                        log_message = (_("Product %s has been created.") % name)
                        self._create_common_log_line(job, csvwriter, log_message, product_code)
                    except:
                        log_message = (_("Product is skipped, due to incorrect field(s)"
                                         " value at row number %s.") % row_num)
                        self._create_common_log_line(job, csvwriter, log_message, product_code)
                        skip_product = skip_product + 1
                        continue

                else:
                    existing_dropship_product = dropship_main_product_obj.filtered(
                        lambda pro: pro.default_code == product_code)
                    if existing_dropship_product:
                        new_dropship_pro_vals = \
                            self._verify_product_data(existing_dropship_product,
                                                      dropship_product_line_vals)
                        if new_dropship_pro_vals:
                            try:
                                existing_dropship_product.write(new_dropship_pro_vals)
                                updated_product = updated_product + 1
                                log_message = (_("Product %s has been updated.") % name)
                                self._create_common_log_line(job, csvwriter, log_message,
                                                             product_code)
                            except:
                                log_message = (_("Product is skipped, due to incorrect"
                                                 " field(s) value at row number %s.") % row_num)
                                self._create_common_log_line(job, csvwriter, log_message,
                                                             product_code)
                                skip_product = skip_product + 1
                                continue
                        else:
                            log_message = (_("Product has been skipped. There is no change"
                                             " in product data."))
                            self._create_common_log_line(job, csvwriter, log_message, product_code)
                            skip_product = skip_product + 1
                    else:
                        if attributes and attribute_values:
                            if dropship_main_product_obj.filtered(lambda prod:
                                                                  prod.attribute_name == attributes
                                                                  and prod.attribute_value ==
                                                                  attribute_values):
                                log_message = (_("Product is skipped due to attribute"
                                                 " [%s] and their values [%s] already defined.")) % \
                                              (attributes, attribute_values)
                                self._create_common_log_line(job, csvwriter, log_message,
                                                             product_code)
                                skip_product = skip_product + 1
                                continue
                        try:
                            dropship_product_line_vals.update(
                                {'main_product_id': main_product_id,
                                 'partner_id': partner_id.id,
                                 'default_code': product_code,
                                 })
                            dropship_product_ept_obj.create(dropship_product_line_vals)
                            created_product = created_product + 1
                            log_message = (_("Product %s has been created.") % name)
                            self._create_common_log_line(job, csvwriter, log_message, product_code)
                        except:
                            log_message = (_("Product is skipped, due to incorrect field(s)"
                                             " value at row number %s.") % row_num)
                            self._create_common_log_line(job, csvwriter, log_message, product_code)
                            skip_product = skip_product + 1
                            continue
            _logger.info('[%s] : %s imported from csv | Total - %s ',
                         product_code, name, (row_num - 1))
        log_message = (_("Total Dropship Products - %s | Total Created - %s |"
                         " Total Updated - %s | Total Skipped - %s ") %
                       ((row_num - 1), created_product, updated_product, skip_product))
        self._create_common_log_line(job, csvwriter, log_message)
        _logger.info('Total Dropship Products - %s | Created - %s |'
                     ' Updated - %s | Skipped - %s', (row_num - 1),
                     created_product, updated_product, skip_product)
        file = open(filename)
        file.seek(0)
        file_data = file.read().encode()
        if file_data:
            vals = {
                'name': server_filename,
                'datas': base64.encodestring(file_data),
                'type': 'binary',
                'res_model': 'common.log.book.ept',
            }
            attachment = self.env['ir.attachment'].create(vals)
            job.message_post(body=_("<b>Supplier's Imported Product File</b>"),
                             attachment_ids=attachment.ids)

        # Move file to archive directory
        try:
            with partner_id.get_dropship_edi_interface(operation="product_import") \
                    as dropship_tpw_interface:
                dropship_tpw_interface.archive_file([server_filename])
        except Exception:
            log_message = (_("Supplier %s has Problem with connection or file Path."
                             " File can not Move to Archive.") % partner_id.name)
            self._create_common_log_line(job, csvwriter, log_message)
        # Attach the log file with job
        log_filename = "%s_%s" % (server_filename[:-4], 'log_details.csv')
        buffer.seek(0)
        log_file_data = buffer.read().encode()
        if log_file_data:
            vals = {
                'name': log_filename,
                'datas': base64.encodestring(log_file_data),
                'type': 'binary',
                'res_model': 'common.log.book.ept',
            }
            attachment = self.env['ir.attachment'].create(vals)
            job.message_post(body=_("<b>Imported Products Log File</b>"),
                             attachment_ids=attachment.ids)
        buffer.close()
        return True

    def _create_common_log_line(self, job, csvwriter, log_message, product_code=''):
        """
        It will create the common log line for the dropship operations.
        :param job: job id
        :param csvwriter: csv writer obj
        :param log_message: message for the process
        :param product_code: default_code or vendor_code of the product
        :return: True
        """
        self.env['common.log.lines.ept'].create({'log_line_id': job.id, 'message': log_message,
                                                 'default_code': product_code})
        csvwriter.writerow({'Product_code': product_code, 'Log_details': log_message})
        return True

    def _verify_product_data(self, existing_dropship_product, dropship_product):
        """
        It will compare the csv file product data with existing dropship product data,
         if there is change in the csv file product data then it will update vals.
        :param existing_dropship_product: existing dropship product
        :param dropship_product: new dropship product dictionary
        :return: new_dropship_line_vals
        """
        new_dropship_line_vals = {}
        name = dropship_product.get('name')
        description = dropship_product.get('description')
        attribute_name = dropship_product.get('attribute_name')
        attribute_value = dropship_product.get('attribute_value')
        price = dropship_product.get('price')
        quantity = dropship_product.get('Quantity')
        category = dropship_product.get('category')
        barcode = dropship_product.get('barcode')
        image_url = dropship_product.get('image_url')
        weight = dropship_product.get('weight')
        server_filename = dropship_product.get('filename')
        image_1920 = dropship_product.get('image_1920')
        if name and existing_dropship_product.name != name:
            new_dropship_line_vals.update({'name': name})
        if description and existing_dropship_product.description != description:
            new_dropship_line_vals.update({'description': description})
        if attribute_name and existing_dropship_product.attribute_name != attribute_name:
            new_dropship_line_vals.update({'attribute_name': attribute_name})
        if attribute_value and existing_dropship_product.attribute_value != attribute_value:
            new_dropship_line_vals.update({'attribute_value': attribute_value})
        if price and existing_dropship_product.price != price:
            new_dropship_line_vals.update({'price': price})
        if quantity and existing_dropship_product.quantity != quantity:
            new_dropship_line_vals.update({'quantity': quantity})
        if category and existing_dropship_product.category != category:
            new_dropship_line_vals.update({'category': category})
        if barcode and existing_dropship_product.barcode != barcode:
            new_dropship_line_vals.update({'barcode': barcode})
        if image_url and existing_dropship_product.image_url != image_url:
            new_dropship_line_vals.update({'image_url': image_url, 'image_1920': image_1920})
        if weight and existing_dropship_product.weight != weight:
            new_dropship_line_vals.update({'weight': weight})
        if server_filename and existing_dropship_product.filename != server_filename:
            new_dropship_line_vals.update({'filename': server_filename})
        return new_dropship_line_vals

    def _validate_file_headers(self, fieldnames, partner_id, server_filename):
        """
        It will check that some necessary headers must be available in the file.
        :param fieldnames: column headers of the file.
        :param partner_id: partner id
        :param server_filename: name of the file which is used to import product.
        :return: True
        """
        headers = ['Main_product_id', 'Product_code', 'Name', 'Price']
        missing = []
        log_line_obj = self.env['common.log.lines.ept']
        for field in headers:
            if field not in fieldnames:
                missing.append(field)
        if len(missing) > 0:
            job = self.env['common.log.book.ept'].create({
                'application': 'product',
                'type': 'import',
                'partner_id': partner_id.id,
                'filename': server_filename,
                'module': 'dropship_edi_integration_ept',
                'message': "FTP connection has been established successfully.",
            })
            log_line_obj.create(
                {'log_line_id': job.id,
                 'message': "Header %s is required to Import Products. " % missing})
            return False
        return True

    def import_products_from_ftp(self, partner_ids):
        """
        It will check the FTP connection. If the connection is established properly then,
         it will perform the import operations.
        :param partner_ids: supplier ids
        :return: True
        """
        for partner_id in partner_ids:
            try:
                with partner_id.get_dropship_edi_interface(operation="product_import") \
                        as dropship_edi_object:
                    filenames, server_filenames = dropship_edi_object.pull_from_ftp(
                        partner_id.prefix_import_product)
            except Exception:
                self.env['common.log.book.ept'].create({
                    'application': 'product',
                    'type': 'import',
                    'partner_id': partner_id.id,
                    'module': 'dropship_edi_integration_ept',
                    'message': "Supplier %s has problem with FTP connection,"
                               " Please check server credentials and file path." %
                               (partner_id.name)
                })
                continue
            for filename, server_filename in zip(filenames, server_filenames):
                file_reader = csv.DictReader(open(filename, "rU"), delimiter=partner_id.csv_delimiter)
                fieldnames = file_reader.fieldnames
                valid_fields = self._validate_file_headers(fieldnames, partner_id, server_filename)
                if not valid_fields:
                    continue
                self._create_droship_product(file_reader, partner_id, server_filename, filename)
        return True

    def import_stock_from_ftp(self, partner_ids):
        """
        First it will check the FTP connection. If connection is established properly then
        it will import stock from ftp.
        :param partner_ids: supplier ids
        :return: True
        """
        product_obj = self.env['product.product']
        product_supplierinfo_obj = self.env['product.supplierinfo']
        vendor_stock_ept_obj = self.env['vendor.stock.ept']
        for partner_id in partner_ids:
            try:
                with partner_id.get_dropship_edi_interface(operation="stock_import") \
                        as dropship_edi_object:
                    filenames, server_filenames = \
                        dropship_edi_object.pull_from_ftp(partner_id.prefix_import_stock)
            except:
                self.env['common.log.book.ept'].create({
                    'application': 'inventory',
                    'type': 'import',
                    'partner_id': partner_id.id,
                    'module': 'dropship_edi_integration_ept',
                    'message': "Supplier %s has problem with FTP connection,"
                               " Please check server credentials and file path." %
                               (partner_id.name)
                })
                continue
            for filename, server_filename in zip(filenames, server_filenames):
                buffer = StringIO()
                stock_log_field_name = ['Product_code', 'Log_details']
                csvwriter = DictWriter(buffer, stock_log_field_name,
                                       delimiter=partner_id.csv_delimiter or ';')
                csvwriter.writer.writerow(stock_log_field_name)
                row_num = 1
                job = self.env['common.log.book.ept'].create({
                    'application': 'inventory',
                    'type': 'import',
                    'partner_id': partner_id.id,
                    'module': 'dropship_edi_integration_ept',
                    'message': "FTP connection has been established successfully.",
                    'filename': server_filename})
                file_reader = csv.DictReader(open(filename, "rU"), delimiter=partner_id.csv_delimiter)
                fieldnames = file_reader.fieldnames
                headers = ['Product_code', 'Quantity', 'Price']
                missing = []
                for field in headers:
                    if field not in fieldnames:
                        missing.append(field)
                if len(missing) > 0:
                    log_message = (_(" %s is the required field(s) to Import Stock.") %
                                   (str(missing)[1:-1]))
                    self._create_common_log_line(job, csvwriter, log_message)
                    continue
                for line in file_reader:
                    product_code = line.get('Product_code')
                    product_qty = product_price = False
                    update_price = {}
                    update_stock = {}
                    row_num = row_num + 1
                    success_message = ''
                    missing_values = []
                    if not product_code:
                        missing_values.append('Product_code')
                    if line.get('Quantity'):
                        try:
                            product_qty = float(line.get('Quantity'))
                        except ValueError:
                            missing_values.append('Quantity')
                            product_qty = False
                    else:
                        missing_values.append('Quantity')
                    if line.get('Price'):
                        try:
                            product_price = float(line.get('Price'))
                        except ValueError:
                            missing_values.append('Price')
                            product_price = False
                    else:
                        missing_values.append('Price')
                    qty_flag = price_flag = False
                    if product_qty is not False and product_qty >= 0:
                        update_stock.update({'vendor_stock': product_qty})
                        success_message += (_('Quantity : %s ') % product_qty)
                        qty_flag = True
                    if product_price is not False and product_price >= 0:
                        update_price.update({'price': product_price})
                        success_message += (_('and ')) if qty_flag else ''
                        success_message += (_('Price : %s ') % product_price)
                        price_flag = True
                    success_message += (_('updated successfully.'))
                    if product_code and (qty_flag or price_flag):
                        product_id = product_obj.search([
                            ('default_code', '=', product_code)], limit=1)
                        if not product_id:
                            vendor_product_id = product_supplierinfo_obj.search(
                                [('product_code', '=', product_code),
                                 ('name', '=', partner_id.id)], limit=1)
                            if vendor_product_id:
                                if price_flag:
                                    vendor_product_id.write(update_price)
                                vendor_stock = vendor_stock_ept_obj.search([('vendor_product_id', '=', vendor_product_id.product_id.id),
                                 ('vendor', '=', partner_id.id)], limit=1)
                                if vendor_stock:
                                    if qty_flag:
                                        vendor_stock.write(update_stock)
                                else:
                                    log_message = (_("Supplier %s is not available for product to"
                                                     " update stock in odoo.") % partner_id.name)
                                    self._create_common_log_line(job, csvwriter, log_message,
                                                                 product_code)
                                if price_flag or (vendor_stock and qty_flag):
                                    self._create_common_log_line(job, csvwriter, success_message,
                                                                 product_code)
                            else:
                                log_message = (_("Supplier %s is not available for"
                                                 " product in odoo.") % partner_id.name)
                                self._create_common_log_line(job, csvwriter, log_message,
                                                             product_code)
                                continue
                        else:
                            vendor_product_id = product_supplierinfo_obj.search(
                                [('product_id', '=', product_id.id),
                                 ('name', '=', partner_id.id)])
                            if vendor_product_id:
                                if price_flag:
                                    vendor_product_id.write(update_price)
                            else:
                                log_message = (_("Supplier %s is not available for product to"
                                                 " update price in odoo.") % partner_id.name)
                                self._create_common_log_line(job, csvwriter, log_message,
                                                             product_code)
                            vendor_stock = vendor_stock_ept_obj.search(
                                [('vendor_product_id', '=', product_id.id),
                                 ('vendor', '=', partner_id.id)], limit=1)
                            if vendor_stock:
                                if qty_flag:
                                    vendor_stock.write(update_stock)
                            else:
                                log_message = (_("Supplier %s is not available for product to"
                                                 " update stock in odoo.") % partner_id.name)
                                self._create_common_log_line(job, csvwriter, log_message,
                                                             product_code)
                            if (vendor_product_id and price_flag) or (vendor_stock and qty_flag):
                                self._create_common_log_line(job, csvwriter, success_message,
                                                             product_code)
                    else:
                        log_message = (_("Missing/Incorrect field(s) value for %s at"
                                         " row number %s.") %
                                       (missing_values, row_num))
                        self._create_common_log_line(job, csvwriter, log_message)
                        continue
                file = open(filename)
                file.seek(0)
                file_data = file.read().encode()
                if file_data:
                    vals = {
                        'name': server_filename,
                        'datas': base64.encodestring(file_data),
                        'type': 'binary',
                        'res_model': 'common.log.book.ept',
                    }
                    attachment = self.env['ir.attachment'].create(vals)
                    job.message_post(body=_("<b>Supplier's Stock File</b>"),
                                     attachment_ids=attachment.ids)
                # Move file to archive directory
                try:
                    with partner_id.get_dropship_edi_interface(operation="stock_import") \
                            as dropship_tpw_interface:
                        dropship_tpw_interface.archive_file([server_filename])
                except:
                    log_message = (_("Supplier %s has Problem with connection or file Path."
                                     " File can not Move to Archive.") % partner_id.name)
                    self._create_common_log_line(job, csvwriter, log_message)
                # Attach log file with job
                stock_log_filename = "%s_%s" % (server_filename[:-4], 'log_details.csv')
                buffer.seek(0)
                stock_log_file_data = buffer.read().encode()
                if stock_log_file_data:
                    vals = {
                        'name': stock_log_filename,
                        'datas': base64.encodestring(stock_log_file_data),
                        'type': 'binary',
                        'res_model': 'common.log.book.ept',
                    }
                    attachment = self.env['ir.attachment'].create(vals)
                    job.message_post(body=_("<b>Imported Stock Log File</b>"),
                                     attachment_ids=attachment.ids)
                buffer.close()
        return True

    def auto_import_stock_from_ftp(self, ctx={}):
        """
        It performs import stock operation as per the supplier's schedule.
        :param ctx: context to fetch that operation is performed by which supplier.
        :return: True
        """
        partner_obj = self.env['res.partner']
        if not isinstance(ctx, dict) or 'partner_id' not in ctx:
            return True
        partner_id = ctx.get('partner_id', False)
        partner_ids = partner_obj.browse(partner_id)
        if partner_ids:
            self.import_stock_from_ftp(partner_ids)
        return True

    def auto_import_products_from_ftp(self, ctx={}):
        """
        It performs the import products operations as per the supplier's schedule.
        :param ctx: context to fetch that operation is performed by which supplier.
        :return: True
        """
        partner_obj = self.env['res.partner']
        if not isinstance(ctx, dict) or 'partner_id' not in ctx:
            return True
        partner_id = ctx.get('partner_id', False)
        partner_ids = partner_obj.browse(partner_id)
        if partner_ids:
            self.import_products_from_ftp(partner_ids)
        return True
