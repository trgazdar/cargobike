# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class ResConfigSettings(models.TransientModel):
	_inherit = 'res.config.settings'
	
	display_stock = fields.Selection([
		('available', 'Quantity on hand'), 
		('outgoing', 'Quantity Available')
		], 'Display Stock',
		help='Display stock by "Qty on Hand" and "Qty Available"', 
		readonly=False)
	stock_message_position = fields.Selection([
		('topleft', 'Top Left'),
		('topright', 'Top Right'),
		('bottomleft', 'Bottom Left'),
		('bottomright', 'Bottom Right')
		], 'Display Stock Message',
		help='Stock availability message based on configuration', 
		readonly=False)

	def set_values(self):
		super(ResConfigSettings, self).set_values()
		self.env['ir.config_parameter'].set_param('webdate_yubabikes.display_stock', self.display_stock)
		self.env['ir.config_parameter'].set_param('webdate_yubabikes.stock_message_position', self.stock_message_position)

	def get_values(self):
		res = super(ResConfigSettings, self).get_values()
		res.update(display_stock = self.env['ir.config_parameter'].sudo().get_param('webdate_yubabikes.display_stock', default='available'))
		res.update(stock_message_position = self.env['ir.config_parameter'].sudo().get_param('webdate_yubabikes.stock_message_position', default='topright'))
		return res
