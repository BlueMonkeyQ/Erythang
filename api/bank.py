import json
from pathlib import Path
from datetime import datetime
from supabaseDB import Supabase

def getBudgetPresets():
    try:
        with open(Path(r"data/bank/presets.json"), "r") as file:
            data = json.load(file)
            return data
    except Exception as e:
        print(e)
        return False

def getTransactionTypes():
    try:
        with open(Path(r"data/bank/transaction_types.json"), "r") as file:
            data = json.load(file)
            return data
    except Exception as e:
        print(e)
        return False
