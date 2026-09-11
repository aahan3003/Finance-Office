# -*- coding: utf-8 -*-

from odoo import models, fields, api


class GoldLoan(models.Model):
    _name = 'gold.loan'
    _description = 'Gold Loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Reference to Business Loan
    business_loan_id = fields.Many2one('business.loan', string='Business Loan', ondelete='cascade')
    
    # Gold Details
    gold_type = fields.Selection([
        ('ornaments', 'Ornaments'),
        ('coins', 'Coins'),
        ('bars', 'Bars'),
        ('jewelry', 'Jewelry'),
    ], string='Gold Type', required=True)
    
    gold_purity = fields.Selection([
        ('22k', '22 Karat (916.7)'),
        ('23k', '23 Karat (958)'),
        ('24k', '24 Karat (999)'),
        ('other', 'Other'),
    ], string='Gold Purity', required=True)
    
    gold_quantity = fields.Float('Gold Quantity (grams)', required=True)
    gold_weight_verified = fields.Float('Weight After Verification (grams)')
    
    # Gold Valuation
    gold_rate_per_gram = fields.Float('Gold Rate per Gram (Rs.)', required=True)
    gold_gross_value = fields.Float('Gross Gold Value', compute='_compute_gold_gross_value', store=True)
    
    # Purity Factor
    purity_factor = fields.Float('Purity Factor (%)')
    gold_net_value = fields.Float('Net Gold Value (After Purity)', compute='_compute_gold_net_value', store=True)
    
    # Loan Against Gold
    loan_to_value_ratio = fields.Float('Loan to Value Ratio (%)', default=75.0, help='Percentage of gold value given as loan')
    loan_amount = fields.Float('Loan Amount', compute='_compute_loan_amount', store=True, required=True)
    
    # Loan Terms
    interest_rate = fields.Float('Interest Rate (% p.a.)', required=True)
    tenure_months = fields.Integer('Tenure (Months)', required=True)
    emi_amount = fields.Float('Monthly Interest Charge', compute='_compute_emi', store=True)
    
    # Insurance
    insurance_type = fields.Selection([
        ('full', 'Full Coverage'),
        ('partial', 'Partial Coverage'),
        ('none', 'No Insurance'),
    ], string='Insurance Type', default='full')
    
    insurance_premium = fields.Float('Insurance Premium Amount')
    
    # Custody Details
    storage_location = fields.Char('Storage Location')
    storage_box_number = fields.Char('Storage Box Number')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('valuation_pending', 'Valuation Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active'),
        ('matured', 'Matured'),
        ('redeemed', 'Redeemed'),
    ], string='Status', default='draft', tracking=True)
    
    # Important Dates
    application_date = fields.Date('Application Date', default=fields.Date.today)
    valuation_date = fields.Date('Valuation Date')
    approval_date = fields.Date('Approval Date')
    loan_start_date = fields.Date('Loan Start Date')
    loan_end_date = fields.Date('Loan End Date')
    redemption_date = fields.Date('Redemption Date')
    
    # Valuation Officer
    valuation_officer_id = fields.Many2one('res.users', string='Valuation Officer')
    valuation_notes = fields.Text('Valuation Notes')
    
    # Documents
    item_description = fields.Text('Item Description')
    item_photo = fields.Binary('Item Photo')
    valuation_certificate = fields.Binary('Valuation Certificate')
    
    # Repayment
    repayment_status = fields.Selection([
        ('not_due', 'Not Due'),
        ('due', 'Due'),
        ('overdue', 'Overdue'),
        ('paid', 'Paid'),
    ], string='Repayment Status', default='not_due', compute='_compute_repayment_status', store=True)
    
    total_amount_payable = fields.Float('Total Amount Payable', compute='_compute_total_payable', store=True)
    
    # Notes
    notes = fields.Text('Notes')

    # Computed Fields
    @api.depends('gold_quantity', 'gold_rate_per_gram')
    def _compute_gold_gross_value(self):
        for record in self:
            record.gold_gross_value = record.gold_quantity * record.gold_rate_per_gram

    @api.depends('gold_gross_value', 'purity_factor')
    def _compute_gold_net_value(self):
        for record in self:
            purity_factor = record.purity_factor or 100
            record.gold_net_value = record.gold_gross_value * (purity_factor / 100)

    @api.depends('gold_net_value', 'loan_to_value_ratio')
    def _compute_loan_amount(self):
        for record in self:
            ratio = record.loan_to_value_ratio or 75
            record.loan_amount = record.gold_net_value * (ratio / 100)

    @api.depends('loan_amount', 'interest_rate')
    def _compute_emi(self):
        for record in self:
            if record.loan_amount and record.interest_rate:
                monthly_rate = record.interest_rate / 12 / 100
                record.emi_amount = record.loan_amount * monthly_rate
            else:
                record.emi_amount = 0

    @api.depends('emi_amount', 'tenure_months', 'loan_amount')
    def _compute_total_payable(self):
        for record in self:
            record.total_amount_payable = record.loan_amount + (record.emi_amount * record.tenure_months)

    @api.depends('loan_end_date')
    def _compute_repayment_status(self):
        from datetime import date
        today = date.today()
        for record in self:
            if record.loan_end_date:
                if record.loan_end_date < today:
                    record.repayment_status = 'overdue'
                elif record.loan_end_date == today:
                    record.repayment_status = 'due'
                else:
                    record.repayment_status = 'not_due'

    # Action Methods
    @api.multi
    def action_submit_for_valuation(self):
        for record in self:
            record.state = 'valuation_pending'

    @api.multi
    def action_approve(self):
        for record in self:
            record.approval_date = fields.Date.today()
            record.state = 'approved'

    @api.multi
    def action_activate_loan(self):
        for record in self:
            from datetime import datetime, timedelta
            record.loan_start_date = fields.Date.today()
            record.loan_end_date = fields.Date.today() + timedelta(days=30 * record.tenure_months)
            record.state = 'active'

    @api.multi
    def action_redeem(self):
        for record in self:
            record.redemption_date = fields.Date.today()
            record.state = 'redeemed'

    @api.multi
    def action_reject(self):
        for record in self:
            record.state = 'rejected'

    # Onchange Methods
    @api.onchange('gold_purity')
    def onchange_gold_purity(self):
        purity_mapping = {
            '22k': 91.67,
            '23k': 95.83,
            '24k': 99.9,
        }
        if self.gold_purity in purity_mapping:
            self.purity_factor = purity_mapping[self.gold_purity]
