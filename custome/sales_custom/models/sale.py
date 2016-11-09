# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('pending_confirmation','Pending Confirmation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
    
    @api.multi
    def action_pending_confirmation(self):
        print self
        self.write({'state': 'sale'})
        return True
        
        