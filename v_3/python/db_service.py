# -*- coding: utf-8 -*-
"""
Created on Fri Jan  4 15:28:47 2019

@author: ClementLefevre
"""
import sqlite3
from config import LIVEFYRE_DB




def drop_table(table_name):
     
    connection  = sqlite3.connect(LIVEFYRE_DB)
    cursor      = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print(cursor.fetchall())
    
    dropTableStatement = "DROP TABLE \"{0}\"".format(table_name)
    print(dropTableStatement)
    cursor.execute(dropTableStatement)
    cursor.execute("vacuum")
    connection.close()   