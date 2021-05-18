from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Grc(models.AbstractModel):
    _name = "grc.grc"

    view_relations = {}
    single_id_name = ''

    note = fields.Html(string='Description')
    active = fields.Boolean('Active', default=True, help="Archive the record")

    def get_relations(self):
        return self.view_relations

    def get_link_to_records(self):
        link = self.env.context.get('link')
        relations = self.get_relations()
        if not relations[link]:
            raise ValidationError("Relation not found.")
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'view_mode': 'tree,form',
            'res_model': relations[link][0],
            'domain': [(relations[link][1], '=', self.id)],
            'context': "{'create': True}"
        }

    def action_publish(self):
        for record in self:
            record.state='published'

    def action_draft(self):
        for record in self:
            record.state='draft'

    def action_archive(self):
        for record in self:
            record.state='archived'
