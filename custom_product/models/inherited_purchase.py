from openerp import api, fields, models
from openerp.exceptions import UserError
from datetime import datetime
import openerp.addons.decimal_precision as dp
from openerp import api, fields, models, _, SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    _description = 'Purchase Order Line'
    
    
#     tax_id = fields.Many2one('account.tax',string='Tax')
    income_percentage = fields.Float('Income %')
    sale_price = fields.Float('Sales Price')
    
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        result = {}
        if not self.product_id:
            return result

        # Reset date, price and quantity since _onchange_quantity will provide default values
        self.date_planned = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.price_unit = self.product_id.list_price
        self.income_percentage = self.product_id.income_percentage
        self.sale_price = self.product_id.list_price
        self.product_uom = self.product_id.uom_po_id or self.product_id.uom_id
        result['domain'] = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}

        product_lang = self.product_id.with_context({
            'lang': self.partner_id.lang,
            'partner_id': self.partner_id.id,
        })
        self.name = product_lang.display_name
        if product_lang.description_purchase:
            self.name += '\n' + product_lang.description_purchase

        fpos = self.order_id.fiscal_position_id
        if self.env.uid == SUPERUSER_ID:
            company_id = self.env.user.company_id.id
            self.taxes_id = None
        else:
            self.taxes_id = None
        self.taxes_id = [self.product_id.vat_id.id]

        self._suggest_quantity()
        self._onchange_quantity()
        return result
    
    @api.depends('product_qty', 'price_unit', 'taxes_id','income_percentage')
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
            tax_amt = 0.0;
            for tax_id in line.taxes_id:
                tax_amt += tax_id.amount
            if line.income_percentage and line.taxes_id:
                pp = (line.price_unit*tax_amt/100)+line.price_unit
                income = (pp*line.income_percentage/100)
                line.sale_price = income +pp
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            #product price update
            for tax_id in line.taxes_id:
                line.product_id.write({'vat_id':tax_id.id,'income_percentage':line.income_percentage})
        return True
            
            
            
            
