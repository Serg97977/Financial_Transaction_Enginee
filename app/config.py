"""
IN THIS PART OF CODE WE ARE CONNECTING TO OUR DATABASE
"""

import mysql.connector

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    password='semg9688'

)
