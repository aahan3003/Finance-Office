# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
from datetime import datetime


class LoanCreditScore(models.Model):
    _name = 'loan.credit.score'
    _description = 'Loan Credit Score Calculation'

    name = fields.Char('Name')
    
    # Score Factors
    revenue_factor = fields.Float('Revenue Factor (0-30)', default=10.0)
    profit_margin_factor = fields.Float('Profit Margin Factor (0-25)', default=10.0)
    turnover_factor = fields.Float('Turnover Factor (0-20)', default=10.0)
    payment_history_factor = fields.Float('Payment History Factor (0-15)', default=7.0)
    collateral_factor = fields.Float('Collateral Factor (0-10)', default=8.0)
    
    total_score = fields.Float('Total Score (0-100)', compute='_compute_total_score', store=True)
    
    # Risk Category
    risk_category = fields.Selection([
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk'),
    ], string='Risk Category', compute='_compute_risk_category', store=True)
    
    @api.depends('revenue_factor', 'profit_margin_factor', 'turnover_factor', 'payment_history_factor', 'collateral_factor')
    def _compute_total_score(self):
        for record in self:
            record.total_score = sum([
                record.revenue_factor,
                record.profit_margin_factor,
                record.turnover_factor,
                record.payment_history_factor,
                record.collateral_factor,
            ])
    
    @api.depends('total_score')
    def _compute_risk_category(self):
        for record in self:
            if record.total_score >= 75:
                record.risk_category = 'low'
            elif record.total_score >= 50:
                record.risk_category = 'medium'
            else:
                record.risk_category = 'high'


class LoanInterestRate(models.Model):
    _name = 'loan.interest.rate'
    _description = 'Interest Rate Configuration'

    name = fields.Char('Name', required=True)
    loan_type = fields.Selection([
        ('two_wheeler', 'Two Wheeler'),
        ('three_wheeler', 'Three Wheeler'),
        ('gold_loan', 'Gold Loan'),
        ('business_loan', 'Business Loan'),
    ], string='Loan Type', required=True)
    
    base_rate = fields.Float('Base Rate (%)', required=True)
    risk_premium = fields.Float('Risk Premium (%)', default=0)
    collateral_discount = fields.Float('Collateral Discount (%)', default=0)
    effective_rate = fields.Float('Effective Rate (%)', compute='_compute_effective_rate', store=True)
    
    tenure_range = fields.Char('Tenure Range (months)', help='e.g., 12-60')
    
    effective_date = fields.Date('Effective Date', default=fields.Date.today)
    
    @api.depends('base_rate', 'risk_premium', 'collateral_discount')
    def _compute_effective_rate(self):
        for record in self:
            record.effective_rate = record.base_rate + record.risk_premium - record.collateral_discount


class LoanEMICalculator(models.Model):
    _name = 'loan.emi.calculator'
    _description = 'EMI Calculator History'

    principal_amount = fields.Float('Principal Amount', required=True)
    rate_of_interest = fields.Float('Rate of Interest (%)', required=True)
    tenure_months = fields.Integer('Tenure (Months)', required=True)
    
    calculated_emi = fields.Float('Calculated EMI', compute='_compute_emi_details', store=True)
    total_interest = fields.Float('Total Interest', compute='_compute_emi_details', store=True)
    total_amount_payable = fields.Float('Total Amount Payable', compute='_compute_emi_details', store=True)
    
    calculation_date = fields.Date('Calculation Date', default=fields.Date.today)
    
    @api.depends('principal_amount', 'rate_of_interest', 'tenure_months')
    def _compute_emi_details(self):
        for record in self:
            if record.principal_amount and record.rate_of_interest and record.tenure_months:
                principal = record.principal_amount
                rate = record.rate_of_interest / 12 / 100
                n = record.tenure_months
                
                if rate > 0:
                    emi = (principal * rate * (1 + rate) ** n) / ((1 + rate) ** n - 1)
                else:
                    emi = principal / n
                
                record.calculated_emi = emi
                record.total_interest = (emi * n) - principal
                record.total_amount_payable = principal + record.total_interest
            else:
                record.calculated_emi = 0
                record.total_interest = 0
                record.total_amount_payable = 0


class GoldRateHistory(models.Model):
    _name = 'gold.rate.history'
    _description = 'Gold Rate History'
    _order = 'rate_date desc'

    rate_date = fields.Date('Rate Date', required=True)
    rate_per_gram = fields.Float('Rate per Gram (Rs.)', required=True)
    
    # Purity-wise rates
    rate_22k = fields.Float('22K Rate (Rs.)')
    rate_24k = fields.Float('24K Rate (Rs.)')
    
    # Market information
    market_source = fields.Char('Market Source')
    city = fields.Char('City/Region')
    
    notes = fields.Text('Notes')
    
    _sql_constraints = [
        ('unique_date_city', 'unique(rate_date, city)', 'Gold rate for a city on a date must be unique!')
    ]


class LoanApplicationTemplate(models.Model):
    _name = 'loan.application.template'
    _description = 'Loan Application Template'

    name = fields.Char('Template Name', required=True)
    description = fields.Text('Description')
    loan_type = fields.Selection([
        ('two_wheeler', 'Two Wheeler'),
        ('three_wheeler', 'Three Wheeler'),
        ('gold_loan', 'Gold Loan'),
        ('business_loan', 'Business Loan'),
    ], string='Loan Type', required=True)
    
    # Template content
    form_html = fields.Html('Form HTML')
    required_documents = fields.Text('Required Documents')
    
    # Default values
    default_interest_rate = fields.Float('Default Interest Rate')
    default_tenure = fields.Integer('Default Tenure (Months)')
    default_max_loan_amount = fields.Float('Default Max Loan Amount')
    
    is_active = fields.Boolean('Is Active', default=True)
    
    created_by = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user)
    created_date = fields.Date('Created Date', default=fields.Date.today)


class DocumentTemplate(models.Model):
    _name = 'document.template'
    _description = 'Document Template for Loans'

    name = fields.Char('Template Name', required=True)
    document_type = fields.Selection([
        ('application', 'Application Form'),
        ('agreement', 'Loan Agreement'),
        ('schedule', 'Repayment Schedule'),
        ('letter', 'Approval Letter'),
        ('certificate', 'Gold Certificate'),
    ], string='Document Type', required=True)
    
    loan_type = fields.Selection([
        ('two_wheeler', 'Two Wheeler'),
        ('three_wheeler', 'Three Wheeler'),
        ('gold_loan', 'Gold Loan'),
        ('business_loan', 'Business Loan'),
    ], string='Applicable for Loan Type')
    
    template_content = fields.Html('Template Content')
    
    is_active = fields.Boolean('Is Active', default=True)
