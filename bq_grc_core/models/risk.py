from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from random import randint
import datetime


# Risk type model
#

class GrcRiskType(models.Model):
    _name = "grc.risk.type"
    _description = "Risk Type"
    _order = 'id'
    name = fields.Char('Risk Type', required=True, tracking=True)

class GrcRiskLikelihood(models.Model):
    _name = "grc.risk.likelihood"
    _description = "Risk likelihood"
    _order = 'id'
    name = fields.Char('Likelihood', required=True, tracking=True)
    value = fields.Integer('Value', required=True)
    note = fields.Text('Description')

class GrcRiskSeverity(models.Model):
    _name = "grc.risk.severity"
    _description = "Risk severity"
    _order = 'id'
    name = fields.Char('Likelihood', required=True, tracking=True)
    value = fields.Integer('Value', required=True)
    note = fields.Text('Description')

class GrcRiskThreat(models.Model):
    _name = "grc.risk.threat"
    _description = "Risk threats"
    _order = 'name'
    name = fields.Char('Threat', required=True)
    note = fields.Text('Description')
    source = fields.Text('Source')
    color = fields.Integer('Color', default='50')

class GrcRiskVulnerability(models.Model):
    _name = "grc.risk.vulnerability"
    _description = "Risk Vulnerabilities"
    _order = "name"
    name = fields.Char("Vulnerability", required=True)
    note = fields.Text('Description')

class GrcRiskSet(models.Model):
    _name = "grc.risk.set"
    _description = "Risk Set"
    _order = "name"
    name = fields.Char("Set name", required=True)
    description = fields.Text('Description')

class GrcRiskAssessment(models.Model):
    _name = "grc.risk.assessment"
    _description = 'Risk assessment'
    name=fields.Char('Name', required=True)
    assessment_date = fields.Date(string='Assessment date', required=True)
    assessment_year = fields.Integer(string='Year',default=2020)
    assessment_year_extra = fields.Char(string='Extra',size=3)
    assessment_period = fields.Char(string='Period',compute='_compute_period')
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('active', 'Active'),
            ('archived', 'Archived')
        ], string="Status", readonly=True, default='draft'
    )
    risk_id = fields.Many2one('grc.risk', required=True)
    likelihood_id = fields.Many2one('grc.risk.likelihood', string="Likelihood", required=True)
    severity_id = fields.Many2one('grc.risk.severity', string='Severity', required=True)
    responsible_id=fields.Many2one('res.partner',string='Responsible', required=True)
    score = fields.Integer(string="Score", compute='_calc_assessment_score', store=True)
    color = fields.Char("Color", default="green")
    impact_type = fields.Selection([
        ('operations','Operations'),
        ('assets','Assets'),
        ('indiv','Individuals'),
        ('other','Other organizations')
    ])

    @api.depends('likelihood_id', 'severity_id')
    def _calc_assessment_score(self):
        score = -1
        for record in self:
            record.score = record.likelihood_id.value * record.severity_id.value

    @api.depends('assessment_year','assessment_year_extra')
    def _compute_period(self):
        for record in self:
            if (record.assessment_year):
                if (record.assessment_year_extra):
                    record.assessment_period= "{}/{}".format(record.assessment_year, record.assessment_year_extra)
                else:
                    record.assessment_period = "{}".format(record.assessment_year)
            else:
                record.assessment_period=""


