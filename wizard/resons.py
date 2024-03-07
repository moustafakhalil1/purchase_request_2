from odoo import fields,api,models

class RejectionReason(models.TransientModel):
    _name='rejection.reason'
    name=fields.Char(required=True)

    def action_add_rejection(self):
       active_id = self.env.context.get('active_id')
       # to get only count of records
       # current_real = self.env['real.state'].search_count([])
       current_purchase_request = self.env['purchase.request'].search([('id', '=', active_id)])
       current_purchase_request.RejectionReason = self.name
       current_purchase_request.state='reject'