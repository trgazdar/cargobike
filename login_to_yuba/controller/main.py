from odoo import fields, http, tools, models,_
from odoo.http import request


class Website(http.Controller):

	@http.route('/accessrestrict', type='http', auth="public", website=True)
	def restrcit_access(self):

		return request.render("login_to_yuba.accessrestrict",{})
