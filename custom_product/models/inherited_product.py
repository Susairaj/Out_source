from openerp import api, fields, models, _
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
        if self.standard_price and self.vat_id and self.income_percentage:
            self.list_price = (self.standard_price * ((self.vat_id.amount + self.income_percentage)/100)) + self.standard_price
        
    @api.onchange('mrp')
    def onchange_mrp(self):
        if self.list_price and self.mrp:
            if not self.mrp >= self.list_price:
                raise UserError(_('Sale price should not be greater then the MRP.'))
        
    options = fields.Selection([('paint','Paint'),('others','Others')],default="paint",string= 'Options')
    standard_price = fields.Float(
        'Actual Price', compute='_compute_standard_price',
        inverse='_set_standard_price', search='_search_standard_price',
        digits=dp.get_precision('Product Price'), groups="base.group_user",
        help="Cost of the product, in the default unit of measure of the product.")
    vat_id  = fields.Many2one('account.tax', 'VAT')
    income_percentage = fields.Float('Income(%)')
    mrp = fields.Float('MRP')
