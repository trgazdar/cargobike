# -*- coding: utf-8 -*-
"""This module is to quickly find the products"""

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class QuickFinder(models.Model):
    _name = "quick.filter"
    _description = "Product Filter"
    _order = 'sequence, name'

    name = fields.Char("Filter", required=True, translate=True)
    sequence = fields.Integer(
        'Sequence', help="Determine the display order", default=10)
    parent_id = fields.Many2one(
        'quick.filter', string='Parent', index=True, ondelete='restrict')
    child_id = fields.One2many('quick.filter', 'parent_id',
                               string='Children Filter', ondelete='restrict', translate=True)
    category_ids = fields.One2many("quick.filter.values", "parent_id",
                                   string="Filter Values", ondelete='restrict', translate=True)
    filter_value_ids = fields.One2many("product.quick.filter.line", "filter_id",
                                       string="Filter Lines Values", ondelete='restrict', translate=True)

    filter_line_ids = fields.One2many(
        'product.quick.filter.line', 'filter_id', 'Lines')

    product_id = fields.Many2many(
        "product.template", compute='_compute_add_products', store=True)

    @api.depends('filter_line_ids.product_tmpl_id')
    def _compute_add_products(self):
        for pa in self:
            pa.product_id = pa.filter_line_ids.product_tmpl_id


class QuickFinderValues(models.Model):
    _name = "quick.filter.values"
    _order = 'sequence, parent_id, id'

    name = fields.Char("Name", required=True, translate=True)
    sequence = fields.Integer(
        'Sequence', help="Determine the display order")
    parent_id = fields.Many2one(
        "quick.filter", 'Filter', ondelete='restrict', required=True)

    is_super_parent_filter = fields.Boolean(
        'Assign Parent', default=False)
    super_parent_id_name = fields.Char('Parent Filter Name', translate=True)

    super_parent_id = fields.Many2one(
        'quick.filter.values', string='Values', index=True, ondelete='restrict')
    filter_value_ids = fields.One2many('quick.filter.values', 'super_parent_id',
                                       string='Parent Filter Values', ondelete='restrict', translate=True)

    super_parent_ids = fields.Many2many('quick.filter.values', 'super_parent_id_values', 'parent_id',
                                        'filter_value_ids', string='Parent Filter Values', ondelete='restrict', translate=True)

    _sql_constraints = [
        ('value_filter_uniq', 'unique(name,parent_id)',
         'This filter value already exists !')
    ]

    @api.onchange('parent_id', 'is_super_parent_filter')
    def onchage_attribute(self):
        if self.parent_id.parent_id:
            if self.is_super_parent_filter == True:
                self.super_parent_id_name = self.parent_id.parent_id.name
            else:
                self.super_parent_id_name = ''
        else:
            return None

    @api.constrains('is_super_parent_filter', 'super_parent_id_name', 'super_parent_ids')
    def check_parent_values(self):
        for rec in self:
            if rec.is_super_parent_filter:
                if not rec.super_parent_id_name:
                    raise ValidationError(
                        _('Please enter a Parent filter Name.'))
                if not rec.super_parent_ids:
                    raise ValidationError(
                        _('Please Select a Parent Filter Values.'))


class ProductQuickFilterLine(models.Model):
    _name = "product.quick.filter.line"

    sequence = fields.Integer(
        'Sequence', help="Determine the display order")
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product Template', required=True)
    filter_id = fields.Many2one(
        'quick.filter', 'Filter Name')
    filter_value_ids = fields.Many2many(
        'quick.filter.values', string='Filter Values', translate=True)


class ProductDisplay(models.Model):
    _inherit = 'product.template'

    filter_line_ids = fields.One2many(
        "product.quick.filter.line", 'product_tmpl_id', translate=True)


class Collection_configure(models.Model):
    _name = 'filter.collection.configure'
    _description = 'Group collections'

    name = fields.Char("Title", translate=True)
    group_collection_ids = fields.Many2many(
        'quick.filter', string="Select Collection", translate=True)
    parent_based_filter = fields.Boolean(
        'Parent Based Filter', default=False)
    active = fields.Boolean("Active", default=True,
        tracking=True, help="If the active field is set to false, it will hide the group without removing it.")

    @api.onchange('active')
    def _check_disable_active(self):
        if not self.active:
            return {
                'warning': {'title': "Warning", 'message': "If Filter Group is In-active, Filters will not show On Website..!."},
            }
