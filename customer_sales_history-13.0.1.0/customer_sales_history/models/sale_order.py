# -*- encoding: utf-8 -*-
##############################################################################
#
# Craftsync Technologies
# Copyright (C) 2020(https://www.craftsync.com)
#
##############################################################################

from odoo import models, fields


class Sale_Order(models.Model):
    _inherit = "sale.order"

    sale_product_count = fields.Integer(
        compute='_compute_sale_product_count', string='Order',
        help="Count of total sales")

    def _compute_sale_product_count(self):
        '''
        Method to calculate total count customer has purchase product.
        '''
        if self.partner_id:
            all_partners = self.env['res.partner'].search(
                [('id', 'child_of', self.partner_id.id)]).ids
            if not self.partner_id.id in all_partners:
                all_partners.append(self.partner_id.id)
            lines_count = self.env['sale.order.line'].search_count(
                [('order_partner_id', 'in', all_partners),('product_id', '!=', False)])
            self.sale_product_count = lines_count
        else:
            self.sale_product_count = 0.0

    def action_view_history_orders(self):
        '''
        Method to return action to view selected partner total sale order
        lines.
        '''
        all_partners = self.env['res.partner'].search(
            [('id', 'child_of', self.partner_id.id)]).ids
        if not self.partner_id.id in all_partners:
            all_partners.append(self.partner_id.id)
        action = self.env.ref(
            'customer_sales_history.view_product_list').read()[0]
        action['context'] = {'group_by': ['product_id']}
        action['domain'] = [('product_id', '!=', False),
                            ('order_partner_id', 'in', all_partners)]
        return action
