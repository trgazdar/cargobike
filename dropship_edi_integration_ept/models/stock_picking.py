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
    
    def unreserve_picking(self):
        lot_traites = []
        stock_picking_ids = self.search([('location_id', '=', 47),
                                                   ('state', 'in', ['assigned', 'partialy_assigned']),
                                                   ('is_merged', 'in', [False, None])])
        _logger.info(str(stock_picking_ids))
        for picking_ready in stock_picking_ids:
            _logger.info(str(picking_ready.name))
            try: 
                picking_ready.do_unreserve()
                lot_traites.append(picking_ready.id)
            except:
                _logger.info("Impossible de déréserver le BP :" + str(picking_ready.id))
                
        return lot_traites

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

    def import_shipment_orders_from_ftp(self, partner_ids):
        """
        It will import shipment orders from FTP.If order fulfil the required condition then
         order will be validated.
        :param partner_ids: suppliers
        :return: True
        """
        for partner_id in partner_ids:
            validate_picking_ids = []
            lot_traites = []
            lot_traites = self.unreserve_picking()
            product_code = ''
            serialtmp = ''

            
            try:
                with partner_id.get_dropship_edi_interface(operation="shipment_import") \
                        as dropship_edi_object:
                    filenames, server_filenames = \
                        dropship_edi_object.pull_from_ftp(partner_id.prefix_import_shipment)
            except:
                self.env['common.log.book.ept'].create({
                    'application': 'shipment',
                    'type': 'import',
                    'partner_id': partner_id.id,
                    'module': 'dropship_edi_integration_ept',
                    'message': "Supplier %s has problem with FTP connection,"
                               " Please check server credentials and file path." % (partner_id.name)
                })
                continue

            for filename, server_filename in zip(filenames, server_filenames):
                buffer = StringIO()
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
                if len(missing) > 0:
                    log_message = (_("%s is the required field(s) to Import Shipment details.") %
                                   (str(missing)[1:-1]))
                    self._create_common_log_line(job, csvwriter, log_message)
                    continue
                log_message = ''
                filecsv = open(filename, "r", encoding='iso-8859-1')
                reader = csv.reader(filecsv, delimiter=partner_id.csv_delimiter)
                stock_pickng_id = 0
                order_ref_prev = ''
                product_ref_prev = ''
                tracking_no = filename
                
                i = 1

                
                stop = 0
                for line in reader:
                    _logger.info("NOMBRE DE CHAMPS : " + str(len(line)))
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
                    
                    #Gestion de la première ligne ECTRA
                    if str(product_qty) == 'E':
                        stock_pickng_id = self.search([('name', '=', order_ref)])
                        if stock_pickng_id:
                            stop = 0
                            #validate_picking_ids.append(stock_pickng_id)
                            _logger.info("AJOUT DES PICKING : " + str(validate_picking_ids))
                        else:
                            stop = 1
                            job.write({
                                'message': "Des erreurs sont survenues lors de l'import vérifier les logs" })
                            log_message = 'ERREUR LE BP N° ' + str(order_ref) + " N'EXISTE PAS DANS ODOO"
                            self._create_common_log_line(job, csvwriter, log_message)
                        if stock_pickng_id:
                            if stock_pickng_id[0].id in lot_traites :
                                lot_traites.remove(stock_pickng_id[0].id)
                        order_ref_prev = order_ref
                        log_message1 = 'Traitement du BP N° ' + str(order_ref)
                        self._create_common_log_line(job, csvwriter, log_message1)
                    
                    #Gestion des numeros de lot livrés
                    elif stop == 0:
                        #stock_lot_id = self.env['stock.production.lot'].search([('name', '=', num_lot)],limit=1)
                        if product_code == '' and len(line) == 2:
                            product_code = product_ref_prev
                            product_qty = 1
                            stock_lot_id = self.env['stock.production.lot'].search([('name', '=', num_lot)],limit=1)
                            
                            if stock_lot_id:
                                self.env.cr.execute("select picking_id from stock_move where reference = '" + str(order_ref_prev)+"'" )
                                picking_en_cours = self.env.cr.fetchone()
    
                                if picking_en_cours:
                                    serialtmp += product_code + " : " + stock_lot_id.name + "\r\n"
                                    _logger.info(str(server_filename) + " - insert into stock_move_line (date, picking_id, product_id, product_uom_id, product_qty, product_uom_qty,qty_done,lot_id,location_id,location_dest_id,state,reference,company_id) values( '2021-12-16'," + str(picking_en_cours[0]) + " , " + str(stock_lot_id.product_id.id) + " ,1,1,1,1," + str(stock_lot_id.id) + ",47,9,'assigned','" + str(order_ref_prev) )
                                    self.env.cr.execute("update stock_quant set location_id=47 where lot_id = " + str(stock_lot_id.id) + " and location_id=9;")
                                    self.env.cr.execute("update stock_quant set reserved_quantity = 1 where lot_id = " + str(stock_lot_id.id) + " and location_id=47;")
                                    self.env.cr.execute("insert into stock_move_line (date, picking_id, product_id, product_uom_id, product_qty, product_uom_qty,qty_done,lot_id,location_id,location_dest_id,state,reference,company_id) values( '2021-12-16'," + str(picking_en_cours[0]) + " , " + str(stock_lot_id.product_id.id) + " ,1,1,1,1," + str(stock_lot_id.id) + ",47,9,'assigned','" + str(order_ref_prev) + "',1 )")
                                else:
                                    log_message = 'Impossible de traiter le BP :' + str(order_ref_prev) + ' Celui-ci n\'est pas présent dans Odoo'
                                    self._create_common_log_line(job, csvwriter, log_message)
                                    job.write({
                                        'message': "Des erreurs sont survenues lors de l'import vérifier les logs" }) 
                                    stop = 1
                                    
                        elif len(line) == 3 and product_code != '':  
                            #str(product_id.id)  
                            product_id = self.env['product.product'].search([
                                            ('default_code', '=', str(line[2]))], limit=1)
                            self.env.cr.execute("select count(lot_id) from stock_quant where product_id ="+str(product_id.id) ) 
                            quants_count = self.env.cr.fetchone()
                            if quants_count[0] == 0:
                                if order_ref_prev != line[2] and product_ref_prev != 'CBD' and str(line[2]) != '' and product_ref_prev != str(line[0]):
                                    if str(product_ref_prev) != str(line[2]):
                                        log_message2 = 'Delivery : ' + str(order_ref_prev) + ' - Reference : ' + str(line[2]) + ' - Quantité livrée : ' + str(product_qty)
                                        self._create_common_log_line(job, csvwriter, log_message2) 
                                        self.env.cr.execute("select picking_id from stock_move where reference = '" + str(order_ref_prev)+"'" )
                                        picking_en_cours = self.env.cr.fetchone()
                                        if picking_en_cours:
                                            product_id = self.env['product.product'].search([
                                                ('default_code', '=', str(line[2]))], limit=1)
                                            stock_move_id = self.env['stock.move'].search(
                                                [('product_id', '=', product_id.id),
                                                ('origin', '=', stock_pickng_id.origin)], limit=1)
                                            
                                            self.env.cr.execute("insert into stock_move_line (date, picking_id, product_id, product_uom_id, product_qty, product_uom_qty,qty_done,location_id,location_dest_id,state,reference,company_id) values( '2021-12-16'," + str(picking_en_cours[0]) + " , " + str(product_id.id) + " ,1," + str(product_qty) + " ,"+ str(product_qty) + "," + str(product_qty) + ",47,9,'assigned','" + str(order_ref_prev) + "',1 )")
                                            self.env.cr.execute("update stock_quant set reserved_quantity = reserved_quantity + "+str(product_qty)+ " where product_id="+str(product_id.id) +" and location_id=47")
                                            validate_picking_ids.append(stock_move_id.picking_id)
                                            tracking_no = filename
                                            stock_move_id.picking_id.write(
                                                        {'carrier_tracking_ref': filename}) 

                                        
                                    

                            product_ref_prev = line[2] or ''
                            
        
                tracking_no = filename
            if product_code != '':
                

                for validate_picking_id in list(set(validate_picking_ids)):
                    try:
                        tracking_no = validate_picking_id.carrier_tracking_ref
                        validate_picking_id.action_done()
                        log_message = (_("Delivery validated successfully : " + str(validate_picking_id.name)))
                        self._create_common_log_line(job, csvwriter, log_message,
                                                    validate_picking_id.origin, tracking_no)
                    except:
                        log_message = (_("ERROR : " + str(validate_picking_id.name)))
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
                    attachment = self.env['ir.attachment'].create(vals)
                    job.message_post(body=_("<b>Imported Shipment's Log File</b>"),
                                     attachment_ids=attachment.ids)
                buffer.close()
        #return True
            for pck_assign in lot_traites:
                pck_asset = self.search([('id', '=', pck_assign)])
                pck_asset.action_assign()
        return True


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

