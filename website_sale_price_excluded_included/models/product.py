# -*- coding: utf-8 -*-
# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp

from odoo.tools import pycompat
from odoo.tools import float_compare


class ProductTemplate(models.Model):
    _inherit = "product.template"
    _name = 'product.template'

    # Tax inclusive prices
    website_price_included = fields.Float('Website price', compute='_website_price_tax',
                                          digits=dp.get_precision('Product Price'))
    website_public_price_included = fields.Float('Website public price', compute='_website_price_tax',
                                                 digits=dp.get_precision('Product Price'))
    website_price_difference_included = fields.Boolean('Website price difference', compute='_website_price_tax')

    # Tax exclusive prices
    website_price_excluded = fields.Float('Website price', compute='_website_price_tax',
                                          digits=dp.get_precision('Product Price'))
    website_public_price_excluded = fields.Float('Website public price', compute='_website_price_tax',
                                                 digits=dp.get_precision('Product Price'))
    website_price_difference_excluded = fields.Boolean('Website price difference', compute='_website_price_tax')

    def _website_price_tax(self):
        # First filter out the ones that have no variant:
        # This makes sure that every template below has a corresponding product in the zipped result.
        self = self.filtered('product_variant_id')
        # use mapped who returns a recordset with only itself to prefetch (and don't prefetch every product_variant_ids)
        for template, product in pycompat.izip(self, self.mapped('product_variant_id')):
            # tax inclusive
            template.website_price_included = product.website_price_included
            template.website_public_price_included = product.website_public_price_included
            template.website_price_difference_included = product.website_price_difference_included

            # tax exinclusive
            template.website_price_excluded = product.website_price_excluded
            template.website_public_price_excluded = product.website_public_price_excluded
            template.website_price_difference_excluded = product.website_price_difference_excluded


class Product(models.Model):
    _inherit = "product.product"

    # tax inclusive prices
    website_price_included = fields.Float('Website price', compute='_website_price_tax',
                                          digits=dp.get_precision('Product Price'))
    website_public_price_included = fields.Float('Website public price', compute='_website_price_tax',
                                                 digits=dp.get_precision('Product Price'))
    website_price_difference_included = fields.Boolean('Website price difference', compute='_website_price_tax')

    # tax exclusive prices
    website_price_excluded = fields.Float('Website price', compute='_website_price_tax',
                                          digits=dp.get_precision('Product Price'))
    website_public_price_excluded = fields.Float('Website public price', compute='_website_price_tax',
                                                 digits=dp.get_precision('Product Price'))
    website_price_difference_excluded = fields.Boolean('Website price difference', compute='_website_price_tax')

    def _website_price_tax(self):
        qty = self._context.get('quantity', 1.0)
        partner = self.env.user.partner_id
        current_website = self.env['website'].get_current_website()
        pricelist = current_website.get_current_pricelist()
        company_id = current_website.company_id

        context = dict(self._context, pricelist=pricelist.id, partner=partner)
        self2 = self.with_context(context) if self._context != context else self

        for p, p2 in pycompat.izip(self, self2):
            taxes = partner.property_account_position_id.map_tax(p.sudo().taxes_id.filtered(lambda x: x.company_id == company_id))

            p.website_price_included = taxes.compute_all(p2.price, pricelist.currency_id, quantity=qty, product=p2, partner=partner)['total_included']
            p.website_price_excluded = taxes.compute_all(p2.price, pricelist.currency_id, quantity = qty,product = p2, partner = partner)['total_excluded']
            # We must convert the price_without_pricelist in the same currency than the
            # website_price, otherwise the comparison doesn't make sense. Moreover, we show a price
            # difference only if the website price is lower
            price_without_pricelist = p.list_price
            if company_id.currency_id != pricelist.currency_id:
                price_without_pricelist = company_id.currency_id.compute(price_without_pricelist, pricelist.currency_id)
            price_without_pricelist_included = taxes.compute_all(price_without_pricelist, pricelist.currency_id)['total_included']
            price_without_pricelist_excluded = taxes.compute_all(price_without_pricelist, pricelist.currency_id)['total_excluded']

            # inclusive pricing
            p.website_price_difference_included = True if float_compare(price_without_pricelist_included,
                                                                        p.website_price_included, precision_rounding=pricelist.currency_id.rounding) > 0 else False
            p.website_public_price_included = taxes.compute_all(p2.lst_price, quantity=qty, product=p2, partner=partner)['total_included']

            # exclusive pricing
            p.website_price_difference_excluded = True if float_compare(price_without_pricelist_excluded,
                                                                        p.website_price_excluded, precision_rounding=pricelist.currency_id.rounding) > 0 else False
            p.website_public_price_excluded = taxes.compute_all(p2.lst_price, quantity=qty, product=p2, partner=partner)['total_excluded']
            print(price_without_pricelist_included)
            print(price_without_pricelist_excluded)

    # Overwite the original method so it shows vat inclusive prices, regardless of the config
    def _website_price(self):
        qty = self._context.get('quantity', 1.0)
        partner = self.env.user.partner_id
        current_website = self.env['website'].get_current_website()
        pricelist = current_website.get_current_pricelist()
        company_id = current_website.company_id

        context = dict(self._context, pricelist=pricelist.id, partner=partner)
        self2 = self.with_context(context) if self._context != context else self

        ret = 'total_included'

        for p, p2 in pycompat.izip(self, self2):
            taxes = partner.property_account_position_id.map_tax(p.sudo().taxes_id.filtered(lambda x: x.company_id == company_id))
            p.website_price = taxes.compute_all(p2.price, pricelist.currency_id, quantity=qty, product=p2, partner=partner)[ret]
            # We must convert the price_without_pricelist in the same currency than the
            # website_price, otherwise the comparison doesn't make sense. Moreover, we show a price
            # difference only if the website price is lower
            price_without_pricelist = p.list_price
            if company_id.currency_id != pricelist.currency_id:
                price_without_pricelist = company_id.currency_id.compute(price_without_pricelist, pricelist.currency_id)
            price_without_pricelist = taxes.compute_all(price_without_pricelist, pricelist.currency_id)[ret]
            p.website_price_difference = True if float_compare(price_without_pricelist, p.website_price, precision_rounding=pricelist.currency_id.rounding) > 0 else False
            p.website_public_price = taxes.compute_all(p2.lst_price, quantity=qty, product=p2, partner=partner)[ret]
