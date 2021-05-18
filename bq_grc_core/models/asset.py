from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import datetime


# Asset type model
class GrcAssetType(models.Model):
    _name = "grc.asset.type"
    _description = "Asset Type"
    _order = 'id'

    name = fields.Char('Asset Type', required=True, tracking=True)


# Asset model
class GrcAsset(models.Model):
    _name = "grc.asset"
    _description = "an Asset"
    _inherit = ['mail.thread','grc.grc']

    single_id_name='asset_id'
    multi_id_name='asset_ids'

    name = fields.Char(string='Asset name', required=True, tracking=True)
    name_sequence = fields.Char(string='Asset Reference', required=True, copy=False, readonly=True, index=True,
                                default=lambda self: _('New'))
    asset_type_id = fields.Many2one(
        'grc.asset.type', 'Asset Type',
        required=True,
        tracking=True,
        store=True)

    all_day = fields.Boolean(invisible=True, compute='')
    owner_id = fields.Many2one('res.partner', string="Owner", tracking=True)
    asset_user_id = fields.Many2one('res.partner', string="Asset user", tracking=True)

    ##
    # Relations to other concepts
    ##
    control_ids = fields.Many2many('grc.control', string="Controls", tracking=True)
    control_count = fields.Integer(compute='compute_controls')
    review_task_count = fields.Integer(compute='compute_review_tasks')
    risk_ids = fields.Many2many('grc.risk', string='Risks')
    risk_count = fields.Integer(compute='compute_risks')
    policy_ids = fields.Many2many('grc.policy',string='Policies', tracking=True)
    view_relations = {
        'control': ('grc.control', multi_id_name, 'Control'),
        'risk': ('grc.risk', multi_id_name, 'Risk'),
        'policy':('grc.policy', multi_id_name, 'Policy')
    }

    # department_id = fields.Many2one('hr.department', string="Business department", tracking=True)
    partner_id = fields.Many2one('res.partner', 'Responsible')

    def compute_controls(self):
        for record in self:
            record.control_count= self.env['grc.control'].search_count([('asset_ids', '=', record.id)])

    def compute_risks(self):
        for record in self:
            record.risk_count= self.env['grc.risk'].search_count([('asset_ids', '=', record.id)])

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
            'label': _('Import Template for Assets'),
            'template': '/grc/static/xls/grc_assets.xls'
        }]

    def create_asset_review_task(self):
        task_edit_form_view_id = self.env.ref('project.view_task_form2', False)
        if (not task_edit_form_view_id.id):
            ValidationError("Task edit form not found.  Contact the administrator.")

        return {
            'name': _('Name of the form'),
            'view_mode': 'form',
            'view_id': 'view_task_form2',
            'views': [(task_edit_form_view_id.id,'form')],
            'view_type': 'form',
            'res_id': False,  # id of the object to which to redirected
            'res_model': 'project.task',
            'type': 'ir.actions.act_window',
            'target': 'new',  # open the form in new tab
            'context': {'default_asset_id': self.id, 'default_name': 'Asset review task'}
        }

    # ----
    # Override the create method to add the sequence
    #
    @api.model
    def create(self, vals):
        if (vals.get('name_sequence', _('New')) == _('New')):
            vals['name_sequence'] = self.env['ir.sequence'].next_by_code('grc.asset.sequence') or _('New')
        result = super(GrcAsset, self).create(vals)
        return result