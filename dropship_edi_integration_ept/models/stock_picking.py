from io import StringIO
from datetime import datetime, timedelta
import base64
from csv import DictWriter
import csv
from odoo import fields, models, _
import logging
import logging
_logger = logging.getLogger(__name__)
class StockPicking(models.Model):
    _inherit = "stock.picking"
    _order = 'partner_id'
    is_exported = fields.Boolean(string="Is Exported?", default=False)
    is_blocked = fields.Boolean(string="Is Blocked?", default=False)

    def export_shipment_orders_to_ftp(self, pickings=False, partner_ids=False):
        """
        It will export shipment orders in CSV file to the supplier's FTP directory path.
        :param pickings: shipment orders
        :param partner_ids: suppliers data
        :return: True
        """
        
        for partner_id in partner_ids:
            #47 pour la prod
            picking_ids = self.search(
               [('is_exported', '!=', True), ('is_blocked', '!=', True),('location_id', '=', 47), ('state', '=', 'assigned'), ]).sorted(key=lambda r: r.partner_id)                 
 
            if picking_ids: 
                buffer = StringIO()
                # Start CSV Writer
                column_headers = ['1','EL','CBD','countObect','Order_no', 'Picking_ref', 'Product_code', 'Quantity',
                                  'First_name', 'Street1', 'Street2',
                                  'Zip', 'City', 'Contact_no', 'Country','Carrier', 'Email']
                export_time = datetime.now()
                filename = "%s_%s" % (
                    partner_id.prefix_shipment_export or "Export_Order",
                    export_time.strftime('%Y_%m_%d_%H_%M_%S.csv'))
                job = self.env['common.log.book.ept'].create({
                    'application': 'shipment',
                    'type': 'export',
                    'module': 'dropship_edi_integration_ept',
                    'partner_id': partner_id.id,
                    'filename': filename
                })
                try:
                    partner_id.ftp_server_id.do_test()
                    job.write({'message': "FTP connection has been established successfully."})
                except Exception:
                    job.write({'message': "Supplier %s has problem with FTP connection or file"
                                          " path. File has not exported to Supplier's FTP." %
                                          (partner_id.name)})
                    break

                csv_writer = DictWriter(buffer, column_headers,
                                        delimiter=partner_id.csv_delimiter or ';')
                #csv_writer.writer.writerow(column_headers)
                commande = 0
                for picking_id in picking_ids:
                    if (picking_id.scheduled_date <= (datetime.now() + timedelta(days=15))) and not picking_id.is_merged :
                        order_not_matched = \
                            self.check_mismatch_details_for_dropship_orders(partner_id, picking_id, job)
                        commande = commande + 1
                        results = self.env['stock.move.line'].search([('picking_id', '=', picking_id.id)])
                        total_objets2 = len(results)
                        data = {
                                '1': commande,
                                'EL': 'E',
                                'CBD': 'CBD',
                                'countObect': total_objets2,
                                'Order_no': picking_id.id,
                                'Picking_ref': picking_id.name,
                                'Product_code': picking_id.scheduled_date.strftime("%Y%m%d"),
                                'Quantity': '',
                                'First_name': picking_id.partner_id.name,
                                'Street1': picking_id.partner_id.street,
                                'Street2': picking_id.partner_id.street2 or '',
                                'Zip': picking_id.partner_id.zip,                            
                                'City': picking_id.partner_id.city,
                                'Contact_no': picking_id.partner_id.mobile
                                            or picking_id.partner_id.phone or '',
                                'Country': picking_id.partner_id.country_id.code,
                                'Carrier': picking_id.carrier_id.name,                                 
                                'Email': picking_id.partner_id.email or '',                                                                 
                            }
                        csv_writer.writerow(data)
                        line = 1
                        for move_line in picking_id.move_lines:
                            product_supplier = self.env['product.supplierinfo'].search(
                                [('product_id', '=', move_line.product_id.id),
                                ('name', '=', partner_id.id)], limit=1)
                            product_code = False
                            if product_supplier.product_code:
                                product_code = product_supplier.product_code
                            elif move_line.product_id.default_code:
                                product_code = move_line.product_id.default_code
                            data = {
                                '1': commande,
                                'EL': 'L',
                                'CBD': 'CBD',
                                'countObect': total_objets2,
                                'Order_no': '',
                                'Picking_ref': '',
                                'Product_code': product_code,
                                'Quantity': int(move_line.reserved_availability),
                                'First_name': 'UUC',
                                'Street1': line,
                                'Street2': '',
                                'Zip': '',
                                'City': '',
                                'Contact_no': '',
                                'Country': '',
                                'Carrier': '',                             
                                'Email': '',                                                                      
                            }
                            
                            if (move_line.reserved_availability > 0):
                                csv_writer.writerow(data)
                                line = line + 1
                                log_message = (_("Dropship order has been exported successfully. "
                                            "| Sale order - %s") % picking_id.sale_id.name)
                                self._create_common_log_line(job, False, log_message,
                                                        picking_id.purchase_id.name, '', '',
                                                        move_line.product_id.id)
                            picking_id.write({'is_exported': True})
                try:
                    if commande > 0:
                        with partner_id.get_dropship_edi_interface(operation="shipment_export") \
                                as dropship_tpw_interface:
                            buffer.seek(0)
                            dropship_tpw_interface.push_to_ftp(filename, buffer)
                except Exception:
                    job.write({'message': "Supplier %s has problem with FTP connection or file"
                                          " path. File has not exported to Supplier's FTP." %
                                          (partner_id.name)})
                buffer.seek(0)
                file_data = buffer.read().encode('iso-8859-1', 'ignore')
                if file_data:
                    vals = {
                        'name': filename,
                        'datas': base64.encodestring(file_data),
                        'type': 'binary',
                        'res_model': 'common.log.book.ept',
                    }
                    attachment = self.env['ir.attachment'].create(vals)
                    job.message_post(body=_("<b>Purchase Order Exported File</b>"),
                                     attachment_ids=attachment.ids)
                    buffer.close()
        return True

    def export_shipment_orders_to_ftp2(self, pickings=False, partner_ids=False):
        """
        It will export shipment orders in CSV file to the supplier's FTP directory path.
        :param pickings: shipment orders
        :param partner_ids: suppliers data
        :return: True
        """
        _logger.info('DANS LA FONCTION')
        for partner_id in partner_ids:
            #47 pour la prod
            picking_ids = self.search(
               [('is_exported', '!=', True), ('is_blocked', '!=', True),('location_id', '=', 8), ('state', '=', 'assigned'), ]).sorted(key=lambda r: r.partner_id)                 
 
            if picking_ids: 
                buffer = StringIO()
                # Start CSV Writer
                column_headers = ['1','EL','CBD','countObect','Order_no', 'Picking_ref', 'Product_code', 'Quantity',
                                  'First_name', 'Street1', 'Street2',
                                  'Zip', 'City', 'Contact_no', 'Country','Carrier', 'Email']
                export_time = datetime.now()
                filename = "%s_%s" % (
                    "ZINALL",
                    export_time.strftime('%Y_%m_%d_%H_%M_%S.csv'))
                job = self.env['common.log.book.ept'].create({
                    'application': 'shipment',
                    'type': 'export',
                    'module': 'dropship_edi_integration_ept',
                    'partner_id': partner_id.id,
                    'filename': filename
                })
                try:
                    partner_id.ftp_server_id.do_test()
                    job.write({'message': "FTP connection has been established successfully."})
                except Exception:
                    job.write({'message': "Supplier %s has problem with FTP connection or file"
                                          " path. File has not exported to Supplier's FTP." %
                                          (partner_id.name)})
                    break

                csv_writer = DictWriter(buffer, column_headers,
                                        delimiter=partner_id.csv_delimiter or ';')
                #csv_writer.writer.writerow(column_headers)
                commande = 0
                for picking_id in picking_ids:
                    if (picking_id.scheduled_date <= (datetime.now() + timedelta(days=1005))) and not picking_id.is_merged :
                        order_not_matched = \
                            self.check_mismatch_details_for_dropship_orders(partner_id, picking_id, job)
                        commande = commande + 1
                        results = self.env['stock.move.line'].search([('picking_id', '=', picking_id.id)])
                        total_objets2 = len(results)
                        data = {
                                '1': commande,
                                'EL': 'E',
                                'CBD': 'CBD',
                                'countObect': total_objets2,
                                'Order_no': picking_id.id,
                                'Picking_ref': picking_id.name,
                                'Product_code': picking_id.scheduled_date.strftime("%Y%m%d"),
                                'Quantity': '',
                                'First_name': picking_id.partner_id.name,
                                'Street1': picking_id.partner_id.street,
                                'Street2': picking_id.partner_id.street2 or '',
                                'Zip': picking_id.partner_id.zip,                            
                                'City': picking_id.partner_id.city,
                                'Contact_no': picking_id.partner_id.mobile
                                            or picking_id.partner_id.phone or '',
                                'Country': picking_id.partner_id.country_id.code,
                                'Carrier': picking_id.carrier_id.name,                                 
                                'Email': picking_id.partner_id.email or '',                                                                 
                            }
                        csv_writer.writerow(data)
                        line = 1
                        for move_line in picking_id.move_lines:
                            product_supplier = self.env['product.supplierinfo'].search(
                                [('product_id', '=', move_line.product_id.id),
                                ('name', '=', partner_id.id)], limit=1)
                            product_code = False
                            if product_supplier.product_code:
                                product_code = product_supplier.product_code
                            elif move_line.product_id.default_code:
                                product_code = move_line.product_id.default_code
                            data = {
                                '1': commande,
                                'EL': 'L',
                                'CBD': 'CBD',
                                'countObect': total_objets2,
                                'Order_no': '',
                                'Picking_ref': '',
                                'Product_code': product_code,
                                'Quantity': int(move_line.reserved_availability),
                                'First_name': 'UUC',
                                'Street1': line,
                                'Street2': '',
                                'Zip': '',
                                'City': '',
                                'Contact_no': '',
                                'Country': '',
                                'Carrier': '',                             
                                'Email': '',                                                                      
                            }
                            
                            if (move_line.reserved_availability > 0):
                                csv_writer.writerow(data)
                                line = line + 1
                                log_message = (_("Dropship order has been exported successfully. "
                                            "| Sale order - %s") % picking_id.sale_id.name)
                                self._create_common_log_line(job, False, log_message,
                                                        picking_id.purchase_id.name, '', '',
                                                        move_line.product_id.id)
                            picking_id.write({'is_exported': True})
                try:
                    if commande > 0:
                        with partner_id.get_dropship_edi_interface(operation="shipment_export") \
                                as dropship_tpw_interface:
                            buffer.seek(0)
                            dropship_tpw_interface.push_to_ftp(filename, buffer)
                except Exception:
                    job.write({'message': "Supplier %s has problem with FTP connection or file"
                                          " path. File has not exported to Supplier's FTP." %
                                          (partner_id.name)})
                buffer.seek(0)
                file_data = buffer.read().encode('iso-8859-1', 'ignore')
                if file_data:
                    vals = {
                        'name': "ZINALL",
                        'datas': base64.encodestring(file_data),
                        'type': 'binary',
                        'res_model': 'common.log.book.ept',
                    }
                    attachment = self.env['ir.attachment'].create(vals)
                    job.message_post(body=_("<b>Purchase Order Exported File</b>"),
                                     attachment_ids=attachment.ids)
                    buffer.close()
        return True
    
    def check_mismatch_details_for_dropship_orders(self, partner_id, picking_id, job):
        """
        It will verify the dropship order details. If any necessary details are missing then it will
         skip that order while export.
        :param partner_id: supplier
        :param picking_id: dropship order
        :param job: common log book object
        :return: orders data which have missing field values.
        """
        order_not_matched = False
        missing_values = []
        order_no = picking_id.origin
        first_name = picking_id.partner_id.name or ''
        street1 = picking_id.partner_id.street
        country = picking_id.partner_id.country_id.name or ''
        state = picking_id.partner_id.state_id.name or ''
        city = picking_id.partner_id.city or ''
        zip = picking_id.partner_id.zip or ''

        if not first_name:
            missing_values.append('First_name')
        if not street1:
            missing_values.append('Street1')
        if not country:
            missing_values.append('Country')
        if not state:
            missing_values.append('State')
        if not city:
            missing_values.append('City')
        if not zip:
            missing_values.append('Zip')
        if missing_values:
            log_message = (_("Dropship order has been skipped, due to this mandatory"
                             " field(s) %s value has been not inserted | Sale Order - %s ") %
                           (str(missing_values)[1:-1], picking_id.sale_id.name))
            self._create_common_log_line(job, False, log_message, order_no)
            order_not_matched = True

        for move_line in picking_id.move_lines:
            product_supplier = self.env['product.supplierinfo'].search(
                [('product_id', '=', move_line.product_id.id),
                 ('name', '=', partner_id.id)], limit=1)
            if not product_supplier.product_code and not move_line.product_id.default_code:
                log_message = (_("Dropship order has been skipped, due to product has been"
                                 " not found in odoo."))
                self._create_common_log_line(job, False, log_message, order_no, '', '',
                                             move_line.product_id.id)
                order_not_matched = True
        return order_not_matched

    
    def import_shipment_orders_from_ftp_control(self, partner_ids):
        for partner_id in partner_ids:
            try:
                with partner_id.get_dropship_edi_interface(operation="shipment_import") \
                        as dropship_edi_object:
                    filenames, server_filenames = \
                        dropship_edi_object.pull_from_ftp2(partner_id.prefix_import_shipment)
                
            except:
                self.env['common.log.book.ept'].create({
                    'application': 'shipment',
                    'type': 'import',
                    'partner_id': partner_id.id,
                    'module': 'dropship_edi_integration_ept',
                    'message': "No File to import "
                })
            for filename, server_filename in zip(filenames, server_filenames):
                _logger.info('>>>>>>>>>>>>>>>>FICHIERS A TRAIER : ' + str(server_filenames))
                self.import_shipment_orders_from_ftp(partner_id,filename, server_filename)
            return True
                
    
    def import_shipment_orders_from_ftp(self, partner_id, filename, server_filename):
        """
        It will import shipment orders from FTP.If order fulfil the required condition then
         order will be validated.
        :param partner_ids: suppliers
        :return: True
        """
        
        validate_picking_ids = []
        
        """ try:
            with partner_id.get_dropship_edi_interface(operation="shipment_import") \
                    as dropship_edi_object:
                filenames, server_filenames = \
                    dropship_edi_object.pull_from_ftp2(partner_id.prefix_import_shipment)
        except:
            self.env['common.log.book.ept'].create({
                'application': 'shipment',
                'type': 'import',
                'partner_id': partner_id.id,
                'module': 'dropship_edi_integration_ept',
                'message': "No File to import or Supplier %s has problem with FTP connection,"
                            " Please check server credentials and file path." % (partner_id.name)
            }) """

            #continue

        #for filename, server_filename in zip(filenames, server_filenames):
        #try:
        buffer = StringIO()
        #field_name = ['LineQty', 'totalline', 'Product_code', 'Order_ref', 'Tracking_no', 'date']
        field_name = ['Order_ref', 'Product_code', 'Log_details', 'Tracking_no']
        csvwriter = DictWriter(buffer, field_name,
                            delimiter=partner_id.csv_delimiter or ';')
        csvwriter.writer.writerow(field_name)
        job = self.env['common.log.book.ept'].create({
            'application': 'shipment',
            'type': 'import',
            'partner_id': partner_id.id,
            'module': 'dropship_edi_integration_ept',
            'message': "FTP connection has been established successfully.",
            'filename': server_filename
        })
        
        reader = csv.DictReader(open(filename, "rU", encoding='iso-8859-1'),
                                delimiter=partner_id.csv_delimiter)
        fieldnames = reader.fieldnames
        headers = ['LineQty', 'totalline', 'Product_code', 'Order_ref', 'Tracking_no', 'date']
        missing = []
        #for field in headers:
        #    if field not in fieldnames:
        #        missing.append(field)
        if len(missing) > 0:
            log_message = (_("%s is the required field(s) to Import Shipment details.") %
                        (str(missing)[1:-1]))
            self._create_common_log_line(job, csvwriter, log_message)
            #continue
        log_message = ''
        #skip_purchase_order_ids = \
            #self.check_mismatch_details_for_import_shipment(csvwriter, job, reader)
        #reader = csv.DictReader(open(filename, "rU"),
                                #delimiter=partner_id.csv_delimiter, fieldnames=None)
        filecsv = open(filename, "r", encoding='iso-8859-1')
        reader = csv.reader(filecsv, delimiter=partner_id.csv_delimiter)
        stock_pickng_id = 0
        order_ref_prev = ''
        product_ref_prev = ''
        lot_traites = []
        i = 1
        _logger.info('>>>>>>>>>>>>>>>>Fichier CSV : ' + str(server_filename))
        for line in reader:
            _logger.info('>>>>>>>>>>>>>>>>Ligne CSV : ' + str(i))
            if len(line) > 3:
                order_ref = line[3] or ''#3
                order_no = line[3] or ''#3
            else:
                order_ref = ''
                order_no = ''
            if len(line) > 2:
                product_code = line[2] or ''
            else:
                product_code = ''
            if len(line) > 0:
                num_lot = line[1] or ''
            else:
                num_lot = ''
            
            product_qty = line[0] or ''
            
            i = i + 1
            
            
            
            #Gestion de la premi??re ligne ECTRA
            if str(product_qty) == 'E':
                #del lot_existants[:]
                stock_pickng_id = self.search([('name', '=', order_ref),
                                        ('state', 'not in', ['done', 'cancel'])],
                                        limit=1)
                
                order_ref_prev = order_ref
                
                #if not stock_pickng_id:
                #   continue

                log_message = 'Traitement du BP N?? ' + str(order_ref)
                self._create_common_log_line(job, csvwriter, log_message)
            
            #Gestion des numeros de lot livr??s
            if product_code == '':
                product_code = product_ref_prev
                product_qty = 1

                #Numero du lot ?? importer
                self._create_common_log_line(job, csvwriter, log_message)
                stock_lot_id = self.env['stock.production.lot'].search([('name', '=', num_lot)],limit=1)

                #quant associ?? au lot import??
                stock_quant_id = self.env['stock.quant'].search([('lot_id', '=', stock_lot_id.id),
                                        ('location_id', '=', 47)], limit=1)

                if stock_lot_id:
                    #on cherche tous les lot associ?? au BL en auto
                    self.env.cr.execute("select lot_id from stock_move_line where product_id= " + str(stock_lot_id.product_id.id) + " and reference='" + str(order_ref_prev) + "'")# + "' and importednum IS NOT TRUE")
                    ids_returned = self.env.cr.fetchone()
                    if ids_returned:
                        log_message = '' 
                    else:
                        log_message = 'le numero de lot n\'existe pas ou a d??j?? ??t?? affect??' 
                        self._create_common_log_line(job, csvwriter, log_message)
                        continue
                

                    if (stock_lot_id.id in ids_returned) and (str(stock_lot_id.name) != str(num_lot)):
                        self.env.cr.execute("update stock_move_line set qty_done = 1 where lot_id = " + str(stock_lot_id.id) + " and reference = '" + str(order_ref_prev) +"'" )
                        log_message = 'REF : ' + str(product_ref_prev) + ' - SN : ' + str(stock_lot_id.name)
                        self._create_common_log_line(job, csvwriter, log_message)
                    else:
                        #on appelle la fonction de SWAP des Num lot
                        _logger.info('>>>>>>>>>>>>>>>> DANS LE SWAP')
                        self.swap_num_lot(csvwriter, job, stock_lot_id.id, ids_returned[0], order_ref_prev)
                        self.env.cr.execute("update stock_move_line set qty_done = 1 where lot_id = " + str(stock_lot_id.id) + " and reference = '" + str(order_ref_prev) +"'" )
                        log_message = 'REF : ' + str(product_ref_prev) + ' - SN : ' + str(stock_lot_id.name)
                        _logger.info('SWAP REF : ' + str(product_ref_prev) + ' - SN : ' + str(stock_lot_id.name))
                        self._create_common_log_line(job, csvwriter, log_message)

            else:    
                product_ref_prev = line[2] or ''
                #log_message = 'Reference Pr??c??dente : ' + str(product_ref_prev) + ' - line : ' + str(line[2])
                #self._create_common_log_line(job, csvwriter, log_message)  
                if line[2] != 'CBD' and  product_ref_prev != 'CBD':
                    log_message = 'Reference Produit trait??e : ' + str(product_ref_prev) + ' - Quantit?? livr??e : ' + str(product_qty)
                    self._create_common_log_line(job, csvwriter, log_message)  
                product_ref_prev = line[2] or ''


            tracking_no = filename
            product_vendor_code_id = self.env['product.product'].search(
                [('default_code', '=', product_code)])
            
            self.env.cr.execute("select id from product_product where default_code = '" + str(product_code) + "'" )
            lot_retourne = self.env.cr.fetchall()
            
            if lot_retourne:
                stock_move_id = self.env['stock.move'].search(
                    [('product_id', 'in', lot_retourne),('reference', '=', order_ref_prev)], limit=1)
                if stock_move_id:
                    stock_move_id.picking_id.write({'is_exported': False})
                    stock_move_id.picking_id.write({'note': str(filename)})
                    
                    if stock_move_id.product_uom_qty < float(product_qty):
                        log_message = (_("1 - Product ordered quantity %s and shipped"
                                        " quantity %s") %
                                    (stock_move_id.product_uom_qty, product_qty))
                        #self._create_common_log_line(job, csvwriter, log_message, order_no,
                        #                            '', product_code,
                        #                           lot_retourne.id)
                    stock_move_id.move_line_ids.write({'qty_done': float(product_qty)})
                    validate_picking_ids.append(stock_move_id.picking_id)
                    # if tracking_no:
                    #     if stock_move_id.picking_id.carrier_tracking_ref:
                    #         stock_move_id.picking_id.write(
                    #             {'carrier_tracking_ref': str(
                    #                 '%s,%s' %
                    #                 (stock_move_id.picking_id.carrier_tracking_ref,
                    #                  tracking_no))})
                    #     else:
                    #         stock_move_id.picking_id.write(
                    #             {'carrier_tracking_ref': tracking_no})
            else:
                product_id = self.env['product.product'].search([
                    ('default_code', '=', product_code)], limit=1)
                if product_id:
                    stock_move_id = self.env['stock.move'].search(
                        [('product_id', '=', product_id.id),
                        ('origin', '=', stock_pickng_id.origin)], limit=1)
                    if stock_move_id:
                        if stock_move_id.product_uom_qty < float(product_qty):
                            log_message = (_("2 - Product ordered quantity %s and"
                                            " shipped quantity %s") %
                                        (stock_move_id.product_uom_qty, product_qty))
                            self._create_common_log_line(job, csvwriter, log_message,
                                                        order_no, '',
                                                        product_code, product_id.id)
                        stock_move_id.move_line_ids.write({'qty_done': product_qty})
                        
                        validate_picking_ids.append(stock_move_id.picking_id)
                        
                        if tracking_no:
                            if stock_move_id.picking_id.carrier_tracking_ref:
                                stock_move_id.picking_id.write(
                                    {'carrier_tracking_ref':
                                        str('%s,%s' %
                                            (stock_move_id.picking_id.carrier_tracking_ref,
                                            tracking_no))})
                            else:
                                stock_move_id.picking_id.write(
                                    {'carrier_tracking_ref': tracking_no})
        if product_code != '':
            for validate_picking_id in list(set(validate_picking_ids)):
                #tracking_no = validate_picking_id.carrier_tracking_ref
                validate_picking_id.action_done()
                validate_picking_id.write({'is_exported': True})
                log_message = (_("Dropship order validated successfully."))
                self._create_common_log_line(job, csvwriter, log_message,
                                            validate_picking_id.origin, tracking_no)
                
            
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
                job.message_post(body=_("<b>Imported Shipment's File</b>"),
                                attachment_ids=attachment.ids)

            try:
                with partner_id.get_dropship_edi_interface(
                        operation="shipment_import") as dropship_tpw_interface:
                    dropship_tpw_interface.archive_file([server_filename])
            except:
                job.write({
                    'message': "Supplier %s has problem with connection or file Path."
                            " File can not move to Archive." % partner_id.name})

            

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
            _logger.info('>>>>>>>>>>>>>>>>DANS LES LOGS : ' )
            attachment = self.env['ir.attachment'].create(vals)
            job.message_post(body=_("<b>Imported Shipment's Log File</b>"),
                                attachment_ids=attachment.ids)
            #buffer.close() 

        

    def swap_num_lot(self,csvwriter, job, lot_import_id, lot_existant_id, reference):
        #On cherche si le lot import?? est affect?? sur un BL
        try:
            log_message = 'id import num lot :  ' + str(lot_import_id) + ' id lot existant : ' + str(lot_existant_id) + ' REF : ' + str(reference)
            _logger.info('id import num lot :  ' + str(lot_import_id) + ' id lot existant : ' + str(lot_existant_id) + ' REF : ' + str(reference))

            if lot_import_id:
                self.env.cr.execute("select count(id) from stock_quant where lot_id = " + str(lot_import_id) + " ")
                count = self.env.cr.fetchone()
                if count[0] > 0:
                    _logger.info('+++++++ 1Mise ?? jour QUANT SERIAL IMPORT')
                    self.env.cr.execute("update stock_quant set location_id=47 where lot_id=" + str(lot_import_id) + " and location_id=9")
                    self.env.cr.execute("update stock_quant set reserved_quantity=1 where lot_id=" + str(lot_import_id) + " and location_id=47")
            
            if lot_existant_id:        
                self.env.cr.execute("select count(id) from stock_quant where lot_id = " + str(lot_existant_id) + " ")
                count = self.env.cr.fetchone()
                if count[0] > 0:
                    _logger.info('+++++++ 1Mise ?? jour QUANT SERIAL EXISTANT')
                    self.env.cr.execute("update stock_quant set location_id=47 where lot_id=" + str(lot_existant_id) + " and location_id=9")
                    self.env.cr.execute("update stock_quant set reserved_quantity=1 where lot_id=" + str(lot_existant_id) + " and location_id=47")


            self._create_common_log_line(job, csvwriter, log_message)
            stock_move_line_import_id = self.env['stock.move.line'].search(
                                [('lot_id', '=', lot_import_id),
                                ('location_id', '=', 47),], limit=1)

            #On cherche quel lot est affect?? sur le BL
            stock_move_line_old_id = self.env['stock.move.line'].search(
                                [('lot_id', '=', lot_existant_id),
                                ('location_id', '=', 47),], limit=1)
            log_message = 'stock_move_line_import_id : ' + str(stock_move_line_import_id) + ' stock_move_line_old_id : ' + str(stock_move_line_old_id) + ' REF : ' + str(reference)
            _logger.info('stock_move_line_import_id : ' + str(stock_move_line_import_id) + ' stock_move_line_old_id : ' + str(stock_move_line_old_id) + ' REF : ' + str(reference))
            self._create_common_log_line(job, csvwriter, log_message)

            if stock_move_line_old_id and stock_move_line_import_id:
                id_temp1 = stock_move_line_old_id
                id_temp2 = stock_move_line_import_id
                log_message = 'On a les 2 -> id_temp1 : ' + str(id_temp1) + ' id_temp2 : ' + str(id_temp2)
                _logger.info('On a les 2 -> id_temp1 : ' + str(id_temp1) + ' id_temp2 : ' + str(id_temp2))
                self._create_common_log_line(job, csvwriter, log_message)

                #Le Num??ro de lot est d??j?? affect??
                if stock_move_line_import_id.reference ==  reference:
                    log_message = 'Le lot du BL est d??j?? affect?? au BL' + str(id_temp1) + ' - ' + str(id_temp2)
                    _logger.info('Le lot du BL est d??j?? affect?? au BL' + str(id_temp1) + ' - ' + str(id_temp2))
                    self._create_common_log_line(job, csvwriter, log_message)
                    return True

                if id_temp2:
                    _logger.info('____________________IDTEMP2')
                    _logger.info(id_temp2)
                    _logger.info(id_temp1)
                    _logger.info('____________________')
                    self.env.cr.execute("select id from stock_move_line where lot_id = " + str(lot_import_id) + " and location_id= 47 and location_dest_id = 9")
                    lot_retourne = self.env.cr.fetchone()
                    
                    tempId = lot_retourne[0]
                    #PB si tout est r??serv??
                    #On doit faire attention suite aux manip sur Serial de verifier les quants
                    self.env.cr.execute("select count(id) from stock_quant where lot_id = " + str(lot_import_id) + " ")
                    count = self.env.cr.fetchone()
                    if count[0] == 2:
                        _logger.info('+++++++ 1Mise ?? jour QUANT SERIAL IMPORT')
                        self.env.cr.execute("update stock_quant set location_id=47 where lot_id=" + str(lot_import_id) + " and location_id=9")
                        self.env.cr.execute("update stock_quant set reserved_quantity=1 where lot_id=" + str(lot_import_id) + " and location_id=47")
                    
                    self.env.cr.execute("select count(id) from stock_quant where lot_id = " + str(lot_existant_id) + " ")
                    count = self.env.cr.fetchone()
                    if count[0] == 2:
                        _logger.info('+++++++ 1Mise ?? jour QUANT SERIAL EXISTANT')
                        self.env.cr.execute("update stock_quant set location_id=47 where lot_id=" + str(lot_existant_id) + " and location_id=9")
                        self.env.cr.execute("update stock_quant set reserved_quantity=1 where lot_id=" + str(lot_existant_id) + " and location_id=47")

                    

                    self.env.cr.execute("update stock_move_line set lot_id = " + str(lot_import_id) + " where lot_id= " + str(lot_existant_id) + " and reference='" + str(reference) + "' and location_id= 47 and location_dest_id = 9")
                    self.env.cr.execute("update stock_move_line set lot_id = " + str(lot_existant_id) + " where id= " + str(tempId) + "  and location_id= 47 and location_dest_id = 9")
                stock_move_line_old_id.importednum = True 
                return True

            #Le nouveau lot n'est pas r??serv?? on doit d??sallouer le lot en cours sur le BL et le remplacer par le nouveau livr??    
            if stock_move_line_old_id and not stock_move_line_import_id and lot_existant_id:
                #On affecte le nouveau numero ?? la ligne

                self.env.cr.execute("select count(id) from stock_quant where lot_id = " + str(lot_import_id) + " ")
                count = self.env.cr.fetchone()
                if count[0] == 2:
                    _logger.info('+++++++ 2Mise ?? jour QUANT SERIAL IMPORT')
                    self.env.cr.execute("update stock_quant set location_id=47 where lot_id=" + str(lot_import_id) + " and location_id=9")
                    self.env.cr.execute("update stock_quant set reserved_quantity=1 where lot_id=" + str(lot_import_id) + " and location_id=47")
                
                self.env.cr.execute("select count(id) from stock_quant where lot_id = " + str(lot_existant_id) + " ")
                count = self.env.cr.fetchone()
                if count[0] == 2:
                    _logger.info('+++++++ 2Mise ?? jour QUANT SERIAL EXISTANT')
                    self.env.cr.execute("update stock_quant set location_id=47 where lot_id=" + str(lot_existant_id) + " and location_id=9")
                    self.env.cr.execute("update stock_quant set reserved_quantity=1 where lot_id=" + str(lot_existant_id) + " and location_id=47")

                if not stock_move_line_old_id.importednum:
                    stock_move_line_old_id.lot_id = lot_import_id
                    stock_move_line_old_id.importednum = True
                self.env.cr.execute("select id from stock_move_line where lot_id = " + str(lot_existant_id) + " and location_id= 47 and location_dest_id = 9")
                lot_retourne = self.env.cr.fetchone() 
                if  lot_retourne:
                    tempId = lot_retourne[0]
                    self.env.cr.execute("update stock_move_line set lot_id = " + str(lot_import_id) + " where id= " + str(tempId) + "  and location_id= 47 and location_dest_id = 9")
                    return True


            if not stock_move_line_old_id and stock_move_line_import_id:
                _logger.info('+++++++ LAST')
                #id_temp1 = stock_move_line_old_id.lot_id
                id_temp2 = stock_move_line_import_id.lot_id
                log_message = 'On a le nouveau et pas l\'ancien -> id_temp1 : ' + str(stock_move_line_old_id.lot_id ) + ' id_temp2 : ' + str(id_temp2)
                self._create_common_log_line(job, csvwriter, log_message)
                stock_move_line_old_id.lot_id  = id_temp2
                #stock_move_line_import_id.lot_id  = id_temp1
                return True
            return False
        except:
            return False


    def check_mismatch_details_for_import_shipment(self, csvwriter, job, data):
        """
        It will check that orders should not be already processed or cancelled before the import.
        :param csvwriter: csvwriter object
        :param job: common log book object
        :param data: order data
        :return: purchase order details which need to be skip.
        """
        missing_values = []
        skip_purchase_order_ids = []
        row_num = 1
        for line in data:
            order_no = line.get('Order_no', False)
            order_ref = line.get('Picking_ref', False)
            stock_picking_id = self.search([('name', '=', order_ref),
                                            ('state', 'not in', ['done', 'cancel'])], limit=1)
            done_stock_picking_id = self.search([('name', '=', order_ref),
                                                 ('state', '=', 'done')], limit=1)
            cancel_stock_picking_id = self.search([('name', '=', order_ref),
                                                   ('state', '=', 'cancel')], limit=1)
            product_code = line.get('Product_code', False)
            product_qty = line.get('Quantity', False)
            tracking_no = line.get('Tracking_no', False)
            row_num = row_num + 1
            if not order_ref:
                missing_values.append('Picking_ref')
            if not order_no:
                missing_values.append('Order_no')
            if not product_code:
                missing_values.append('Product_code')
            if not product_qty:
                missing_values.append('Quantity')
            if not tracking_no:
                missing_values.append('Tracking_no')
            if missing_values:
                log_message = (_("Missing field(s) value for %s at row number %s.") %
                               (str(missing_values)[1:-1], row_num))
                self._create_common_log_line(job, csvwriter, log_message)
                skip_purchase_order_ids.append(stock_picking_id.id)
                continue

            if done_stock_picking_id:
                log_message = (_("This order no. %s has been already processed.") % order_ref)
                self._create_common_log_line(job, csvwriter, log_message, order_no)
                skip_purchase_order_ids.append(done_stock_picking_id.id)
                continue

            if cancel_stock_picking_id:
                log_message = (_("This order no %s has been already cancelled.") % order_ref)
                self._create_common_log_line(job, csvwriter, log_message, order_no)
                skip_purchase_order_ids.append(cancel_stock_picking_id.id)
                continue

            if stock_picking_id:
                product_vendor_code_id = self.env['product.supplierinfo'].search([
                    ('product_code', '=', product_code)], limit=1)
                product_id = self.env['product.product'].search([
                    ('default_code', '=', product_code)], limit=1)
                if not product_vendor_code_id and not product_id:
                    log_message = (_("Product has been not found in odoo."))
                    self._create_common_log_line(job, csvwriter, log_message, order_no, '',
                                                 product_code)
                    skip_purchase_order_ids.append(cancel_stock_picking_id.id)
                    continue
            else:
                log_message = (_("There is no Dropship order like %s in odoo.") % order_ref)
                self._create_common_log_line(job, csvwriter, log_message, order_no)
                skip_purchase_order_ids.append(cancel_stock_picking_id.id)
                continue
        return skip_purchase_order_ids

    def _create_common_log_line(self, job, csvwriter, log_message, order_no='', tracking_no='',
                                product_code='', product_id=''):
        """
        It will create the common log line for the dropship operations.
        :param job: job object
        :param csvwriter: csv writer object
        :param log_message: message for the process
        :param tracking_no: shipment tracking no
        :return: True
        """
        self.env['common.log.lines.ept'].create(
            {'log_line_id': job.id, 'message': log_message, 'order_ref': order_no,
             'tracking_no': tracking_no, 'default_code': product_code, 'product_id': product_id})
        if csvwriter:
            csvwriter.writerow({'Order_ref': order_no, 'Product_code': product_code,
                                'Log_details': log_message, 'Tracking_no': tracking_no})
        return True

    def auto_export_shipment_orders_to_ftp(self, ctx={}):
        """
        It will export the shipment orders to the FTP as per the supplier's schedule.
        :param ctx: context to fetch that operation is performed by which supplier.
        :return: True
        """
        partner_obj = self.env['res.partner']
        stock_picking_obj = self.env['stock.picking']
        if not isinstance(ctx, dict) or 'partner_id' not in ctx:
            return True
        partner_id = ctx.get('partner_id', False)
        partner_ids = partner_obj.browse(partner_id)
        picking_ids = stock_picking_obj.search(
            [('picking_type_id.is_dropship_process', '=', True),
             ('partner_id', 'in', partner_ids.ids),
             ('state', 'not in', ('cancel', 'done')), ('is_exported', '!=', True)])
        if partner_ids and picking_ids:
            self.export_shipment_orders_to_ftp(picking_ids, partner_ids)
        return True

    def auto_import_shipment_orders_from_ftp(self, ctx={}):
        """
        It will import the shipment orders from the FTP as per the supplier's schedule.
        :param ctx: context to fetch that operation is performed by which supplier.
        :return: True
        """
        partner_obj = self.env['res.partner']
        if not isinstance(ctx, dict) or 'partner_id' not in ctx:
            return True
        partner_id = ctx.get('partner_id', False)
        partner_ids = partner_obj.browse(partner_id)
        if partner_ids:
            self.import_shipment_orders_from_ftp(partner_ids)
        return True

