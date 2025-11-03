from odoo import fields, models

class PhongBan(models.Model):
    _name = 'phong.ban'

    name = fields.Char('Name', required=True)
