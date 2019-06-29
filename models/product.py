# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, _
from datetime import datetime

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    date_next_coming = fields.Datetime(string='Next Coming', help="Date for next coming.",
        compute='_compute_quantities')

    def _compute_quantities_dict(self):
        
        variants_available = self.mapped('product_variant_ids')._product_available()
        prod_available = {}
        
        for template in self:
            qty_available = 0
            virtual_available = 0
            incoming_qty = 0
            outgoing_qty = 0
            date_next_coming = None

            for p in template.product_variant_ids:
                qty_available += variants_available[p.id]["qty_available"]
                virtual_available += variants_available[p.id]["virtual_available"]
                incoming_qty += variants_available[p.id]["incoming_qty"]
                outgoing_qty += variants_available[p.id]["outgoing_qty"]

                logging.getLogger('product_variant_ids').warning('*' * 80)
                logging.getLogger('p.name').warning(p.name)
                logging.getLogger('p.id').warning(p.id)
                logging.getLogger('incoming_qty').warning(incoming_qty)
                logging.getLogger('outgoing_qty').warning(outgoing_qty)

            if incoming_qty > 0:
                date_next_coming = self._get_date_next_coming(template)

                logging.getLogger('_get_date_next_coming').warning(date_next_coming)
                
            prod_available[template.id] = {
                "qty_available": qty_available,
                "virtual_available": virtual_available,
                "incoming_qty": incoming_qty,
                "outgoing_qty": outgoing_qty,
                "date_next_coming": date_next_coming,
            }


        return prod_available

    def _get_date_next_coming(self, product):
        line = product.env['purchase.order.line'].search(
            [('order_id.state', '=', 'purchase'),
            ('product_id', '=', product.id)],
            order='date_planned asc', limit=1)    

        logging.getLogger(__name__).warning('-' * 80)
        logging.getLogger('product.id').warning(product.id)
        logging.getLogger('line.date_planed').warning(line.date_planned)

        return line.date_planned
