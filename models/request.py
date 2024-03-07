from odoo import api,fields,models,_
from datetime import datetime


class PurchaseRequest(models.Model):
    _name="purchase.request"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name=fields.Char(required=True)
    requested_by=fields.Many2one('res.users',default=lambda self: self.env.user,required=True)
    startDate=fields.Date(default=lambda self: datetime.today().date())
    endDate=fields.Date()
    order_lines_id = fields.One2many('purchase.request.line','order_id')
    RejectionReason=fields.Char(readonly=True)
    TotalPrice=fields.Float(readonly=True,compute='_compute_total_order_cost',store=True)
    state=fields.Selection([
        ('draft',"Draft"),
        ('approved','Approved'),
        ('reject','Reject'),
        ('cancel','Cancel'),
        ('to_be_approved','to be Approved'),
    ],default='draft')

    @api.depends('order_lines_id.Total')
    def _compute_total_order_cost(self):
        for order in self:
            order.TotalPrice = sum(order.order_lines_id.mapped('Total'))

    def action_submit_for_approval(self):
        self.state = 'to_be_approved'
    def action_approve(self):
        self.ensure_one()
        self.state = 'approved'

        # Get the purchase manager group
        # Get the purchase manager group
        purchase_managers_group = self.env.ref('purchase_request2.purchase_manager_group')
        purchase_managers = purchase_managers_group.users

        # Constructing the subject and body of the email
        subject = f"Purchase Request {self.name} Approved"
        body = f"Purchase Request {self.name} has been approved."

        # Send email notification to all users in the purchase manager group
        for manager in purchase_managers:
            mail_vals = {
                'subject': subject,
                'body_html': body,
                'email_to': manager.email,
            }
            self.env['mail.mail'].create(mail_vals).send()

            # Create a log note for each manager in the manager group
            self.message_post(
                body=body,
                subject=subject,
                partner_ids=[manager.partner_id.id],  # Use a command to add the manager as a recipient
                subtype_id=self.env.ref('mail.mt_note').id,  # Use subtype 'Note'
            )
        return True
    def action_cancle(self):
            self.state = 'cancel'

    def action_rejection_reason(self):
            self.state = 'reject'

    def action_reset_to_draft(self):
            self.state = 'draft'
class PurchaseRequestLine(models.Model):
    _name='purchase.request.line'
    order_id=fields.Many2one('purchase.request')
    product_id=fields.Many2one('product.product',required=True)
    Description=fields.Text(compute='_compute_description')
    quantity=fields.Integer(default=1)
    CostPrice=fields.Float(string='Product Cost ',readonly=True,related='product_id.standard_price',store=True)
    Total=fields.Float(readonly=True,compute='_compute_total_product_cost')

    @api.depends('product_id')
    def _compute_description(self):
        for line in self:
            line.Description = line.product_id.name
    @api.depends('quantity', 'CostPrice')
    def _compute_total_product_cost(self):
       for line in self:
        line.Total = line.quantity * line.CostPrice
