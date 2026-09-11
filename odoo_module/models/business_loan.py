# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class BusinessLoan(models.Model):
    _name = 'business.loan'
    _description = 'Business Loan Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char('Loan ID', required=True, copy=False, readonly=True, 
                       default=lambda self: self.env['ir.sequence'].next_by_code('business.loan') or 'NEW')
    
    loan_type = fields.Selection([
        ('two_wheeler', 'Two Wheeler'),
        ('three_wheeler', 'Three Wheeler'),
        ('gold_loan', 'Gold Loan'),
        ('business_loan', 'Business Loan'),
    ], string='Loan Type', required=True, tracking=True)
    
    borrower_id = fields.Many2one('res.partner', string='Borrower', required=True, tracking=True)
    partner_id = fields.Many2one('res.partner', string='Related Partner')
    
    # Loan Amount and Terms
    loan_amount = fields.Float('Loan Amount', required=True, tracking=True)
    interest_rate = fields.Float('Interest Rate (%)', required=True, tracking=True)
    loan_tenure = fields.Integer('Loan Tenure (Months)', required=True, tracking=True)
    
    # EMI Calculation
    emi_amount = fields.Float('EMI Amount', compute='_compute_emi', store=True, readonly=True)
    total_interest = fields.Float('Total Interest', compute='_compute_total_interest', store=True, readonly=True)
    total_amount_payable = fields.Float('Total Amount Payable', compute='_compute_total_payable', store=True, readonly=True)
    
    # Loan Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('closed', 'Closed'),
    ], string='Status', default='draft', tracking=True)
    
    # Dates
    application_date = fields.Date('Application Date', default=fields.Date.today)
    approval_date = fields.Date('Approval Date')
    disbursement_date = fields.Date('Disbursement Date')
    
    # Documents
    document_ids = fields.One2many('loan.document', 'loan_id', string='Documents')
    
    # Vehicle Information (for Two/Three Wheeler)
    vehicle_name = fields.Char('Vehicle Model')
    vehicle_registration = fields.Char('Registration Number')
    vehicle_value = fields.Float('Vehicle Value')
    
    # Gold Loan Information
    gold_quantity = fields.Float('Gold Quantity (grams)', help='Gold quantity in grams')
    gold_purity = fields.Selection([
        ('22k', '22 Karat'),
        ('24k', '24 Karat'),
        ('916', '91.6 Purity'),
        ('995', '99.5 Purity'),
    ], string='Gold Purity')
    gold_rate = fields.Float('Gold Rate per gram (Rs.)')
    gold_value = fields.Float('Total Gold Value', compute='_compute_gold_value', store=True)
    
    # Business Loan Information
    business_partner_id = fields.Many2one('res.partner', string='Business Entity')
    revenue_annual = fields.Float('Annual Revenue')
    profit_annual = fields.Float('Annual Profit')
    business_turnover = fields.Float('Business Turnover')
    credit_score = fields.Float('Credit Score', compute='_compute_credit_score', store=True)
    
    # Collateral Information
    collateral_type = fields.Selection([
        ('none', 'No Collateral'),
        ('vehicle', 'Vehicle'),
        ('gold', 'Gold'),
        ('property', 'Property'),
        ('inventory', 'Inventory'),
    ], string='Collateral Type', default='none')
    
    collateral_value = fields.Float('Collateral Value')
    collateral_description = fields.Text('Collateral Description')
    
    # Repayment Information
    repayment_schedule_ids = fields.One2many('loan.repayment.schedule', 'loan_id', string='Repayment Schedule')
    payment_account_id = fields.Many2one('account.account', string='Payment Account')
    
    # Notes
    notes = fields.Text('Notes')
    rejection_reason = fields.Text('Rejection Reason')
    
    # Computed Fields
    @api.depends('loan_amount', 'interest_rate', 'loan_tenure')
    def _compute_emi(self):
        for record in self:
            if record.loan_amount and record.interest_rate and record.loan_tenure:
                principal = record.loan_amount
                rate = record.interest_rate / 12 / 100
                n = record.loan_tenure
                
                if rate > 0:
                    emi = (principal * rate * (1 + rate) ** n) / ((1 + rate) ** n - 1)
                else:
                    emi = principal / n
                
                record.emi_amount = emi
            else:
                record.emi_amount = 0
    
    @api.depends('loan_amount', 'interest_rate', 'loan_tenure')
    def _compute_total_interest(self):
        for record in self:
            total_interest = (record.emi_amount * record.loan_tenure) - record.loan_amount
            record.total_interest = total_interest if total_interest > 0 else 0
    
    @api.depends('loan_amount', 'total_interest')
    def _compute_total_payable(self):
        for record in self:
            record.total_amount_payable = record.loan_amount + record.total_interest
    
    @api.depends('gold_quantity', 'gold_rate')
    def _compute_gold_value(self):
        for record in self:
            record.gold_value = record.gold_quantity * record.gold_rate if record.gold_quantity and record.gold_rate else 0
    
    @api.depends('revenue_annual', 'profit_annual', 'business_turnover')
    def _compute_credit_score(self):
        for record in self:
            score = 0
            if record.revenue_annual:
                score += min((record.revenue_annual / 1000000) * 10, 30)  # Max 30 points
            if record.profit_annual and record.revenue_annual:
                profit_margin = (record.profit_annual / record.revenue_annual) * 100
                score += min(profit_margin / 5, 40)  # Max 40 points
            if record.business_turnover:
                score += min((record.business_turnover / 500000) * 20, 30)  # Max 30 points
            
            record.credit_score = min(score, 100)
    
    # Action Methods
    @api.multi
    def action_submit(self):
        for record in self:
            record.state = 'submitted'
    
    @api.multi
    def action_send_for_review(self):
        for record in self:
            record.state = 'under_review'
    
    @api.multi
    def action_approve(self):
        for record in self:
            record.approval_date = fields.Date.today()
            record.state = 'approved'
            record._generate_repayment_schedule()
    
    @api.multi
    def action_reject(self):
        for record in self:
            record.state = 'rejected'
    
    @api.multi
    def action_disburse(self):
        for record in self:
            if record.state == 'approved':
                record.disbursement_date = fields.Date.today()
                record.state = 'active'
    
    @api.multi
    def action_generate_repayment_schedule(self):
        for record in self:
            record._generate_repayment_schedule()
    
    def _generate_repayment_schedule(self):
        """Generate EMI repayment schedule"""
        self.env['loan.repayment.schedule'].search([('loan_id', '=', self.id)]).unlink()
        
        start_date = self.disbursement_date or fields.Date.today()
        
        for month in range(1, int(self.loan_tenure) + 1):
            payment_date = start_date + timedelta(days=30 * month)
            self.env['loan.repayment.schedule'].create({
                'loan_id': self.id,
                'installment_no': month,
                'payment_date': payment_date,
                'emi_amount': self.emi_amount,
                'principal_amount': self.emi_amount * 0.7,  # Simplified calculation
                'interest_amount': self.emi_amount * 0.3,
                'balance_amount': self.loan_amount - (self.emi_amount * month * 0.7),
            })
    
    @api.onchange('gold_quantity', 'gold_rate')
    def onchange_gold_values(self):
        if self.gold_quantity and self.gold_rate:
            self.collateral_value = self.gold_value
    
    @api.onchange('vehicle_value')
    def onchange_vehicle_value(self):
        if self.vehicle_value and self.loan_type in ['two_wheeler', 'three_wheeler']:
            self.collateral_value = self.vehicle_value


