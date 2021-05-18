from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import datetime



# Control model
class GrcPolicy(models.Model):
    _name = "grc.policy"
    _description = "a Policy"
    _inherit = ['mail.thread','grc.grc']

    single_id_name = 'policy_id'
    multi_id_name = 'policy_ids'

    name = fields.Char(string='Policy name', required=True, tracking=True)
    name_sequence = fields.Char(string='Policy Reference', required=True, copy=False, readonly=True, index=True,
                                default=lambda self: _('New'))

    content = fields.Html(string='Content')
    doc_url = fields.Char(string='URL to document')
    attachment = fields.Binary(string='File')
    note = fields.Text(string='Description')
    review_date = fields.Date(string="Review date", tracking=True)
    owner_id = fields.Many2one('res.partner', string="Owner", tracking=True)
    partner_id = fields.Many2one('res.partner', 'Responsible')

    ##
    # Relations to other concepts
    ##
    risk_ids=fields.Many2many('grc.risk',string="Risks")
    risk_count=fields.Integer(compute='count_risks')
    view_relations = {
        'risk': ('grc.risk', 'policy_ids', 'Control')
    }

    state = fields.Selection(
        [
            ('draft','Draft'),
            ('active','Active'),
            ('inactive','Inactive')
        ], string="Status", readonly=True, default='draft'
    )

    def count_risks(self):
        for record in self:
            record.risk_count = self.env['grc.risk'].search_count([('policy_ids','=',self.id)])

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
            'template': '/grc/static/xls/grc_policies.xls'
        }]

    def action_activate(self):
        for record in self:
            record.state='active'

    def action_draft(self):
        for record in self:
            record.state='draft'

    def action_inactivate(self):
        for record in self:
            record.state='inactive'

    #override
    def get_relations(self):
        return self.view_relations


# ----
    # Override the create method to add the sequence
    #
    @api.model
    def create(self, vals):
        if (vals.get('name_sequence', _('New')) == _('New')):
            vals['name_sequence'] = self.env['ir.sequence'].next_by_code('grc.policy.sequence') or _('New')
        result = super(GrcPolicy, self).create(vals)
        return result