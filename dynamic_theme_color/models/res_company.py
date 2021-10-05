# -*- coding: utf-8 -*-
import base64

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    community_color = fields.Char()
    enterprise_color = fields.Char()
    background_color = fields.Char()
    text_color = fields.Char()
    line_high = fields.Float()
    font_size = fields.Float()

    @api.model
    def create(self, values):
        res = super().create(values)
        if 'community_color' in values or 'enterprise_color' in values or 'line_high' in values or 'font_size' in values or 'background_color' in values or 'text_color' in values:
            self._update_asset_them_style()
        return res

    def write(self, values):
        res = super().write(values)
        if 'community_color' in values or 'enterprise_color' in values or 'line_high' in values or 'font_size' in values or 'background_color' in values or 'text_color' in values:
            self._update_asset_them_style()
        return res

    def _get_asset_theme_style_b64(self):
        template_style = self.env.ref('dynamic_theme_color.styles_company_theme', raise_if_not_found=False)
        if not template_style:
            return ''
        # One bundle for everyone, so this method
        # necessarily updates the style for every company at once
        company_ids = self.sudo().search([])
        company_styles = template_style.render({
            'company_ids': company_ids,
        })
        return base64.b64encode((company_styles))

    def _update_asset_them_style(self):
        asset_attachment = self.env.ref('dynamic_theme_color.asset_styles_company_theme_color', raise_if_not_found=False)
        if not asset_attachment:
            return
        asset_attachment = asset_attachment.sudo()
        b64_val = self._get_asset_theme_style_b64()
        if b64_val != asset_attachment.datas:
            asset_attachment.write({'datas': b64_val})
