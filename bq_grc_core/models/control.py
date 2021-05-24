from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import datetime


# Control type model
#
class GrcControlType(models.Model):
    _name = "grc.control.type"
    _description = "Control Type"
    _order = 'id'
    _inherit = ['mail.thread']
    name = fields.Char('Control Type', required=True, tracking=True)


# Control model
class GrcControl(models.Model):
    _name = "grc.control"
    _description = "Controls"
    _inherit = ['mail.thread', 'grc.grc']

    single_id_name = 'control_id'
    multi_id_name = 'control_ids'

    name = fields.Char(string='Control name', required=True, tracking=True)
    name_sequence = fields.Char(string='Control Reference', required=True, copy=False, readonly=True, index=True,
                                default=lambda self: _('New'))
    control_type_id = fields.Many2one(
        'grc.control.type', 'Control Type',
        required=True,
        tracking=True)

    objective =fields.Text(string='Control objective')
    review_date = fields.Date(string="Review date", tracking=True)
    all_day = fields.Boolean(invisible=True, readonly=True, default=True)
    owner_id = fields.Many2one('res.partner', string="Owner", tracking=True)
    responsible_id = fields.Many2one('res.partner', 'Responsible')

    ##
    # Relations to other concepts
    ##

    risk_ids = fields.Many2many('grc.risk', string="Risks")
    risk_count = fields.Integer(compute='count_risks')
    asset_ids = fields.Many2many('grc.asset',string="Assets")
    asset_count = fields.Integer(compute='count_assets')

    view_relations = {
        'risk': ('grc.risk', 'control_ids', 'Control'),
        'asset': ('grc.asset','control_ids','Asset')
    }

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('inactive', 'Inactive')
        ], string="Status", readonly=True, default='draft'
    )

    def count_risks(self):
        for record in self:
            record.risk_count = self.env['grc.risk'].search_count([('control_ids', '=', self.id)])

    def count_assets(self):
        for record in self:
            record.asset_count = self.env['grc.asset'].search_count([('control_ids', '=', self.id)])

    @api.constrains('review_date')
    def _check_future(self):
        for record in self:
            if record.review_date:
                if record.review_date < datetime.date.today():
                    raise ValidationError("Review date should be in the future.")

        # ---------------------------------------------------------
        # Business Methods
        # ---------------------------------------------------------

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Controls'),
            'template': '/grc/static/xls/grc_controls.xls'
        }]

    def action_activate(self):
        for record in self:
            record.state = 'active'

    def action_draft(self):
        for record in self:
            record.state = 'draft'

    def action_inactivate(self):
        for record in self:
            record.state = 'inactive'

    # override
    def get_relations(self):
        return self.view_relations

    # ----
    # Override the create method to add the sequence
    #
    @api.model
    def create(self, vals):
        if (vals.get('name_sequence', _('New')) == _('New')):
            vals['name_sequence'] = self.env['ir.sequence'].next_by_code('grc.control.sequence') or _('New')
        result = super(GrcControl, self).create(vals)
        return result
