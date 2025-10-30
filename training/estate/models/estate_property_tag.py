from odoo import fields, models



class PropertyTag(models.Model):
    _name = 'estate.property.tag'
    _inherit = 'estate.mixin'
    _description = 'Tag of real estate'
    _sql_constraints = [
        ('unique_tag_name','UNIQUE(name)','Tag name should be unique')
    ]
    _order = 'name'
    color = fields.Integer('Color')


