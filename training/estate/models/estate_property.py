from datetime import timedelta,date
from odoo import fields,models,api,_
from odoo.exceptions import UserError


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _order = ''

    name = fields.Char('Property Name', required=True)
    description = fields.Text('Property Description')
    postcode = fields.Char('Postcode')
    expected_price = fields.Float('Expected Price', required=True)
    selling_price = fields.Float('Selling Price', readonly=True, copy=False)
    bedrooms = fields.Integer('Bedrooms', default=2)
    date_availability = fields.Date('Date Availability', copy=False, default=lambda self: date.today() + timedelta(days=90))
    living_area = fields.Integer('Living Area', search='_search_living_area')
    facade = fields.Integer('Facade')
    garage = fields.Boolean('Garage', default=True)
    garden = fields.Boolean('Garden', default=True)
    garden_area = fields.Integer('Garden Area')
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('west', 'West'),
        ('east', 'East'),
    ], string="Garden Orientation", copy=False, required=True, default='north')
    state = fields.Selection([
        ('offer_received', 'Offer Received'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled'),
        ('new', 'New')
    ], default='new', copy=False)

    property_type_id = fields.Many2one('estate.property.type')
    buyer_id = fields.Many2one('res.partner', string="Buyer", copy=False)
    salePerson_id = fields.Many2one('res.users', string="Sales Person", default=lambda self: self.env.user)
    offer_id = fields.One2many('estate.property.offer', 'property_id')
    tag_id = fields.Many2many('estate.property.tag')

    total_area = fields.Integer('Total Area', compute='_compute_total_area',store=True)

    _sql_constraints = [
        ('check_expected_price_positive','CHECK(expected_price>=0)','Expected Price is greater than 0'),
        ('check_selling_price_positive','CHECK(selling_price>=0)','Selling Price is greater than 0'),
    ]

    def _search_living_area(self, operator, value):
        if operator in ['=', '>']:
            return [('living_area', '>=', value)]
        return [('living_area', operator, value)]

    @api.ondelete(at_uninstall=False)
    def _unlink_if_allowed(self):
        for record in self:
            if record.state not in ['new', 'canceled']:
                raise UserError(
                    _('You cannot delete a property that is not in New or Canceled state.')
                )


    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
         for record in self:
             record.total_area = (record.living_area or 0) + (record.garden_area or 0)

    best_price = fields.Float('Best Price', compute='_compute_best_price', store=True)
    @api.depends('offer_id.price')
    def _compute_best_price(self):
        for record in self:
            if record.offer_id:
                record.best_price = max(record.offer_id.mapped('price') or [0.0],default=0.0)
            else:
                record.best_price = 0.0

    @api.onchange('garden')
    def _onchange_garden(self):
        for estate in self:
            if not estate.garden:
                estate.garden_area = 0

    @api.onchange('date_availability')
    def _onchange_date_availability(self):
        for estate in self:
            return {
                'warning':{
                    'title':_('Warning'),
                    'message':_('My message')
                }
            }

    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError(_('A sold property cannot be cancelled.'))
            record.state = 'canceled'

    def action_sold(self):
        for record in self:
            if record.state == 'canceled':
                raise UserError(_('A canceled property cannot be sold.'))
            record.state = 'sold'

    @api.constrains('selling_price')
    def _check_constrain(self):
        for estate in self:
            if estate.selling_price < 5000:
                raise ValidationError(_('Test message'))

    @api.constrains('selling_price','expected_price')
    def _check_selling_price(self):
        #check thg selling price có giá trị
        for record in self:
            if record.selling_price and record.expected_price:
                if record.selling_price < 0.9 * record.expected_price:
                    raise ValidationError(
                        'The selling price cannot be lower than 90% of the expected price.'
                        )