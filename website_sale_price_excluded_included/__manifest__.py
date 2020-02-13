# -*- coding: utf-8 -*-
# Copyright 2019 Crazy Projects
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "e-commerce show vat included & excluded price",
    "summary": "This module shows in the product page the price as vat included and vat excluded",
    "version": "11.0.1.0.0",
    "development_status": "Production/Stable",
    "category": "Website",
    "website": "https://www.crazyprojects.es",
    "author": "Crazy Projects, Odoo Community Association (OCA)",
    # see https://odoo-community.org/page/maintainer-role for a description of the maintainer role and responsibilities
    "maintainers": ["crazy-projects"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "base",
        'sale',
        'website_sale',
    ],
    # this feature is only present for 11.0+
    "excludes": [
    ],
    "data": [
        "views/templates.xml",
    ],
    "demo": [
        "demo/assets.xml",
        "demo/res_partner_demo.xml",
    ],
    "qweb": [
    ]
}
