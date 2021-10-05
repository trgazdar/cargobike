# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.http_routing.models.ir_http import slug
from odoo.osv import expression

PPG = 20  # Products Per Page
PPR = 4  # Products Per Row


class WebsiteSaleExt(WebsiteSale):

    @http.route(['/shop/quick_filter_snippet'], type='json', auth='public', website=True)
    def quick_filter_snippet(self, **post):
        values = {}
        if post.get('collection_id') and post.get('collection_id') != 'false':
            collection_data = request.env['filter.collection.configure'].browse(
                int(post.get('collection_id')))
            if collection_data.active:
                if collection_data.parent_based_filter:
                    values.update({
                        'parent_option': 'True'
                    })
                else:
                    values.update({
                        'parent_option': 'False'
                    })
                values.update({
                    'value': request.env.ref("quick_filter.filter_collection_configure")._render({'obj': collection_data})
                })
            else:
                values.update({
                    'disable_group': 'True'
                })
        return values

    def _get_search_domain(self, search, category, attrib_values, search_in_description=True):
        domains = super(WebsiteSaleExt, self)._get_search_domain(
            search=search, category=category, attrib_values=attrib_values)
        if request.params.get('filter'):
            filters = None
            ids = []
            filter_list = request.httprequest.args.getlist('filter')
            filter_values = [[int(x) for x in v.split("-")]
                             for v in filter_list if v]
            for value in filter_values:
                if not filters:
                    filters = value[0]
                    ids.append(value[1])
                elif value[0] == filters:
                    ids.append(value[1])
                else:
                    domains = expression.AND(
                        [[('filter_line_ids.filter_value_ids', 'in', ids)], domains])
                    filters = value[0]
                    ids = [value[1]]
            if filters:
                domains = expression.AND(
                    [[('filter_line_ids.filter_value_ids', 'in', ids)], domains])
        return domains

    @http.route()
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        res = super(WebsiteSaleExt, self).shop(
            page=page, category=category, search=search, ppg=ppg, **post)
        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")]
                         for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        filter_list = request.httprequest.args.getlist('filter')
        filter_values = [[int(x) for x in v.split("-")]
                         for v in filter_list if v]
        filters_ids = {v[0] for v in filter_values}
        filter_set = {v[1] for v in filter_values}

        if filter_list:
            post['filter'] = filter_list
            domain = self._get_search_domain(
                search=search, category=category, attrib_values=attrib_values)
            keep = QueryURL('/shop', category=category and int(category),
                            search=search, filter=filter_list, order=post.get('order'))

            url = "/shop"
            if search:
                post["search"] = search
            if category:
                category = request.env['product.public.category'].browse(
                    int(category))
                url = "/shop/category/%s" % slug(category)

            Product = request.env[
                'product.template'].with_context(bin_size=True)

            search_product = Product.search(domain)

            product_count = len(search_product)
            pager = request.website.pager(
                url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
            products = Product.search(
                domain, order=self._get_search_order(post))

            ProductFilter = request.env['quick.filter']
            if products:
                filters = ProductFilter.search(
                    [('filter_value_ids.product_tmpl_id', 'in', products.ids)])
            else:
                filters = ProductFilter.browse(filters_ids)

            values = {
                'bins': TableCompute().process(products, ppg),
                'search': search,
                'pager': pager,
                'search_count': product_count,
                'products': products,
                'keep': keep,
            }
            res.qcontext.update(values)
        return res
