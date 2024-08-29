from datetime import datetime
from db import supabase

def insertRecord(name:str,amount:float,date:str,_type:str,categories:list):
    try:
        supabase.from_("bank")\
        .insert({
            "name": name,
            "amount": amount,
            "date": date,
            "type": _type,
            "categories": categories,
        })\
        .execute()
    except Exception as e:
        print(e)
        return False
    
def updateRecord(id:int,name:str,amount:float,date:str,_type:str,categories:list):
    try:
        supabase.from_("bank")\
        .update({
            "name": name,
            "amount": amount,
            "date": date,
            "type": _type,
            "categories": categories,
        })\
        .eq(column='id',value=id)\
        .execute()
    except Exception as e:
        print(e)
        return False
    
def deleteRecord(id:int):
    try:
        supabase.from_("bank")\
        .delete()\
        .eq(column='id',value=id)\
        .execute()
    except Exception as e:
        print(e)
        return False
    
def getRecords():
    try:
        records = supabase.from_("bank")\
        .select("*")\
        .execute().data

        return records
    except Exception as e:
        print(e)
        return False