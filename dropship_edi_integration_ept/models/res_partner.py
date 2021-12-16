from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.addons.ftp_connector_ept.models.api import TPWFTPInterface

_intervalTypes = {
    'days': lambda interval: relativedelta(days=interval),
    'hours': lambda interval: relativedelta(hours=interval),
    'weeks': lambda interval: relativedelta(days=7 * interval),
    'months': lambda interval: relativedelta(months=interval),
    'minutes': lambda interval: relativedelta(minutes=interval),
}


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_allow_edi_integrate = fields.Boolean(string="Allow Dropship EDI Integration?",
                                            default=False,
                                            help='When this is ticked Dropship FTP'
                                                 ' Configuration page will be visible.')
    ftp_server_id = fields.Many2one('ftp.server.ept', string="FTP Server")
    csv_delimiter = fields.Char(string="CSV Delimiter", default=",")
    prefix_import_product = fields.Char(string="Prefix For Import Product File",
                                        help='All the files whose name start with this'
                                             ' prefix will be fetched to import product.')
    product_import_directory_id = fields.Many2one('ftp.directory.ept',
                                                  string="Product Import Directory Name",
                                                  domain="[('ftp_server_id','=',ftp_server_id)]")
    product_archive_directory_id = fields.Many2one('ftp.directory.ept',
                                                   string="Product Archive Directory Name",
                                                   domain="[('ftp_server_id','=',ftp_server_id)]")
    search_by_vendor_code = fields.Boolean(string="Search By Vendor Code?",
                                           help="If ticked, it will set the product code into"
                                                " vendor code. Otherwise it will set in product"
                                                " code while you import the products From FTP.")
    auto_create_category = fields.Boolean(string="Allow to Auto Create Product Category if"
                                                 " not found?", default=False,
                                          help='If ticked automatic product category'
                                               ' will be created if not available.')
    # Auto import product scheduler action
    auto_import_product = fields.Boolean(string="Auto Import Product From FTP?", default=False)
    product_import_interval_number = fields.Integer('Product Import Interval Number',
                                                    help="Repeat at every x.")
    product_import_interval_type = fields.Selection([('minutes', 'Minutes'),
                                                     ('hours', 'Hours'), ('days', 'Days'),
                                                     ('weeks', 'Weeks'), ('months', 'Months')],
                                                    'Product Import Interval Unit')
    product_import_next_execution = fields.Datetime('Product Import Next Execution',
                                                    help='Next execution time')
    product_import_user_id = fields.Many2one('res.users', string="Product Import User",
                                             help='User',
                                             default=lambda self: self.env.user)
    # Auto create/update product to catalog scheduler action
    auto_create_product = fields.Boolean(string="Auto Create/Update Product?",
                                         default=False)
    product_creation_interval_number = fields.Integer('Product Creation Interval Number',
                                                      help="Repeat every x.")
    product_creation_interval_type = fields.Selection([('minutes', 'Minutes'),
                                                       ('hours', 'Hours'), ('days', 'Days'),
                                                       ('weeks', 'Weeks'), ('months', 'Months')],
                                                      'Product Creation Interval Unit')
    product_creation_next_execution = fields.Datetime('Product Creation Next Execution',
                                                      help='Next execution time')
    product_creation_user_id = fields.Many2one('res.users', string="Product Creation User",
                                               help='User',
                                               default=lambda self: self.env.user)
    # stock import action
    prefix_import_stock = fields.Char(string="Prefix For Import Stock File")
    stock_import_directory_id = fields.Many2one('ftp.directory.ept',
                                                string="Stock Import Directory Name",
                                                domain="[('ftp_server_id','=',ftp_server_id)]")
    stock_archive_directory_id = fields.Many2one('ftp.directory.ept',
                                                 string="Stock Archive Directory Name",
                                                 domain="[('ftp_server_id','=',ftp_server_id)]")
    # Auto stock import scheduler action
    auto_import_inventory = fields.Boolean(string="Auto Import Inventory Stock?", default=False)
    stock_import_interval_number = fields.Integer('Stock Import Interval Number',
                                                  help="Repeat every x.")
    stock_import_interval_type = fields.Selection([('minutes', 'Minutes'),
                                                   ('hours', 'Hours'), ('days', 'Days'),
                                                   ('weeks', 'Weeks'), ('months', 'Months')],
                                                  'Stock Import Interval Unit')
    stock_import_next_execution = fields.Datetime('Stock Import Next Execution',
                                                  help='Next execution time')
    stock_import_user_id = fields.Many2one('res.users', string="Stock Import User",
                                           help='User',
                                           default=lambda self: self.env.user)
    # shipment import action
    prefix_import_shipment = fields.Char(string="Prefix For Import Shipment File")
    shipment_import_directory_id = fields.Many2one('ftp.directory.ept',
                                                   string="Shipment Import Directory Name",
                                                   domain="[('ftp_server_id','=',ftp_server_id)]")
    shipment_archive_directory_id = fields.Many2one('ftp.directory.ept',
                                                    string="Shipment Archive Directory Name",
                                                    domain="[('ftp_server_id','=',ftp_server_id)]")
    # Auto shipment import scheduler action
    auto_import_shipment = fields.Boolean(string="Auto Import shipment?", default=False)
    shipment_import_interval_number = fields.Integer('Import Shipment Interval Number',
                                                     help="Repeat every x.")
    shipment_import_interval_type = fields.Selection([('minutes', 'Minutes'),
                                                      ('hours', 'Hours'), ('days', 'Days'),
                                                      ('weeks', 'Weeks'), ('months', 'Months')],
                                                     'Import Shipment Interval Unit')
    shipment_import_next_execution = fields.Datetime('Shipment Import Next Execution',
                                                     help='Next execution time')
    shipment_import_user_id = fields.Many2one('res.users', string="Shipment Import User",
                                              help='User',
                                              default=lambda self: self.env.user)
    # shipment export action
    prefix_shipment_export = fields.Char(string="Prefix For Export Shipment File")
    shipment_export_directory_id = fields.Many2one('ftp.directory.ept',
                                                   string="Shipment Export Directory Name",
                                                   domain="[('ftp_server_id','=',ftp_server_id)]")
    # Auto shipment export scheduler action
    auto_export_shipment = fields.Boolean(string="Auto Export Shipment?",
                                          default=False)
    shipment_export_interval_number = fields.Integer('Export Shipment Interval Number',
                                                     help="Repeat every x.")
    shipment_export_interval_type = fields.Selection([('minutes', 'Minutes'),
                                                      ('hours', 'Hours'), ('days', 'Days'),
                                                      ('weeks', 'Weeks'), ('months', 'Months')],
                                                     'Export Shipment Interval Unit')
    shipment_export_next_execution = fields.Datetime('Shipment Export Next Execution',
                                                     help='Next execution time')
    shipment_export_user_id = fields.Many2one('res.users', string="Shipment Export User",
                                              help='User', default=lambda self: self.env.user)

    def get_dropship_edi_interface(self, operation):
        """
        It will send the FTP details to the TPWFTPInterface library and return the connection object.
        :param operation: which operation is performed
        :return: ftp connection object
        """
        host = self.ftp_server_id.ftp_host
        user_name = self.ftp_server_id.ftp_username
        password = self.ftp_server_id.ftp_password
        port = int(self.ftp_server_id.ftp_port)

        if operation == 'product_import':
            dropship_edi_object = TPWFTPInterface(host, user_name, password,
                                                  self.product_import_directory_id.path,
                                                  False, self.product_archive_directory_id.path,
                                                  port)
            return dropship_edi_object
        elif operation == 'stock_import':
            dropship_edi_object = TPWFTPInterface(host, user_name, password,
                                                  self.stock_import_directory_id.path, False,
                                                  self.stock_archive_directory_id.path, port)
            return dropship_edi_object
        elif operation == 'shipment_export':
            dropship_edi_object = TPWFTPInterface(host, user_name, password, False,
                                                  self.shipment_export_directory_id.path,
                                                  False, port)
            return dropship_edi_object
        elif operation == 'shipment_import':
            dropship_edi_object = TPWFTPInterface(host, user_name, password,
                                                  self.shipment_import_directory_id.path,
                                                  False, self.shipment_archive_directory_id.path,
                                                  port)
            return dropship_edi_object

    @api.model_create_multi
    def create(self, vals):
        """
        It will call the cron methods to setup cron.
        :param vals: partner data
        :return: res
        """
        res = super(ResPartner, self).create(vals)
        self.setup_auto_import_product_from_ftp_cron()
        self.setup_auto_create_or_update_product_cron()
        self.setup_auto_import_stock_from_ftp_cron()
        self.setup_auto_export_shipment_orders_cron()
        self.setup_auto_import_shipment_orders_cron()
        return res

    def write(self, vals):
        """
        It will call the cron methods to setup cron.
        :param vals: partner data
        :return: res
        """
        res = super(ResPartner, self).write(vals)
        self.setup_auto_import_product_from_ftp_cron()
        self.setup_auto_create_or_update_product_cron()
        self.setup_auto_import_stock_from_ftp_cron()
        self.setup_auto_export_shipment_orders_cron()
        self.setup_auto_import_shipment_orders_cron()
        return res

    def setup_auto_import_product_from_ftp_cron(self):
        """
        It will setup the automatic import products from FTP cron.
        :return: True
        """
        for product in self:
            if product.auto_import_product:
                try:
                    cron_exist = \
                        self.env.ref(
                            'dropship_edi_integration_ept.ir_cron_dropship_import_products_from_ftp_supplier_%d' %
                            (product.id), raise_if_not_found=False)
                except:
                    cron_exist = False
                nextcall = datetime.now()
                nextcall += \
                    _intervalTypes[product.product_import_interval_type](product.product_import_interval_number)
                vals = {'active': True,
                        'interval_number': product.product_import_interval_number,
                        'interval_type': product.product_import_interval_type,
                        'nextcall': product.product_import_next_execution or
                                    nextcall.strftime('%Y-%m-%d %H:%M:%S'),
                        'code': "model.auto_import_products_from_ftp(ctx={'partner_id':%d})" %
                                (product.id),
                        'user_id': product.product_import_user_id and
                                   product.product_import_user_id.id}
                if cron_exist:
                    vals.update({'name': cron_exist.name})
                    cron_exist.write(vals)
                else:
                    try:
                        import_product_from_ftp_cron = self.env.ref(
                            'dropship_edi_integration_ept.ir_cron_dropship_import_products_from_ftp')
                    except:
                        import_product_from_ftp_cron = False
                    if not import_product_from_ftp_cron:
                        raise Warning(_(
                            'Core settings of Auto Import Products are deleted, Please upgrade'
                            ' Dropshipping EDI Integration module to restore this settings.'))

                    name = product.name + ' : ' + import_product_from_ftp_cron.name
                    vals.update({'name': name})
                    new_cron = import_product_from_ftp_cron.copy(default=vals)
                    self.env['ir.model.data'].create(
                        {'module': 'dropship_edi_integration_ept',
                         'name': 'ir_cron_dropship_import_products_from_ftp_supplier_%d' % (product.id),
                         'model': 'ir.cron',
                         'res_id': new_cron.id,
                         'noupdate': True
                         })
            else:
                try:
                    cron_exist = self.env.ref(
                        'dropship_edi_integration_ept.ir_cron_dropship_import_products_from_ftp_supplier_%d' %
                        (product.id))
                except:
                    cron_exist = False
                if cron_exist:
                    cron_exist.write({'active': False})
        return True

    def setup_auto_create_or_update_product_cron(self):
        """
        It will setup the automatic create or update products from dropship to odoo cron.
        :return: True
        """
        for product in self:
            if product.auto_create_product:
                try:
                    cron_exist = self.env.ref(
                        'dropship_edi_integration_ept.ir_cron_dropship_create_or_update_products_supplier_%d' %
                        (product.id), raise_if_not_found=False)
                except:
                    cron_exist = False
                nextcall = datetime.now()
                nextcall += _intervalTypes[product.product_creation_interval_type] \
                    (product.product_creation_interval_number)
                vals = {'active': True,
                        'interval_number': product.product_creation_interval_number,
                        'interval_type': product.product_creation_interval_type,
                        'nextcall':
                            product.product_creation_next_execution or nextcall.strftime('%Y-%m-%d %H:%M:%S'),
                        'code': "model.auto_create_or_update_products(ctx={'partner_id':%d})" %
                                (product.id),
                        'user_id': product.product_creation_user_id and product.product_creation_user_id.id}
                if cron_exist:
                    vals.update({'name': cron_exist.name})
                    cron_exist.write(vals)
                else:
                    try:
                        create_or_update_product_cron = self.env.ref(
                            'dropship_edi_integration_ept.ir_cron_dropship_create_or_update_products')
                    except:
                        create_or_update_product_cron = False
                    if not create_or_update_product_cron:
                        raise Warning(_(
                            'Core settings of Auto Create or Update Products From Dropship Products'
                            ' are deleted, Please upgrade Dropshipping EDI Integration module'
                            ' to restore this settings.'))
                    name = product.name + ' : ' + create_or_update_product_cron.name
                    vals.update({'name': name})
                    new_cron = create_or_update_product_cron.copy(default=vals)
                    self.env['ir.model.data'].create(
                        {'module': 'dropship_edi_integration_ept',
                         'name': 'ir_cron_dropship_create_or_update_products_supplier_%d' % (product.id),
                         'model': 'ir.cron',
                         'res_id': new_cron.id,
                         'noupdate': True
                         })
            else:
                try:
                    cron_exist = self.env.ref(
                        'dropship_edi_integration_ept.ir_cron_dropship_create_or_update_products_supplier_%d' %
                        (product.id))
                except:
                    cron_exist = False
                if cron_exist:
                    cron_exist.write({'active': False})
        return True

    def setup_auto_import_stock_from_ftp_cron(self):
        """
        It will setup the automatic import stock from FTP cron.
        :return:
        """
        for product in self:
            if product.auto_import_inventory:
                try:
                    cron_exist = \
                        self.env.ref(
                            'dropship_edi_integration_ept.ir_cron_dropship_import_stock_from_ftp_supplier_%d' %
                            (product.id), raise_if_not_found=False)
                except:
                    cron_exist = False
                nextcall = datetime.now()
                nextcall += _intervalTypes[product.stock_import_interval_type]\
                    (product.stock_import_interval_number)
                vals = {'active': True,
                        'interval_number': product.stock_import_interval_number,
                        'interval_type': product.stock_import_interval_type,
                        'nextcall': product.stock_import_next_execution or
                                    nextcall.strftime('%Y-%m-%d %H:%M:%S'),
                        'code': "model.auto_import_stock_from_ftp(ctx={'partner_id':%d})" %
                                (product.id),
                        'user_id': product.stock_import_user_id and product.stock_import_user_id.id}
                if cron_exist:
                    vals.update({'name': cron_exist.name})
                    cron_exist.write(vals)
                else:
                    try:
                        import_stock_from_ftp_cron = self.env.ref(
                            'dropship_edi_integration_ept.ir_cron_dropship_import_stock_from_ftp')
                    except:
                        import_stock_from_ftp_cron = False
                    if not import_stock_from_ftp_cron:
                        raise Warning(_(
                            'Core settings of Auto Import Inventory Stock Information are deleted,'
                            ' Please upgrade Dropshipping EDI Integration module to restore this'
                            ' settings.'))

                    name = product.name + ' : ' + import_stock_from_ftp_cron.name
                    vals.update({'name': name})
                    new_cron = import_stock_from_ftp_cron.copy(default=vals)
                    self.env['ir.model.data'].create(
                        {'module': 'dropship_edi_integration_ept',
                         'name': 'ir_cron_dropship_import_stock_from_ftp_supplier_%d' %
                                 (product.id),
                         'model': 'ir.cron',
                         'res_id': new_cron.id,
                         'noupdate': True
                         })
            else:
                try:
                    cron_exist = \
                        self.env.ref(
                            'dropship_edi_integration_ept.ir_cron_dropship_import_stock_from_ftp_supplier_%d' %
                            (product.id))
                except:
                    cron_exist = False
                if cron_exist:
                    cron_exist.write({'active': False})
        return True

    def setup_auto_export_shipment_orders_cron(self):
        """
        It will setup the automatic export shipment orders to FTP cron.
        :return: True
        """
        for product in self:
            if product.auto_export_shipment:
                try:
                    cron_exist = self.env.ref(
                        'dropship_edi_integration_ept.ir_cron_dropship_export_shipment_orders_to_ftp_supplier_%d'
                        % (product.id), raise_if_not_found=False)
                except:
                    cron_exist = False
                nextcall = datetime.now()
                nextcall += _intervalTypes[product.shipment_export_interval_type]\
                    (product.shipment_export_interval_number)
                vals = {'active': True,
                        'interval_number': product.shipment_export_interval_number,
                        'interval_type': product.shipment_export_interval_type,
                        'nextcall': product.shipment_export_next_execution or
                                    nextcall.strftime('%Y-%m-%d %H:%M:%S'),
                        'code': "model.auto_export_shipment_orders_to_ftp(ctx={'partner_id':%d})" %
                                (product.id),
                        'user_id': product.shipment_export_user_id and product.shipment_export_user_id.id}
                if cron_exist:
                    vals.update({'name': cron_exist.name})
                    cron_exist.write(vals)
                else:
                    try:
                        export_orders_from_ftp_cron = self.env.ref(
                            'dropship_edi_integration_ept.ir_cron_dropship_export_shipment_orders_to_ftp')
                    except:
                        export_orders_from_ftp_cron = False
                    if not export_orders_from_ftp_cron:
                        raise Warning(_(
                            'Core settings of Auto Export Dropship Orders are deleted, please'
                            ' upgrade Dropshipping Connector module to back this settings.'))

                    name = product.name + ' : ' + export_orders_from_ftp_cron.name
                    vals.update({'name': name})
                    new_cron = export_orders_from_ftp_cron.copy(default=vals)
                    self.env['ir.model.data'].create(
                        {'module': 'dropship_edi_integration_ept',
                         'name': 'ir_cron_dropship_export_shipment_orders_to_ftp_supplier_%d' %
                                 (product.id),
                         'model': 'ir.cron',
                         'res_id': new_cron.id,
                         'noupdate': True
                         })
            else:
                try:
                    cron_exist = self.env.ref(
                        'dropship_edi_integration_ept.ir_cron_dropship_export_shipment_orders_to_ftp_supplier_%d' %
                        (product.id))
                except:
                    cron_exist = False
                if cron_exist:
                    cron_exist.write({'active': False})
        return True

    def setup_auto_import_shipment_orders_cron(self):
        """
        It will setup the automatic import shipment orders from FTP cron.
        :return: True
        """
        for product in self:
            if product.auto_import_shipment:
                try:
                    cron_exist = self.env.ref(
                        'dropship_edi_integration_ept.ir_cron_dropship_import_shipment_orders_from_ftp_supplier_%d' %
                        (product.id), raise_if_not_found=False)
                except:
                    cron_exist = False
                nextcall = datetime.now()
                nextcall += _intervalTypes[product.shipment_import_interval_type]\
                    (product.shipment_import_interval_number)
                vals = {'active': True,
                        'interval_number': product.shipment_import_interval_number,
                        'interval_type': product.shipment_import_interval_type,
                        'nextcall': product.shipment_import_next_execution or
                                    nextcall.strftime('%Y-%m-%d %H:%M:%S'),
                        'code': "model.auto_import_shipment_orders_from_ftp(ctx={'partner_id':%d})" %
                                (product.id),
                        'user_id': product.shipment_import_user_id and product.shipment_import_user_id.id}
                if cron_exist:
                    vals.update({'name': cron_exist.name})
                    cron_exist.write(vals)
                else:
                    try:
                        import_shipment_orders_from_ftp_cron = self.env.ref(
                            'dropship_edi_integration_ept.ir_cron_dropship_import_shipment_orders_from_ftp')
                    except:
                        import_shipment_orders_from_ftp_cron = False
                    if not import_shipment_orders_from_ftp_cron:
                        raise Warning(_(
                            'Core settings of Auto Import Shipment Information are deleted,'
                            ' please upgrade Dropshipping Connector module to back this settings.'))

                    name = product.name + ' : ' + import_shipment_orders_from_ftp_cron.name
                    vals.update({'name': name})
                    new_cron = import_shipment_orders_from_ftp_cron.copy(default=vals)
                    self.env['ir.model.data'].create(
                        {'module': 'dropship_edi_integration_ept',
                         'name': 'ir_cron_dropship_import_shipment_orders_from_ftp_supplier_%d' %
                                 (product.id),
                         'model': 'ir.cron',
                         'res_id': new_cron.id,
                         'noupdate': True
                         })
            else:
                try:
                    cron_exist = self.env.ref(
                        'dropship_edi_integration_ept.ir_cron_dropship_import_shipment_orders_from_ftp_supplier_%d' %
                        (product.id))
                except:
                    cron_exist = False
                if cron_exist:
                    cron_exist.write({'active': False})
        return True
