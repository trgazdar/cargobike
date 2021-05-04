#!/usr/bin/python3
from odoo import models, fields, _
from .sftp_interface import sftp_interface
from .api import TPWFTPInterface
from odoo.exceptions import Warning, ValidationError, UserError
import ftplib
import paramiko


class FtpServerEpt(models.Model):
    _name = "ftp.server.ept"
    _description = "Ftp Server Details"

    name = fields.Char("Server name", required=True)
    ftp_host = fields.Char("Host", required=True)
    ftp_username = fields.Char("User Name", required=True)
    ftp_password = fields.Char("Password")
    ftp_port = fields.Char("Port", required=True)
    is_passive_mode = fields.Boolean("Passive Mode", default=True)
    directory_ids = fields.One2many("ftp.directory.ept", 'ftp_server_id', string="Directory list")
    conn_type = fields.Selection([('ftp', 'FTP'), ('sftp', 'SFTP')], string="Connection Type",
                                 default='sftp', )
    server_type = fields.Selection([('production', 'Production'), ('sandbox', 'Sandbox')],
                                   string="Server Connection Type", default='sandbox')
    key_filename = fields.Char("SSH Key path")
    is_production_environment = fields.Boolean()

    _sql_constraints = [
        ('ftp_unique_ept', 'UNIQUE (name,ftp_host,ftp_username,ftp_password,ftp_port)',
         'The Server must be unique!'), ]

    def toggle_prod_environment_value(self):
        """
        This will switch environment between production and pre-production.
        @return : True
        @author: Keyur Kanani
        """
        self.ensure_one()
        self.is_production_environment = not self.is_production_environment
        if self.is_production_environment:
            self.server_type = 'production'
        else:
            self.server_type = 'sandbox'

    def do_test(self):
        """
        author: bhavesh jadav 27/4/2019
        func: this method use for test connection only of FTP and SFTP
        :return:
        """
        conn_type = self.conn_type
        ftp_host = self.ftp_host
        ftp_port = int(self.ftp_port)
        ftp_username = self.ftp_username
        ftp_password = self.ftp_password
        key_filename = self.key_filename
        if conn_type == "ftp":
            try:
                with TPWFTPInterface(host=ftp_host, user=ftp_username, passwd=ftp_password,
                                     port=ftp_port, from_tpw_dir=False, to_tpw_dir=False):
                    title = _("FTP Connection Test Succeeded!")
                    message = _("Everything seems properly set up!")
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': title,
                            'message': message,
                            'sticky': False,
                        }
                    }
            except Exception as e:
                raise UserError(_("Connection Test Failed! Here is what we got instead:\n %s") % (e))
        elif conn_type == "sftp":
            try:
                with sftp_interface(host=ftp_host, user=ftp_username, passwd=ftp_password, key_filename=key_filename,
                                    port=ftp_port, upload_dir=False):
                    title = _("SFTP Connection Test Succeeded!")
                    message = _("Everything seems properly set up!")
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'title': title,
                            'message': message,
                            'sticky': False,
                        }
                    }
            except Exception as e:
                raise UserError(_("Connection Test Failed! Here is what we got instead:\n %s") % (e))
        else:
            raise Warning("Please set proper connection type.")

    def do_test_connection(self):
        """
        author: bhavesh jadav 15/4/2019
        func: this method use for test connection of FTP and SFTP
        :return:NULL
        """
        global sending, receive, archive
        conn_type = self.conn_type
        ftp_host = self.ftp_host
        ftp_port = int(self.ftp_port)
        ftp_username = self.ftp_username
        ftp_password = self.ftp_password
        key_filename = self.key_filename
        if conn_type == "ftp":
            try:
                if not self.directory_ids:
                    raise Warning("Please add FTP directories")
                for directory in self.directory_ids:
                    sending = TPWFTPInterface(
                        host=ftp_host,
                        user=ftp_username,
                        passwd=ftp_password,
                        from_tpw_dir=directory.path,
                        to_tpw_dir=directory.path,
                        port=ftp_port
                    )

                    receive = TPWFTPInterface(
                        host=ftp_host,
                        user=ftp_username,
                        passwd=ftp_password,
                        to_tpw_dir=directory.path,
                        from_tpw_dir=directory.path,
                        port=ftp_port
                    )

                    archive = TPWFTPInterface(
                        host=ftp_host,
                        user=ftp_username,
                        passwd=ftp_password,
                        archive_dir=directory.path,
                        to_tpw_dir=directory.path,
                        from_tpw_dir=directory.path,
                        port=ftp_port
                    )

                if sending or receive or archive:
                    raise Warning("Working properly")
                else:
                    raise Warning("Not working")
            except Exception as e:
                raise Warning("%s" % e)
        elif conn_type == "sftp":
            try:
                if not self.directory_ids:
                    raise Warning("Please add FTP directories")
                for directory in self.directory_ids:
                    sending = sftp_interface(
                        host=ftp_host,
                        user=ftp_username,
                        passwd=ftp_password,
                        key_filename=key_filename,
                        port=int(ftp_port),
                        upload_dir=str(directory.path)
                    )
                    receive = sftp_interface(
                        host=ftp_host,
                        user=ftp_username,
                        passwd=ftp_password,
                        key_filename=key_filename,
                        port=ftp_port,
                        download_dir=str(directory.path)
                    )
                    archive = sftp_interface(
                        host=ftp_host,
                        user=ftp_username,
                        passwd=ftp_password,
                        key_filename=key_filename,
                        port=ftp_port,
                        archive_dir=str(directory.path)
                    )
                if sending or receive or archive:
                    raise Warning("Working properly")
                else:
                    raise Warning("Oops.. Not working")
            except Exception as e:
                raise Warning("%s" % e)

    def add_directory(self):
        """
        This method set all directory list in FTP instance.
        :return: Set directory list in FTP instance
        """
        if self.do_test():
            if self.conn_type == 'ftp':
                FTP = ftplib.FTP(self.ftp_host, self.ftp_username, self.ftp_password)
                ls = FTP.nlst()
                for dir in ls:
                    if not dir.__contains__('.'):
                        self.directory_ids.create({
                            'ftp_server_id': self.id,
                            'name': dir,
                            'path': "/" + dir
                        })
            elif self.conn_type == 'sftp':
                with sftp_interface(host=self.ftp_host, user=self.ftp_username, passwd=self.ftp_password, key_filename=self.key_filename,
                                    port=self.ftp_port, upload_dir=False) as ssh:
                    for dir in ssh.sftp_client.listdir():
                        lstatout = str(ssh.sftp_client.lstat(dir)).split()[0]
                        if 'd' in lstatout:
                            self.directory_ids.create({
                                'ftp_server_id': self.id,
                                'name': dir,
                                'path': "/" + dir
                            })
        return True


class FtpDirectoryEpt(models.Model):
    _name = "ftp.directory.ept"
    _description = "Ftp Directories Ddetails"

    ftp_server_id = fields.Many2one("ftp.server.ept", string="Ftp Server")
    name = fields.Char("Name", required=True)
    path = fields.Char("Path", required=True)

    _sql_constraints = [('directory_unique', 'UNIQUE (name,ftp_server_id)', 'The Directory must be unique!'), ]
