import sqlite3
import pandas
import logging

# Configure logger
logging.basicConfig(
    filename="error_log.txt",
    level=logging.ERROR,
    format="%(message)s"
)

# Dict for type conversion
csv_to_sql_dict = {
    "int64": "INTEGER",
    "float64": "REAL",
    "object": "TEXT",
}

con = sqlite3.connect("cars_db")
cur = con.cursor()

def get_sql_schema(table_name):
    cur.execute(f"PRAGMA table_info({table_name})")
    return cur.fetchall()

def compare_schemas(sql_schema, dataframe):
    sql_cols = [col[1] for col in sql_schema]
    dataframe_cols = dataframe.columns.tolist()
    # SQL schema is expected to have an auto-incrementing ID field, CSV schema is not, so we account for this
    return sql_cols[1:] == dataframe_cols

def create_sql_table_from_csv(dataframe, table_name):
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

if __name__ == "__main__":
    try:    
        table_name = "new_cars_1"
        csv_name = "cars.csv"
        # Read in CSV data and get SQL schema
        dataframe = pandas.read_csv(csv_name)
        sql_schema = get_sql_schema(table_name)
        if sql_schema:
            if compare_schemas(sql_schema, dataframe):
                print("Schemas are the same, appending data...")
                create_sql_table_from_csv(dataframe, table_name)
            else:
                # Prompt user for options
                print("Schemas are not the same. You can choose to overwrite the table with the new schema, choose another table name to use, or skip the process and do nothing.")
                choice = input("[O]verwrite, [R]ename, [S]kip: ").lower()
                if choice == 'o':
                    print("Overwriting table...")
                    con.execute(f'DROP TABLE IF EXISTS "{table_name}"')
                    create_sql_table_from_csv(dataframe, table_name)
                elif choice == 'r':
                    print("Creating new table...")
                    new_name = input("Enter a new name for the table: ").strip()
                    create_sql_table_from_csv(dataframe, new_name)
                else:
                    print("Skipping...")
        else:
            # Schema does not exist and a new table can be created without conflict
            create_sql_table_from_csv(dataframe, table_name)
    except Exception as e:
        logging.error("Error: ", exc_info=True)
        print("An error has occured, check error_log.txt for details.")
    
    # Close the database
    con.close()