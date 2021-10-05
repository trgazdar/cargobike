# -*- encoding: utf-8 -*-
##############################################################################
#
# Craftsync Technologies
# Copyright (C) 2020(https://www.craftsync.com)
#
##############################################################################

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_product_count = fields.Integer(
        compute='_compute_sale_product_count', help="Count of total sales")
    sale_product_ids = fields.One2many('sale.order.line', 'order_partner_id',
                                       string='Shopped Products', copy=False)

    def _compute_sale_product_count(self):
        '''
        Method to calculate partner and child partners total purchase count.
        '''
        all_partners = self.search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])

        sale_order_groups = self.env['sale.order.line'].read_group(
            domain=[('order_partner_id', 'in', all_partners.ids)],
            fields=['order_partner_id'], groupby=['order_partner_id']
        )
        partners = self.browse()
        for group in sale_order_groups:
            partner = self.browse(group['order_partner_id'][0])
            while partner:
                if partner in self:
                    partner.sale_product_count += group['order_partner_id_count']
                    partners |= partner
                partner = partner.parent_id
        (self - partners).sale_product_count = 0
