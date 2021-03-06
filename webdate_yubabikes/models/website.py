# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime

class website(models.Model):
	_inherit = "website"

	def getStockSetting(self):
		stock_type = self.env["ir.config_parameter"].sudo().get_param('webdate_yubabikes.display_stock')
		if stock_type:
			return str(stock_type)
		else:
			return str('available')

	def getStockMessagePosition(self):
		stock_message_position = self.env["ir.config_parameter"].sudo().get_param('webdate_yubabikes.stock_message_position')
		if stock_message_position:
			return str(stock_message_position)
		else:
			return str('topright')

	@api.model
	def stockbldate(self, vals):
		tasks_specific = []
		if vals.get("product"):
			product = vals.get("product")
			add_qty = vals.get("add_qty")
			print(product, add_qty)
			query = """WITH forecast_qty AS (
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
										LEFT JOIN stock_warehouse whs ON ls.parent_path like concat('%%/', whs.view_location_id, '/%%')
										LEFT JOIN stock_warehouse whd ON ld.parent_path like concat('%%/', whd.view_location_id, '/%%')
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
											GENERATE_SERIES((now() at time zone 'utc')::date - interval '12month',
											(now() at time zone 'utc')::date + interval '12 month', '1 day'::interval) date,
											stock_quant q
										LEFT JOIN stock_location l on (l.id=q.location_id)
										LEFT JOIN stock_warehouse wh ON l.parent_path like concat('%%/', wh.view_location_id, '/%%')
										WHERE
											l.usage = 'internal'
										UNION
										SELECT
											m.id,
											m.product_id,
											'forecast' as state,
											GENERATE_SERIES(
											CASE
												WHEN m.state = 'done' THEN (now() at time zone 'utc')::date - interval '12month'
												ELSE m.date_expected::date
											END,
											CASE
												WHEN m.state != 'done' THEN (now() at time zone 'utc')::date + interval '12 month'
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
										LEFT JOIN stock_warehouse whs ON ls.parent_path like concat('%%/', whs.view_location_id, '/%%')
										LEFT JOIN stock_warehouse whd ON ld.parent_path like concat('%%/', whd.view_location_id, '/%%')
										LEFT JOIN product_product pp on pp.id=m.product_id
										LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id
										WHERE
											pt.type = 'product' AND
											product_qty != 0 AND
											(whs.id IS NULL or whd.id IS NULL OR whs.id != whd.id) AND
											m.state NOT IN ('cancel', 'draft')
									)
									select product_qty as myqt,CASE WHEN SUM(SIGN(product_qty)) = 0 THEN date ELSE date + 1 END as mdate from (
									SELECT
										date,
										sum(product_qty) as product_qty
									FROM forecast_qty where product_id = %(product)s and state = 'forecast'
									GROUP BY product_id, state, date, company_id, warehouse_id order by date asc)t  where CASE WHEN SIGN(product_qty) > 0 THEN 0 else 1 END > 0 and date >= current_date GROUP BY date, myqt order by mdate desc limit 1"""
			params = {
				'product': product}
			self.env.cr.execute(query, params)

			for myqt, mdate in self.env.cr.fetchall():
				# add an dict to use it as a json object later in javascript
				tasks_specific.append(
					{'myqt': myqt, 'mdate': mdate.strftime("%d-%m-%Y")})
				return tasks_specific