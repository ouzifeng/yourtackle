import pandas as pd
import numpy as np
import mysql.connector
import re

# Define database connection details
db_config = {
    "host": "sql8.freemysqlhosting.net",
    "user": "sql8619007",
    "password": "vV9L8kKxxh",
    "database": "sql8619007",
}

# File path
file_path = "output.csv"

# Define column mappings
column_mappings = {
    "id": "ID",
    "gtin": "GTIN",
    "title": "Title",
    "price": "Price",
    "image_link": "Image",
    "mpn": "MPN",
}

# Read the CSV file and select specific columns
data = pd.read_csv(file_path, usecols=column_mappings.keys())

# Rename the columns
data.rename(columns=column_mappings, inplace=True)

# Strip non-numeric characters from the 'Price' column
data["Price"] = data["Price"].str.extract(r"(\d+\.\d+)", expand=False)
data["Price"] = pd.to_numeric(data["Price"], errors="coerce")

# Handle missing values
data.replace({np.nan: None}, inplace=True)

# Establish database connection
cnx = mysql.connector.connect(**db_config)
cursor = cnx.cursor()

# Clear the existing table
clear_table_query = "TRUNCATE TABLE tackle"
cursor.execute(clear_table_query)

# Insert the data into the table
insert_query = "INSERT INTO tackle (ID, GTIN, Title, Price, Image, MPN) VALUES (%s, %s, %s, %s, %s, %s)"
data_values = [tuple(row) for row in data[column_mappings.values()].values]
cursor.executemany(insert_query, data_values)

# Commit the changes
cnx.commit()

# Close the cursor and database connection
cursor.close()
cnx.close()
