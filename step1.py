import sqlite3
import pandas

con = sqlite3.connect("cars_db")
dataframe = pandas.read_csv("cars.csv")
dataframe.to_sql("cars", con, if_exists="append", index=False)
