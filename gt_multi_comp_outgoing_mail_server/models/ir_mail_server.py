###############################################################################
#                                                                             #
#    Globalteckz                                                              #
#    Copyright (C) 2013-Today Globalteckz (http://www.globalteckz.com)        #
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU Affero General Public License as           #
#    published by the Free Software Foundation, either version 3 of the       #
#    License, or (at your option) any later version.                          #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU Affero General Public License for more details.                      #
#                                                                             #
#    You should have received a copy of the GNU Affero General Public License #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
#                                                                             #
###############################################################################


from odoo import fields,models, api

class Ir_Mail_Server(models.Model):
    _inherit = 'ir.mail_server'
    
    
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.user.company_id)
   
class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'
    
    # @api.multi
    def get_mail_values(self, res_ids):
        res=super(MailComposer,self).get_mail_values(res_ids)
        for value in res.values():
            mail_server = self.env['ir.mail_server'].sudo().search([('company_id','=',self.env.user.company_id.id)],limit=1)
            if mail_server:
                value.update({'mail_server_id':mail_server.id})
            if not mail_server:
                mail_server = self.env['ir.mail_server'].sudo().search([('company_id','=',False)],limit=1)
                value.update({'mail_server_id':mail_server.id})

        return res