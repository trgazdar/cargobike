# Copyright 2018 Giacomo Grasso <giacomo.grasso.82@gmail.com>
# Odoo Proprietary License v1.0 see LICENSE file

import logging
from psycopg2 import sql


def pre_init_hook(cr):
    """Create eventually columns before module installations."""
    cr.execute(  # pylint: disable=E8103
        sql.SQL("""
        ALTER TABLE account_move_line ADD COLUMN treasury_date date;
        ALTER TABLE account_move_line ADD COLUMN treasury_planning boolean;
        ALTER TABLE account_move_line ADD COLUMN forecast_id INT;
        
        ALTER TABLE account_bank_statement_line ADD COLUMN statement_fp boolean;
        ALTER TABLE account_bank_statement_line ADD COLUMN treasury_forecast_id INT;
        
        UPDATE account_move_line SET 
            treasury_date = date_maturity,
            treasury_planning = False,
            forecast_id = NULL
            ;
        
        UPDATE account_bank_statement_line SET
            statement_fp = False,
            treasury_forecast_id = NULL    
            ;
            
        """)
    )
