import sqlite3

# Create database and connection to it (con); & create cursor to interact with database.
con = sqlite3.connect('TestDatabase.db')
cursor = con.cursor()
print('DB initialized\n')

# Check version of SQLite & execute/retrieve query
query = 'SELECT sqlite_version();'
cursor.execute(query)
result = cursor.fetchall()
print('The SQLite version is ' + str(result))

# Write query to create table and store to value (creator_query)
creator_query = """
    CREATE TABLE IF NOT EXISTS Ingredient_Table (
        Name STR UNIQUE PRIMARY KEY,
        Measure STR NOT NULL, 
        Count INT DEFAULT 0,
        Cost STR DEFAULT 'waiting'
    );
"""
cursor.execute(creator_query)
print('\nThe Ingredients Table has been created.\n')

# Define a static 'test' entry to the table with specified values
# Execute actually 'performs' the change we define
cursor.execute(
    'INSERT OR IGNORE INTO Ingredient_Table (Name, Measure, Count, Cost) VALUES ("Potato", "Lb", 20, 1.02)')
# Commit 'solidifies' the change(s) we define'
con.commit()
print('Inserted "Test" Data Entry:')
cursor.execute('SELECT * FROM Ingredient_Table')
# Iterate through & print all existing rows
for row in cursor.fetchall():
    print(row)


# Create a function which takes input from the user to populate ingredient entries
def entry_function(curse, connect):
    while True:
        name = input('Ingredient Name: ')
        measure = str(input('What unit measure? (Lb, Oz, Qt, etc.): '))
        count = int(input('Currently in stock: '))
        cost = float(input('Dollar cost per unit: '))

        # The action of storing user values 'exists as' variable (enter)
        enter = """INSERT INTO Ingredient_Table (Name, Measure, Count, Cost)
        VALUES (?, ?, ?, ?);
        """
        # Execute actually 'performs' the change we define
        curse.execute(enter, (name, measure, count, cost))
        # Commit 'solidifies' the change(s) we define'
        connect.commit()
        print('Ingredient added!')
        # Create a 'check' variable to ask user for more entries
        # If not some variation of 'yes', kill the while true loop
        repeat = input('Add another item to table? (Y/N): ').strip().upper()
        if repeat not in ('Y', "YES"):
            # Iterate through & print all existing rows
            print('Current Entries:\n')
            curse.execute('SELECT * FROM Ingredient_Table')
            for funcrow in curse.fetchall():
                print(funcrow)
            break

# To remove an ingredient
def remove_function(curse, connect):
    # selects what you want to delete as a placeholder
    whatdelete = input('\nEnter the **Name** of ingredient to remove: ').strip()
    # deletes the placeholder
    actualdelete = "DELETE FROM Ingredient_Table Where Name = ?;"
    curse.execute(actualdelete, (whatdelete,))
    connect.commit()
    # if placeholder exists in table, deletes it
    if curse.rowcount > 0:
        print(whatdelete + ' has been successfully removed.')
    else:
        print("Could not find an ingredient named '{whatdelete}'. No rows were removed.")

    print('\nCurrent functions:')
    curse.execute('SELECT * FROM Ingredient_Table')
    for funcrow in curse.fetchall():
        print(funcrow)

entry_function(cursor, con)
remove_function(curse, connect)

# Close the cursor and connection to DB
input("Hit enter to exit:")
cursor.close()
con.close()
print("\nDB Connection Closed")



