from odoo import models, fields, api

class TravelCity(models.Model):
    _name = 'traveloop.city'
    _description = 'City'
    name        = fields.Char('City Name', required=True)
    country     = fields.Char('Country')
    description = fields.Text('Description')
    cost_index  = fields.Float('Cost Per Day ($)')
    popularity  = fields.Selection([('low','Low'),('medium','Medium'),('high','High')], default='medium')

class TravelActivity(models.Model):
    _name = 'traveloop.activity'
    _description = 'Activity'
    name          = fields.Char('Activity Name', required=True)
    city_id       = fields.Many2one('traveloop.city', string='City')
    activity_type = fields.Selection([('sightseeing','Sightseeing'),('food','Food Tour'),('adventure','Adventure'),('culture','Culture'),('shopping','Shopping')])
    cost          = fields.Float('Estimated Cost ($)')
    duration      = fields.Float('Duration (hours)')
    description   = fields.Text('Description')

class TravelTrip(models.Model):
    _name = 'traveloop.trip'
    _description = 'Trip'
    _inherit = ['mail.thread']
    name         = fields.Char('Trip Name', required=True)
    user_id      = fields.Many2one('res.users', default=lambda self: self.env.user)
    start_date   = fields.Date('Start Date')
    end_date     = fields.Date('End Date')
    description  = fields.Text('Description')
    is_public    = fields.Boolean('Share Publicly', default=False)
    state        = fields.Selection([('draft','Planning'),('confirmed','Confirmed'),('done','Completed')], default='draft')
    stop_ids      = fields.One2many('traveloop.stop', 'trip_id', string='Stops')
    checklist_ids = fields.One2many('traveloop.checklist', 'trip_id', string='Packing List')
    note_ids      = fields.One2many('traveloop.note', 'trip_id', string='Notes')
    total_budget = fields.Float('Total Budget ($)')
    total_cost   = fields.Float('Estimated Cost ($)', compute='_compute_total_cost', store=True)
    stop_count   = fields.Integer(compute='_compute_stop_count')

    @api.depends('stop_ids.total_cost')
    def _compute_total_cost(self):
        for trip in self:
            trip.total_cost = sum(trip.stop_ids.mapped('total_cost'))

    def _compute_stop_count(self):
        for trip in self:
            trip.stop_count = len(trip.stop_ids)

class TravelStop(models.Model):
    _name = 'traveloop.stop'
    _description = 'Trip Stop'
    trip_id        = fields.Many2one('traveloop.trip', required=True, ondelete='cascade')
    city_id        = fields.Many2one('traveloop.city', string='City', required=True)
    arrive_date    = fields.Date('Arrival Date')
    leave_date     = fields.Date('Departure Date')
    notes          = fields.Text('Notes')
    activity_ids   = fields.Many2many('traveloop.activity', string='Activities')
    stay_cost      = fields.Float('Stay Cost ($)')
    transport_cost = fields.Float('Transport Cost ($)')
    meal_cost      = fields.Float('Meal Cost ($)')
    total_cost     = fields.Float('Total Cost ($)', compute='_compute_cost', store=True)

    @api.depends('stay_cost','transport_cost','meal_cost','activity_ids.cost')
    def _compute_cost(self):
        for stop in self:
            activity_total = sum(stop.activity_ids.mapped('cost'))
            stop.total_cost = stop.stay_cost + stop.transport_cost + stop.meal_cost + activity_total

class TravelChecklist(models.Model):
    _name = 'traveloop.checklist'
    _description = 'Packing Checklist'
    trip_id   = fields.Many2one('traveloop.trip', required=True, ondelete='cascade')
    item      = fields.Char('Item', required=True)
    category  = fields.Selection([('clothing','Clothing'),('documents','Documents'),('electronics','Electronics'),('medicine','Medicine'),('other','Other')], default='other')
    is_packed = fields.Boolean('Packed?', default=False)

class TravelNote(models.Model):
    _name = 'traveloop.note'
    _description = 'Trip Note'
    trip_id = fields.Many2one('traveloop.trip', required=True, ondelete='cascade')
    title   = fields.Char('Title')
    content = fields.Text('Note')
    date    = fields.Datetime('Date', default=fields.Datetime.now)
