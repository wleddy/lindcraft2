# How to import data for Lindcraft

1. Place a copy of the current live data in this directory. ('mysitedata.db')
2. Place a copy of the new (empty) data file in this directory. ('database.sqlite') 
Any data in this file will be deleted
3. In terminal, cd into the this directory and run `sqlite3 mysitedata.md`
4. enter `.read import_data.sql`

The data from the old db should now be in the new db.

Copy the new datafile to the project `instance` directory
