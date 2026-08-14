from typing import Dict, Any
from db import get_db

class StatsRepository:
    #Handles MongoDB aggregations for dashboard summary metrics.

    @staticmethod
    def get_dashboard_stats() -> Dict[str, Any]:
        #Aggregates real-time metrics from customers, accounts, and transactions collections.
        try:
            db = get_db()
            
            # Count total customers
            total_customers = db["customers"].count_documents({}) if "customers" in db.list_collection_names() else 0
            
            # Safe collection checks comparing with None explicitly
            accounts_col = db["accounts"] if "accounts" in db.list_collection_names() else None
            active_accounts = accounts_col.count_documents({"status": "Active"}) if accounts_col is not None else 0
            closed_accounts = accounts_col.count_documents({"status": "Closed"}) if accounts_col is not None else 0
            
            # Calculate total combined bank balance across active accounts
            total_balance = 0.0
            if accounts_col is not None:
                pipeline = [
                    {"$match": {"status": "Active"}},
                    {"$group": {"_id": None, "total_balance": {"$sum": "$balance"}}}
                ]
                balance_result = list(accounts_col.aggregate(pipeline))
                if balance_result:
                    total_balance = balance_result[0].get("total_balance", 0.0)

            trans_col = db["transactions"] if "transactions" in db.list_collection_names() else None
            total_transactions = trans_col.count_documents({}) if trans_col is not None else 0
            failed_transactions = trans_col.count_documents({"status": "Failed"}) if trans_col is not None else 0

            return {
                "Customers": str(total_customers),
                "Active Accounts": str(active_accounts),
                "Closed Accounts": str(closed_accounts),
                "Transactions": str(total_transactions),
                "Bank Balance": f"₹{total_balance:,.2f}",
                "Failed Transactions": str(failed_transactions),
            }
        except Exception as e:
            print(f"[StatsRepository Error - get_dashboard_stats]: {e}")
            return {
                "Customers": "0",
                "Active Accounts": "0",
                "Closed Accounts": "0",
                "Transactions": "0",
                "Bank Balance": "₹0.00",
                "Failed Transactions": "0",
            }