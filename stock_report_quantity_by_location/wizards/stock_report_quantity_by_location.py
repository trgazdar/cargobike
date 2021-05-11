# Copyright 2019-21 ForgeFlow, S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, fields, models, tools


class StockReportByLocationPrepare(models.TransientModel):
    _name = "stock.report.quantity.by.location.prepare"
    _description = "Stock Report Quantity By Location Prepare"

    location_ids = fields.Many2many(
        comodel_name="stock.location", string="Locations", required=True
    )
    with_quantity = fields.Boolean(
        string="Quantity > 0",
        default=True,
        help="Show only the products that have existing quantity on hand",
    )

    def open(self):
        self.ensure_one()
        self._compute_stock_report_by_location()
        action = {
            "type": "ir.actions.act_window",
            "view_mode": "pivot,tree",
            "name": _("Stock Report by Location"),
            "context": {
                "search_default_quantity_gt_zero": 1,
                "group_by_no_leaf": 1,
                "group_by": [],
            },
            "res_model": "stock.report.quantity.by.location",
            "domain": [("wiz_id", "=", self.id)],
        }
        return action

    def _compute_stock_report_by_location(self):
        self.ensure_one()
        recs = []
        for loc in self.location_ids:
            quant_groups = self.env["stock.quant"].read_group(
                [("location_id", "child_of", [loc.id])],
                ["quantity", "product_id"],
                ["product_id"],
            )
            mapping = {
                quant_group["product_id"][0]: quant_group["quantity"]
                for quant_group in quant_groups
            }
            products = self.env["product.product"].search([("type", "=", "product")])
            vals_list = []
            for product in products:
                quantity = mapping.get(product.id, 0.0)
                if (self.with_quantity and quantity) or not self.with_quantity:
                    vals_list.append(
                        {
                            "product_id": product.id,
                            "product_category_id": product.categ_id.id,
                            "uom_id": product.uom_id.id,
                            "quantity": mapping.get(product.id, 0.0),
                            "location_id": loc.id,
                            "wiz_id": self.id,
                            "default_code": product.default_code,
                        }
                    )
            recs = self.env["stock.report.quantity.by.location"].create(vals_list)
        return recs.ids


class StockReportQuantityByLocation(models.TransientModel):
    _name = "stock.report.quantity.by.location"
    _description = "Stock Report By Location"

    wiz_id = fields.Many2one(comodel_name="stock.report.quantity.by.location.prepare")
    product_id = fields.Many2one(comodel_name="product.product", required=True)
    product_category_id = fields.Many2one(
        comodel_name="product.category", string="Product Category"
    )
    location_id = fields.Many2one(comodel_name="stock.location", required=True)
    quantity = fields.Float()
    uom_id = fields.Many2one(comodel_name="uom.uom", string="Product UoM")
    default_code = fields.Char("Internal Reference")


