from openerp import api, fields, models,tools,_


class ResPartner(models.Model):
    _inherit = 'res.partner'

    tin_no = fields.Char ('GST TIN')