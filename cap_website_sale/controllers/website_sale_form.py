import logging
from odoo.addons.website_sale.controllers.main import WebsiteSale

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class WebsiteSaleForceAuth(WebsiteSale):

    def _get_pricelist_context(self):
        """
            Surcharge de la méthode standard pour exploiter la liste de prix de l'utilisateur si définie
        """
        pricelist_context, pricelist = super()._get_pricelist_context()

        context = dict(request.env.context)
#         if not context.get('pricelist'):
        if request.env.user.partner_id.property_product_pricelist:
            pricelist_context['pricelist'] = request.env.user.partner_id.property_product_pricelist.id

        return pricelist_context, pricelist