class LoanDocument(models.Model):
    _name = 'loan.document'
    _description = 'Loan Documents'
    
    loan_id = fields.Many2one('business.loan', string='Loan', required=True, ondelete='cascade')
    document_type = fields.Selection([
        ('identity', 'Identity Proof'),
        ('address', 'Address Proof'),
        ('income', 'Income Proof'),
        ('bank', 'Bank Statement'),
        ('vehicle', 'Vehicle Document'),
        ('gold', 'Gold Certificate'),
        ('business', 'Business Registration'),
        ('other', 'Other'),
    ], string='Document Type', required=True)
    
    document_name = fields.Char('Document Name', required=True)
    document_file = fields.Binary('Document File', attachment=True)
    file_name = fields.Char('File Name')
    upload_date = fields.Date('Upload Date', default=fields.Date.today)
    
    is_verified = fields.Boolean('Verified', default=False)
    verified_by = fields.Many2one('res.users', string='Verified By')
    verified_date = fields.Date('Verification Date')


class LoanRepaymentSchedule(models.Model):
    _name = 'loan.repayment.schedule'
    _description = 'Loan Repayment Schedule'
    _order = 'installment_no'
    
    loan_id = fields.Many2one('business.loan', string='Loan', required=True, ondelete='cascade')
    installment_no = fields.Integer('Installment No.', required=True)
    payment_date = fields.Date('Payment Date', required=True)
    
    emi_amount = fields.Float('EMI Amount', required=True)
    principal_amount = fields.Float('Principal Amount')
    interest_amount = fields.Float('Interest Amount')
    balance_amount = fields.Float('Balance Amount')
    
    payment_status = fields.Selection([
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('partial', 'Partial Payment'),
    ], string='Payment Status', default='pending')
    
    payment_date_actual = fields.Date('Actual Payment Date')
    payment_amount = fields.Float('Payment Amount')
    
    notes = fields.Text('Notes')
