# -*- coding: utf-8 -*-

from odoo import models, fields, api


class TwoWheelerLoan(models.Model):
    _name = 'two.wheeler.loan'
    _description = 'Two Wheeler Loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Reference to Business Loan
    business_loan_id = fields.Many2one('business.loan', string='Business Loan', ondelete='cascade')
    
    # Vehicle Details
    vehicle_type = fields.Selection([
        ('motorcycle', 'Motorcycle'),
        ('scooter', 'Scooter'),
        ('moped', 'Moped'),
    ], string='Vehicle Type', required=True)
    
    vehicle_brand = fields.Char('Brand', required=True)
    vehicle_model = fields.Char('Model', required=True)
    vehicle_year = fields.Integer('Year of Manufacture')
    engine_number = fields.Char('Engine Number')
    chassis_number = fields.Char('Chassis Number', required=True)
    vehicle_color = fields.Char('Color')
    
    # Pricing
    vehicle_ex_showroom_price = fields.Float('Ex-Showroom Price')
    vehicle_on_road_price = fields.Float('On-Road Price', required=True)
    vehicle_insurance = fields.Float('Insurance Amount')
    vehicle_total_value = fields.Float('Total Value', compute='_compute_vehicle_total', store=True)
    
    # Loan Details
    down_payment = fields.Float('Down Payment')
    loan_amount = fields.Float('Loan Amount', compute='_compute_loan_amount', store=True)
    interest_rate = fields.Float('Interest Rate (%)')
    tenure_months = fields.Integer('Tenure (Months)')
    
    # EMI Details
    emi_amount = fields.Float('EMI Amount', compute='_compute_emi', store=True)
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ], string='Status', default='draft')
    
    # Documentation
    rc_document = fields.Binary('RC Document')
    insurance_document = fields.Binary('Insurance Document')
    pollution_document = fields.Binary('Pollution Certificate')
    
    # Computed Fields
    @api.depends('vehicle_on_road_price', 'vehicle_insurance')
    def _compute_vehicle_total(self):
        for record in self:
            record.vehicle_total_value = record.vehicle_on_road_price + (record.vehicle_insurance or 0)
    
    @api.depends('vehicle_total_value', 'down_payment')
    def _compute_loan_amount(self):
        for record in self:
            record.loan_amount = record.vehicle_total_value - (record.down_payment or 0)
    
    @api.depends('loan_amount', 'interest_rate', 'tenure_months')
    def _compute_emi(self):
        for record in self:
            if record.loan_amount and record.interest_rate and record.tenure_months:
                principal = record.loan_amount
                rate = record.interest_rate / 12 / 100
                n = record.tenure_months
                
                if rate > 0:
                    emi = (principal * rate * (1 + rate) ** n) / ((1 + rate) ** n - 1)
                else:
                    emi = principal / n
                
                record.emi_amount = emi
            else:
                record.emi_amount = 0


class ThreeWheelerLoan(models.Model):
    _name = 'three.wheeler.loan'
    _description = 'Three Wheeler Loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Reference to Business Loan
    business_loan_id = fields.Many2one('business.loan', string='Business Loan', ondelete='cascade')
    
    # Vehicle Details
    vehicle_type = fields.Selection([
        ('auto_rickshaw', 'Auto Rickshaw'),
        ('tuk_tuk', 'Tuk Tuk'),
        ('cargo', 'Cargo Auto'),
    ], string='Vehicle Type', required=True)
    
    vehicle_brand = fields.Char('Brand', required=True)
    vehicle_model = fields.Char('Model', required=True)
    vehicle_year = fields.Integer('Year of Manufacture')
    engine_number = fields.Char('Engine Number')
    chassis_number = fields.Char('Chassis Number', required=True)
    
    # Seating Capacity
    seating_capacity = fields.Integer('Seating Capacity')
    cargo_capacity = fields.Float('Cargo Capacity (kg)')
    
    # Pricing
    vehicle_ex_showroom_price = fields.Float('Ex-Showroom Price')
    vehicle_on_road_price = fields.Float('On-Road Price', required=True)
    vehicle_insurance = fields.Float('Insurance Amount')
    vehicle_total_value = fields.Float('Total Value', compute='_compute_vehicle_total', store=True)
    
    # Loan Details
    down_payment = fields.Float('Down Payment')
    loan_amount = fields.Float('Loan Amount', compute='_compute_loan_amount', store=True)
    interest_rate = fields.Float('Interest Rate (%)')
    tenure_months = fields.Integer('Tenure (Months)')
    
    # EMI Details
    emi_amount = fields.Float('EMI Amount', compute='_compute_emi', store=True)
    
    # Commercial Details
    registration_type = fields.Selection([
        ('personal', 'Personal'),
        ('commercial', 'Commercial'),
    ], string='Registration Type')
    
    permit_number = fields.Char('Permit Number')
    fitness_certificate = fields.Char('Fitness Certificate Number')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ], string='Status', default='draft')
    
    # Computed Fields
    @api.depends('vehicle_on_road_price', 'vehicle_insurance')
    def _compute_vehicle_total(self):
        for record in self:
            record.vehicle_total_value = record.vehicle_on_road_price + (record.vehicle_insurance or 0)
    
    @api.depends('vehicle_total_value', 'down_payment')
    def _compute_loan_amount(self):
        for record in self:
            record.loan_amount = record.vehicle_total_value - (record.down_payment or 0)
    
    @api.depends('loan_amount', 'interest_rate', 'tenure_months')
    def _compute_emi(self):
        for record in self:
            if record.loan_amount and record.interest_rate and record.tenure_months:
                principal = record.loan_amount
                rate = record.interest_rate / 12 / 100
                n = record.tenure_months
                
                if rate > 0:
                    emi = (principal * rate * (1 + rate) ** n) / ((1 + rate) ** n - 1)
                else:
                    emi = principal / n
                
                record.emi_amount = emi
            else:
                record.emi_amount = 0
