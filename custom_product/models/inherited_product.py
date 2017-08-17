from openerp import api, fields, models,tools,_
from openerp.exceptions import UserError
import openerp.addons.decimal_precision as dp


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"


    @api.onchange('standard_price','vat_id','actual_amt','income_percentage')
    def onchange_standard_price(self):
        if self.actual_amt and self.vat_id and not self.income_percentage:
            self.list_price = (self.actual_amt * (self.vat_id.amount/100)) + self.actual_amt
            self.vat_amt = self.list_price - self.actual_amt
            self.vat_percentage = self.vat_id.amount
        if self.actual_amt and self.vat_id and self.income_percentage:
            actual_vat_amt = (self.actual_amt * (self.vat_id.amount/100)) + self.actual_amt
            self.vat_amt = actual_vat_amt - self.actual_amt
            self.income_amt = (self.actual_amt + self.vat_amt) * (self.income_percentage/100)
            self.list_price = self.vat_amt + self.actual_amt + self.income_amt
            self.vat_percentage = self.vat_id.amount
        
    @api.onchange('mrp')
    def onchange_mrp(self):
        if self.list_price and self.mrp:
            if not self.mrp >= self.list_price:
                raise UserError(_('Sale price should not be greater then the MRP.'))
        
    is_mrp = fields.Boolean('Is MRP')
    actual_amt = fields.Float('Actual Price')
    vat_id  = fields.Many2one('account.tax', 'VAT')
    vat_percentage = fields.Float('Vat Percentage')
    vat_amt = fields.Float("")
    income_percentage = fields.Float('Income(%)')
    income_amt = fields.Float("")
    mrp = fields.Float('MRP')

    @api.model
    def create(self, vals):
        ''' Store the initial standard price in order to be able to retrieve the cost of a product template for a given date'''
        # TDE FIXME: context brol
        tools.image_resize_images(vals)
        template = super(ProductTemplateInherit, self).create(vals)
        if "create_product_product" not in self._context:
            template.create_variant_ids()

        # This is needed to set given values to first variant after creation
        related_vals = {}
        if vals.get('barcode'):
            related_vals['barcode'] = vals['barcode']
        if vals.get('default_code'):
            related_vals['default_code'] = vals['default_code']
        if vals.get('actual_amt'):
            related_vals['actual_amt'] = vals['actual_amt']
        if vals.get('volume'):
            related_vals['volume'] = vals['volume']
        if vals.get('weight'):
            related_vals['weight'] = vals['weight']
        if related_vals:
            template.write(related_vals)
        if vals.get('list_price') and vals.get('mrp'):
            if not vals.get('mrp') >= vals.get('list_price'):
                raise UserError(_('Sale price should not be greater then the MRP.'))
        return template

    @api.multi
    def write(self, vals):
        tools.image_resize_images(vals)
        res = super(ProductTemplateInherit, self).write(vals)
        if 'attribute_line_ids' in vals or vals.get('active'):
            self.create_variant_ids()
        if 'active' in vals and not vals.get('active'):
            self.with_context(active_test=False).mapped('product_variant_ids').write({'active': vals.get('active')})
        if vals.get('mrp'):
            if vals.get('mrp') == True:
                if not vals.get('mrp') >= self.list_price:
                    raise UserError(_('Sale price should not be greater then the MRP.'))
        if vals.get('list_price'):
            if not self.mrp >= vals.get('list_price'):
                if self.is_mrp == True:
                    raise UserError(_('Sale price should not be greater then the MRP.'))
        if vals.get('list_price') and vals.get('mrp'):
            if not vals.get('mrp') >= vals.get('list_price'):
                raise UserError(_('Sale price should not be greater then the MRP.'))
        if vals.get('is_mrp') and vals.get('mrp'):
            if not vals.get('mrp') >= self.list_price:
                raise UserError(_('Sale price should not be greater then the MRP.'))

        return res