class ReportStockQuantity(models.Model):
    _inherit = 'report.stock.quantity'
    _auto = False
    _description = 'Stock Quantity Report'

    date = fields.Date(string='Date', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', related='product_id.product_tmpl_id')
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    state = fields.Selection([
        ('forecast', 'Forecasted Stock'),
        ('in', 'Forecasted Receipts'),
        ('out', 'Forecasted Deliveries'),
    ], string='State', readonly=True)
    product_qty = fields.Float(string='Quantity', readonly=True)
    move_ids = fields.One2many('stock.move', readonly=True)
    company_id = fields.Many2one('res.company', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_stock_quantity')
        query = """
CREATE or REPLACE VIEW report_stock_quantity AS (
WITH forecast_qty AS (
    SELECT
        m.id,
        m.product_id,
        CASE
            WHEN (whs.id IS NOT NULL AND whd.id IS NULL) OR ls.usage = 'transit' THEN 'out'
            WHEN (whs.id IS NULL AND whd.id IS NOT NULL) OR ld.usage = 'transit' THEN 'in'
        END AS state,
        m.date_expected::date AS date,
        CASE
            WHEN (whs.id IS NOT NULL AND whd.id IS NULL) OR ls.usage = 'transit' THEN -product_qty
            WHEN (whs.id IS NULL AND whd.id IS NOT NULL) OR ld.usage = 'transit' THEN product_qty
        END AS product_qty,
        m.company_id,
        CASE
            WHEN (whs.id IS NOT NULL AND whd.id IS NULL) OR ls.usage = 'transit' THEN whs.id
            WHEN (whs.id IS NULL AND whd.id IS NOT NULL) OR ld.usage = 'transit' THEN whd.id
        END AS warehouse_id
    FROM
        stock_move m
    LEFT JOIN stock_location ls on (ls.id=m.location_id)
    LEFT JOIN stock_location ld on (ld.id=m.location_dest_id)
    LEFT JOIN stock_warehouse whs ON ls.parent_path like concat('%/', whs.view_location_id, '/%')
    LEFT JOIN stock_warehouse whd ON ld.parent_path like concat('%/', whd.view_location_id, '/%')
    LEFT JOIN product_product pp on pp.id=m.product_id
    LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id
    WHERE
        pt.type = 'product' AND
        product_qty != 0 AND
        (whs.id IS NULL or whd.id IS NULL OR whs.id != whd.id) AND
        m.state NOT IN ('cancel', 'draft', 'done')
    UNION
    SELECT
        -q.id as id,
        q.product_id,
        'forecast' as state,
        date.*::date,
        q.quantity as product_qty,
        q.company_id,
        wh.id as warehouse_id
    FROM
        GENERATE_SERIES((now() at time zone 'utc')::date,
        (now() at time zone 'utc')::date + interval '2 year', '1 day'::interval) date,
        stock_quant q
    LEFT JOIN stock_location l on (l.id=q.location_id)
    LEFT JOIN stock_warehouse wh ON l.parent_path like concat('%/', wh.view_location_id, '/%')
    WHERE
        l.usage = 'internal'
    UNION
    SELECT
        m.id,
        m.product_id,
        'forecast' as state,
        GENERATE_SERIES(
        CASE
            WHEN m.state = 'done' THEN (now() at time zone 'utc')::date
            ELSE m.date_expected::date
        END,
        CASE
            WHEN m.state != 'done' THEN (now() at time zone 'utc')::date + interval '2 year'
            ELSE m.date::date - interval '1 day'
        END, '1 day'::interval)::date date,
        CASE
            WHEN ((whs.id IS NOT NULL AND whd.id IS NULL) OR ls.usage = 'transit') AND m.state = 'done' THEN product_qty
            WHEN ((whs.id IS NULL AND whd.id IS NOT NULL) OR ld.usage = 'transit') AND m.state = 'done' THEN -product_qty
            WHEN (whs.id IS NOT NULL AND whd.id IS NULL) OR ls.usage = 'transit' THEN -product_qty
            WHEN (whs.id IS NULL AND whd.id IS NOT NULL) OR ld.usage = 'transit' THEN product_qty
        END AS product_qty,
        m.company_id,
        CASE
            WHEN (whs.id IS NOT NULL AND whd.id IS NULL) OR ls.usage = 'transit' THEN whs.id
            WHEN (whs.id IS NULL AND whd.id IS NOT NULL) OR ld.usage = 'transit' THEN whd.id
        END AS warehouse_id
    FROM
        stock_move m
    LEFT JOIN stock_location ls on (ls.id=m.location_id)
    LEFT JOIN stock_location ld on (ld.id=m.location_dest_id)
    LEFT JOIN stock_warehouse whs ON ls.parent_path like concat('%/', whs.view_location_id, '/%')
    LEFT JOIN stock_warehouse whd ON ld.parent_path like concat('%/', whd.view_location_id, '/%')
    LEFT JOIN product_product pp on pp.id=m.product_id
    LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id
    WHERE
        pt.type = 'product' AND
        product_qty != 0 AND
        (whs.id IS NULL or whd.id IS NULL OR whs.id != whd.id) AND
        m.state NOT IN ('cancel', 'draft')
)
SELECT
    MIN(id) as id,
    product_id,
    state,
    date,
    sum(product_qty) as product_qty,
    company_id,
    warehouse_id
FROM forecast_qty
GROUP BY product_id, state, date, company_id, warehouse_id
);
"""
        self.env.cr.execute(query)
