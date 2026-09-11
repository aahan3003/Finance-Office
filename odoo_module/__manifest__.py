# -*- coding: utf-8 -*-
{
    'name': 'Finance Office - Business Loan Management System',
    'version': '1.0.0',
    'category': 'Accounting/Finance',
    'summary': 'Complete Business Loan Management for Two/Three Wheelers, Gold Loans & Business Loans',
    'description': """
        Finance Office Business Loan Module
        
        Complete Features:
        ==================
        
        1. TWO WHEELER FINANCING
        - Motorcycle & Scooter loan management
        - Vehicle documentation tracking
        - EMI calculation and repayment schedules
        - Insurance integration
        
        2. THREE WHEELER FINANCING  
        - Auto-rickshaw & Cargo auto financing
        - Commercial registration support
        - Permit tracking
        - Fitness certificate management
        
        3. GOLD LOAN SERVICES
        - Gold purity assessment (22K, 24K)
        - Real-time rate tracking
        - Loan-to-value calculations
        - Secure storage management
        - Redemption workflow
        
        4. BUSINESS LOAN SYSTEM
        - Real-time financial data analysis
        - Automated credit scoring
        - Dynamic interest rate calculation
        - Inventory-based lending
        - Accounts receivable financing
        - Vendor financing integration
        
        5. COMMON FEATURES
        - Automated EMI calculations
        - Comprehensive repayment schedules
        - Document management system
        - Multi-level approval workflow
        - Real-time status tracking
        - Detailed analytics & reports
        
        INSTALLATION
        ============
        1. Copy this module to your Odoo addons directory
        2. Update the module list
        3. Install from Apps menu
        4. Configure loan types and interest rates
    """,
    'author': 'Aahan Finance Solutions',
    'website': 'https://github.com/aahan3003/Finance-Office',
    'license': 'LGPL-3',
    
    'depends': [
        'base',
        'account',
        'sale',
        'purchase',
        'stock',
        'mail',
        'web',
    ],
    
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Data
        'data/loan_sequence.xml',
        'data/interest_rates.xml',
        
        # Views
        'views/business_loan_views.xml',
        'views/two_wheeler_views.xml',
        'views/three_wheeler_views.xml',
        'views/gold_loan_views.xml',
        'views/loan_utilities_views.xml',
        'views/loan_document_views.xml',
        'views/repayment_schedule_views.xml',
        
        # Menus
        'views/loan_menu.xml',
        
        # Reports
        'reports/loan_report.xml',
        'reports/repayment_report.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
    
    'external_dependencies': {
        'python': ['requests', 'pandas', 'numpy'],
    },
    
    'images': ['static/description/icon.png'],
}
