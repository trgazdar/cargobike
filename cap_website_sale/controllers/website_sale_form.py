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
        _logger.info("We are in _get_pricelist_context")
        pricelist_context, pricelist = super()._get_pricelist_context()

        context = dict(request.env.context)
        if not context.get('pricelist'):
            if request.env.user.partner_id.property_product_pricelist:
                _logger.info("We are in the IF")
                pricelist_context['pricelist'] = request.env.user.partner_id.property_product_pricelist.id
                _logger.info("La pricelist du partner est %s :" % pricelist_context['pricelist'])
                _logger.info("La pricelist du partner actuel est : %s " % self.env['res.partner'].search([('id', '=', '1')]).property_product_pricelist

        return pricelist_context, pricelist
