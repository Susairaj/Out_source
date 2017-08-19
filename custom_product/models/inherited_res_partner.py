from openerp import api, fields, models,tools,_


class ResPartner(models.Model):
    _inherit = 'res.partner'

    tin_no = fields.Char ('GST TIN')
    
class UpdateProduct(models.Model):
    _name = 'update.product'

    name = fields.Char ('Name')
    
    @api.multi
    def update_vat(self):
        product_ids = self.env['product.product'].search([])
        for product_id in product_ids:
            if not product_id.vat_percentage:
                product_id.vat_percentage = product_id.vat_id.amount