##############
# Risk model #
##############
class GrcRisk(models.Model):
    _name = "grc.risk"
    _description = "Risks"
    _inherit = ['mail.thread','grc.grc']

    name = fields.Char(string='Risk name', required=True, tracking=True)
    risk_type_id = fields.Many2one(
        'grc.risk.type', 'Risk Type',
        required=True,
        tracking=True)

    single_id_name = 'risk_id'
    multi_id_name = 'risk_ids'

    name_sequence = fields.Char(string='Risk Reference', required=True, copy=False, readonly=True, index=True,
                                default=lambda self: _('New'))
    note = fields.Text(string='Description', tracking=True)
    review_date = fields.Date(string="Review date", tracking=True, required=True)

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('published', 'Published'),
            ('archived', 'Archived')
        ], string="Status", readonly=True, default='draft', tracking=True
    )

    ##
    score = fields.Integer(string="Max risk score", compute='_calc_risk_score', store=True, tracking=True)
    color = fields.Char("Color", default="green")

    ## Links to other concepts:
    assessment_id = fields.One2many('grc.risk.assessment','risk_id',string="Assessments", ondelete="cascade" ,tracking=True)
    control_ids = fields.Many2many('grc.control',string="Control", tracking=True)
    policy_ids = fields.Many2many('grc.policy',string="Policies")
    asset_ids = fields.Many2many('grc.asset', string="Assets")
    view_relations = {
        'asset': ('grc.asset', 'risk_ids', 'Asset'),
        'control': ('grc.control', 'risk_ids', 'Control'),
        'policy': ('grc.policy', 'risk_ids', 'Policies')
    }
    control_count = fields.Integer(compute='compute_controls')
    asset_count = fields.Integer(compute='compute_assets')
    policy_count=fields.Integer(compute='compute_policies')

    #
    threat_id = fields.Many2many('grc.risk.threat', string="Threat")
    ##
    vulnerability_id = fields.Many2many('grc.risk.vulnerability', string="Vulnerability")
    ##
    treatment = fields.Selection(
        selection=[('mitigate', 'Mitigate'), ('accept', 'Accept'), ('share', 'Share'), ('avoid', 'Avoid')]
    )

    # Doc fields
    consequences = fields.Text(string="Consequences", tracking=True)
    scenario = fields.Text(string='Scenario', tracking=True)
    # Tagging
    tag_ids = fields.Many2many(
        'grc.risk.tag', 'grc_risk_tag_rel',
        'tag_id', 'risk_id', string='Tags')
    color = fields.Integer(string='Color Index')

    all_day = fields.Boolean(invisible=True, readonly=True, default=True)
    owner_id = fields.Many2one('res.partner', string="Owner", tracking=True)
    partner_id = fields.Many2one('res.partner', 'Responsible')


    @api.constrains('review_date')
    def _check_future(self):
        for record in self:
            if record.review_date:
                if record.review_date < datetime.date.today():
                    raise ValidationError("Review date should be in the future.")

    # ----
    # Override the create method to add the sequence
    #
    @api.model
    def create(self, vals):
        if (vals.get('name_sequence', _('New')) == _('New')):
            vals['name_sequence'] = self.env['ir.sequence'].next_by_code('grc.risk.sequence') or _('New')
        result = super(GrcRisk, self).create(vals)
        return result
        # ---------------------------------------------------------
        # Business Methods
        # ---------------------------------------------------------

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for risks'),
            'template': '/grc/static/xls/grc_risks.xls'
        }]

    def get_fields_to_ignore_in_search(self):
        return ['color', 'all_day']

    @api.model
    def fields_get(self, allfields=None, attributes=None):
        res = super(GrcRisk, self).fields_get(allfields, attributes=attributes)
        for field in self.get_fields_to_ignore_in_search():
            if res.get(field):
                res.get(field)['searchable'] = False
        return res

    @api.depends('assessment_id')
    def _calc_risk_score(self):
        ''' Calculate the score as the maximum of the assessment scores'''
        for record in self:
             max_assessment = self.env['grc.risk.assessment'].search([('risk_id', '=', record.id)],order='score desc',limit=1)
        if (max_assessment):
            record.score = max_assessment.score
        else:
            record.score=None

    def compute_controls(self):
        for record in self:
            record.control_count= self.env['grc.control'].search_count([('risk_ids', '=', self.id)])

    def compute_assets(self):
        for record in self:
            record.asset_count= self.env['grc.asset'].search_count([('risk_ids', '=', self.id)])

    def compute_policies(self):
        for record in self:
            record.policy_count= self.env['grc.policy'].search_count([('risk_ids', '=', self.id)])

class GrcRiskTag(models.Model):
    """Model for tagging of risks, ... """
    _name = 'grc.risk.tag'
    _description = 'Risk Tag'
    _order = 'name'

    def _default_color(self):
        return randint(1, 11)

    name = fields.Char(required=True, translate=True)
    color = fields.Integer(
        string='Color Index', default=lambda self: self._default_color(),
        help='Tag color. No color means no display in kanban to distinguish internal tags from public categorization tags.')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]