from openerp import api, fields, models,tools,_
from openerp.exceptions import UserError
import openerp.addons.decimal_precision as dp


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    @api.one
    def _set_standard_price(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.standard_price = self.standard_price

    @api.depends('product_variant_ids', 'product_variant_ids.standard_price')
    def _compute_standard_price(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.standard_price = template.product_variant_ids.standard_price
        for template in (self - unique_variants):
            template.standard_price = 0.0

    @api.onchange('standard_price','vat_id','income_percentage')
    def onchange_standard_price(self):
        if self.standard_price and self.vat_id and not self.income_percentage:
            self.list_price = (self.standard_price * (self.vat_id.amount/100)) + self.standard_price
            self.vat_amt = self.list_price - self.standard_price
        if self.standard_price and self.vat_id and self.income_percentage:
            actual_vat_amt = (self.standard_price * (self.vat_id.amount/100)) + self.standard_price
            self.vat_amt = actual_vat_amt - self.standard_price
            self.income_amt = (self.standard_price + self.vat_amt) * (self.income_percentage/100)
            self.list_price = self.vat_amt + self.standard_price + self.income_amt
            
#             self.list_price = (self.list_price * ((self.vat_id.amount + self.income_percentage)/100)) + self.standard_price
#             actual_income_amt = (self.standard_price * (self.income_percentage/100)) + self.standard_price
#             self.income_amt = actual_income_amt - self.standard_price
#             actual_vat_amt = (self.standard_price * (self.vat_id.amount/100)) + self.standard_price
#             self.vat_amt = actual_vat_amt - self.standard_price
        
    @api.onchange('mrp')
    def onchange_mrp(self):
        if self.list_price and self.mrp:
            if not self.mrp >= self.list_price:
                raise UserError(_('Sale price should not be greater then the MRP.'))
        
    is_mrp = fields.Boolean('Is MRP')
    standard_price = fields.Float(
        'Actual Price', compute='_compute_standard_price',
        inverse='_set_standard_price', search='_search_standard_price',
        digits=dp.get_precision('Product Price'), groups="base.group_user",
        help="Cost of the product, in the default unit of measure of the product.")
    vat_id  = fields.Many2one('account.tax', 'VAT')
    vat_amt = fields.Float("")
    income_percentage = fields.Float('Income(%)')
    income_amt = fields.Float("")
    mrp = fields.Float('MRP')

    @api.model
    def create(self, vals):
        print('inth')
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
        if vals.get('standard_price'):
            related_vals['standard_price'] = vals['standard_price']
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