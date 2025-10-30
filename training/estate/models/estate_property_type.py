from odoo import fields, models, _, api


class PropertyType(models.Model):
    _name = 'estate.property.type'
    _inherit = 'estate.mixin'
    _description = 'Test'
    _order = 'sequence desc, name'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=1)
    property_id = fields.One2many('estate.property',
                                  'property_type_id',
                                  string='Properties')
    property_count = fields.Integer(compute='_compute_property_count')
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string='Offers')
    offer_count = fields.Integer(compute='_compute_offer_count')

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for val in vals_list:
            name = val.get('name')
            if name:  # chỉ tạo nếu có name
                self.env['estate.property.tag'].create({'name': name})
        return res

    def unlink(self):
        self.property_id.unlink()
        return super().unlink()

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    @api.depends('property_id')
    def _compute_property_count(self):
        for rec in self:
            rec.property_count = len(rec.property_id)

    _sql_constraints = [
        ('unique_name', 'UNIQUE(name)', 'Name should be unique')
    ]

    def action_open_property_ids(self):
        return {
            'name': _('Related Properties'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'estate.property',
            'target': 'current',
            'domain': [('property_type_id', '=', self.id)],
            'context': {'default_property_type_id': self.id},
        }
