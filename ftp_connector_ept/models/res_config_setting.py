from ast import literal_eval
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ftp_id = fields.Many2one("ftp.server.ept", string="Ftp Server")

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()

        ftp_id = literal_eval(ICPSudo.get_param('ftp_connector_ept.ftp_id', default='False'))

        res.update(ftp_id=ftp_id)
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('ftp_connector_ept.ftp_id', self.ftp_id.id)
