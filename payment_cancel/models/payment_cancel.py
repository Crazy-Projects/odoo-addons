# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.account.models.account_payment import account_payment

class PaymentInvoiceCancel(models.Model):
    _inherit = ['account.payment']
		
    @api.multi
    def unlink(self):
        if any(bool(rec.move_line_ids) for rec in self):
            raise UserError(_("You can not delete a payment that is already posted"))
        return super(account_payment, self).unlink()
