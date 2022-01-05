from odoo import api, fields, models


class CapProductTemplate(models.Model):
    _inherit = "product.template"

    invoice_policy = fields.Selection([
        ('order', 'Ordered quantities'),
        ('delivery', 'Delivered quantities')], string='Invoicing Policy',
        company_dependent=True,
        help='Ordered Quantity: Invoice quantities ordered by the customer.\n'
             'Delivered Quantity: Invoice quantities delivered to the customer.',
        default='order')

    expense_policy = fields.Selection(
        [('no', 'No'), ('cost', 'At cost'), ('sales_price', 'Sales price')],
        string='Re-Invoice Expenses',
        default='no',
        company_dependent=True,
        help="Expenses and vendor bills can be re-invoiced to a customer."
             "With this option, a validated expense can be re-invoice to a customer at its cost or sales price.")
