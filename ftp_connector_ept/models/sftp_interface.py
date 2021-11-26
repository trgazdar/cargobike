from odoo import models, fields, api, _
from odoo.osv import expression, osv
import paramiko
from tempfile import NamedTemporaryFile
import os


class sftp_interface(object):
    client = None

    def __init__(self, host, user, passwd, key_filename, port, upload_dir='', download_dir='', archive_dir='', ):
        self.host = host
        self.user = user
        self.passwd =  passwd or None
        self.port = int(port)
        self.upload_dir = upload_dir
        self.download_dir = download_dir
        self.archive_dir = archive_dir
        self.key_filename = key_filename or None
        self.ssh = paramiko.SSHClient()
        self.__enter__()

    def __enter__(self):
        """
        author:bhavesh jadav 14/4/2019
        func: this method use for establish  connection
        :return: self
        """
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(hostname=self.host, port=self.port or 2222, username=self.user, password=self.passwd, key_filename=self.key_filename)
        except Exception as e:
            raise osv.except_osv(_('connection error'), _('%s' % e))
        self.sftp_client = self.ssh.open_sftp()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        author:bhavesh jadav 14/4/2019
        func: this method use for break connection
        """
        self.sftp_client.close()
        self.ssh.close()

    def push_to_ftp(self, filename, local_file):
        """
        Uploads the given file in a binary transfer mode to the `upload_dir`
        :param filename: filename of the created file
        :param file: Path to the file name of the local file
        """
        try:
            # assert isinstance(local_file, basestring), "Local file must be a filename"
            self.sftp_client.chdir(self.upload_dir)
            self.sftp_client.put(local_file, filename, confirm=False)
        except Exception as e:
            raise osv.except_osv(_('Amazon Error'), _('%s' % (e) + ' or  Invalid directory name. '))

    def pull_from_ftp(self, pattern):
        """
        Pulls all the available files from the FTP location and imports them
        :param pattern: Filename Pattern to match, e.g., `Cdeclient`
        :return: Filenames of files to export
        """

        self.sftp_client.chdir(self.download_dir)

        # Match the pattern in each filename in the directory and filter
        matched_files = [f for f in self.sftp_client.listdir() if pattern in f]
        files_to_export = {}
        for file_to_import in matched_files:
            file = NamedTemporaryFile(delete=False)
            file.close()
            self.sftp_client.get(file_to_import, file.name)
            files_to_export.update({file_to_import: file.name})
            return files_to_export


           
    def delete_from_tmp(self, filenames):
        """
        author:bhavesh jadav 15/4/2019
        func: this method use from delete  temp
        :param filenames:
        :return:
        """
        for filename in filenames:
            os.remove(filename)
        return True

    def delete_from_ftp(self, filenames):
        """
        author:bhavesh jadav 15/4/2019
        func: this method use from delete from remote dictionary
        :param filenames:use for files name
        :return: TRUE
        """
        for filename in filenames:
            # self.sftp_client.chdir(self.download_dir)
            self.sftp_client.remove(filename)
        return True

    def archive_file(self, filenames):
        for filename in filenames:
            fromname = "%s/%s" % (self.download_dir, filename)
            toname = "%s/%s" % (self.archive_dir, filename)
            self.sftp_client.chdir(self.archive_dir)
            self.sftp_client.rename(fromname, toname)
        return True
