from win32com.server import exception
from odoo import fields, models, api, _
from datetime import timedelta
from odoo.exceptions import UserError


class EstateOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'offers made for real estate'
    _order = 'price desc'

    price = fields.Float()
    status = fields.Selection(
        [
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
        ],
        copy=False,
    )
    partner_id = fields.Many2one('res.partner',required=True)
    property_id = fields.Many2one('estate.property',required=True)
    validity = fields.Integer(default=7)
    date_deadline = fields.Date(
        compute='_compute_date_deadline',
        inverse='_inverse_date_deadline',
        store=True,
    )

    property_type_id = fields.Many2one(
        related='property_id.property_type_id',
        store=True,
        string='Property Type',
    )
    _sql_constraints = [
        ('check_offer_price_positive','CHECK(price>0)','The offer price must be strictly positive.'),
    ]

    @api.model
    def create(self, vals):
        property_id = vals.get('property_id')
        property_record = self.env['estate.property'].browse(property_id)

        existing_max_price = max(property_record.offer_id.mapped('price') or [0])
        if vals.get('price', 0) <= existing_max_price:
            raise exception.UserError(
                _('You cannot create an offer with a lower price than existing ones.')
            )
        property_record.state = 'offer_received'
        return super(EstateOffer, self).create(vals)


    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            create_date=record.create_date or fields.Datetime.now()
            record.date_deadline=(create_date + timedelta(days=record.validity)).date()

    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline and record.create_date:
                record.validity = (record.date_deadline - record.create_date.date()).days
    def action_accept(self):
        self.ensure_one()
        if "accepted" in self.property_id.offer_id.mapped('status'):
            raise UserError(_("Text error"))
        self.status = 'accepted'
        self.property_type_id.selling_price = self.price

    def action_refuse(self):
        self.ensure_one()
        self.status = 'refused'