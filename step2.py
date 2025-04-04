import sqlite3
import pandas

# Dict for type conversion
csv_to_sql_dict = {
    "int64": "INTEGER",
    "float64": "REAL",
    "object": "TEXT",
}

con = sqlite3.connect("cars_db")
cur = con.cursor()

def create_sql_table_from_csv(csv_name, table_name):
    # Read in CSV data
    dataframe = pandas.read_csv(csv_name)

    # Create a list of the different columns along with their corresponding data types
    columns = []
    columns.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
    for column, csv_type in dataframe.dtypes.items():
        sql_type = csv_to_sql_dict[str(csv_type)]
        columns.append(f'"{column}" {sql_type}')

    # ChatGPT helped make this create statement, only create the table if it doesn't already exist
    create_statement = f'CREATE TABLE IF NOT EXISTS {table_name} (\n  ' + ",\n  ".join(columns) + "\n);"

    # Create the table and push the CSV data to it
    cur.execute(create_statement)
    con.commit()
    dataframe.to_sql(table_name, con, if_exists="append", index=False)

    # Close the database
    con.close()


if __name__ == "__main__":
    create_sql_table_from_csv("cars.csv", "new_cars_1")