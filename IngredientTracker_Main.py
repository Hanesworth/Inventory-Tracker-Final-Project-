import sqlite3

# DB init & table creation

con = sqlite3.connect('TestDatabase.db')
cursor = con.cursor()
print('DB initialized\n')

cursor.execute('SELECT sqlite_version();')
result = cursor.fetchall()
print('The SQLite version is ' + str(result))

# ingredient table creation
ingredientQuery = """
    CREATE TABLE IF NOT EXISTS Ingredient_Table (
        Name STR UNIQUE PRIMARY KEY,
        Measure STR NOT NULL, 
        Count REAL DEFAULT 0,
        Cost REAL DEFAULT 0.00
    );
"""
cursor.execute(ingredientQuery)
print('\n-The Ingredients Table has been created-')


# recipe table creation
recipeTableQuery = """
    CREATE TABLE IF NOT EXISTS Recipe_Table (
        RecipeID INTEGER PRIMARY KEY AUTOINCREMENT,
        RecipeName STR UNIQUE,
        Instructions STR
    );
"""
cursor.execute(recipeTableQuery)
print('-The Recipe Table has been created-')

recipeIngredientsQuery = """
    CREATE TABLE IF NOT EXISTS Recipe_Ingredients_Table (
        RecipeID INTEGER,
        IngredientName STR,
        QuantityNeeded REAL NOT NULL,
        Measure STR NOT NULL,
        PRIMARY KEY (RecipeID, IngredientName),
        FOREIGN KEY (RecipeID) REFERENCES Recipe_Table(RecipeID) ON DELETE CASCADE,
        FOREIGN KEY (IngredientName) REFERENCES Ingredient_Table(Name) ON DELETE CASCADE
    );
"""
cursor.execute(recipeIngredientsQuery)
print('-The Recipe Ingredients Table has been created-\n')

cursor.execute(
    'INSERT OR IGNORE INTO Ingredient_Table (Name, Measure, Count, Cost) VALUES ("Potato", "lb", 20.0, 1.02)'
)
con.commit()
print('-Inserted "Test" Data Entry-')
cursor.execute('SELECT * FROM Ingredient_Table')
for row in cursor.fetchall():
    print(row)


# Ingredient addition function
def entryFunction(cursor, connect):
    print("\n-Add/Update Ingredient Inventory-")

    while True:
        try:
            name = input('Ingredient Name: ').strip()
            measure = input('What unit measure? (lb, oz, qt, etc.): ').strip()
            count = float(input('Currently in stock (Count): '))
            cost = float(input('Dollar cost per unit: '))
        except ValueError:
            print("Invalid input for Count or Cost. Please enter a number.")
            continue
        # The action of storing user values 'exists as' variable (enter)
        insertQuery = """
            INSERT OR REPLACE INTO Ingredient_Table (Name, Measure, Count, Cost)
            VALUES (?, ?, ?, ?);
        """
        # Execute actually 'performs' the change we define
        cursor.execute(insertQuery, (name, measure, count, cost))
        # Commit 'solidifies' the change(s) we define'
        connect.commit()
        print(name + " added/updated!")
        # Iterate through & print all existing rows
        while True:
            repeat = input('Add another item? (Y/N): ').strip().upper()
            if repeat in ('Y', 'YES'):
                break
            elif repeat in ('N', 'NO'):
                print('\n-Current Inventory-')
                cursor.execute('SELECT * FROM Ingredient_Table')
                for funcrow in cursor.fetchall():
                    print(funcrow)
                return
            else:
                print("Invalid choice. Enter Y or N.")


# Ingredient removal function
def removeFunction(cursor, connect):
    print("\n-Remove Ingredient from Inventory-")
    # selects what you want to delete as a placeholder
    whatDelete = input('Ingredient name to remove: ').strip()
    # deletes the placeholder
    deleteQuery = "DELETE FROM Ingredient_Table WHERE Name = ?;"
    cursor.execute(deleteQuery, (whatDelete,))
    connect.commit()
    # if placeholder exists in table, deletes it
    if cursor.rowcount > 0:
        print(whatDelete + " has been removed.")
    else:
        print("No ingredient named '" + whatDelete + "' found.")

    print('\n-Current Inventory-')
    cursor.execute('SELECT * FROM Ingredient_Table')
    for funcrow in cursor.fetchall():
        print(funcrow)


# Recipe Addition function
def addRecipeFunction(cursor, connect):
    print("\n-Add New Recipe-")
    recipeName = input('Recipe name: ').strip()
    instructions = input('Cooking instructions: ').strip()

    try:
        cursor.execute(
            "INSERT INTO Recipe_Table (RecipeName, Instructions) VALUES (?, ?);",
            (recipeName, instructions)
        )
        recipeId = cursor.lastrowid
        print("Recipe '" + recipeName + "' added (ID: " + str(recipeId) + ").")
    except sqlite3.IntegrityError:
        print("A recipe named '" + recipeName + "' already exists.")
        return

    while True:
        ingName = input('\nIngredient for recipe: ').strip()

        cursor.execute("SELECT Measure, Count FROM Ingredient_Table WHERE Name = ?;", (ingName,))
        ingredientInfo = cursor.fetchone()

        if ingredientInfo is None:
            print("Ingredient '" + ingName + "' not found in inventory.")
            continue

        ingredientMeasure = ingredientInfo[0]
        currentStock = ingredientInfo[1]
    # Throw a warning if the user is out of said item
        if currentStock <= 0:
            print("WARNING: You currently have " + str(currentStock) + " " +
                  ingredientMeasure + " of " + ingName)

        try:
            quantity = float(input("Quantity needed (" + ingredientMeasure + "): "))
        except ValueError:
            print("Invalid number.")
            continue

        insertLink = """
        INSERT INTO Recipe_Ingredients_Table (RecipeID, IngredientName, QuantityNeeded, Measure)
        VALUES (?, ?, ?, ?);
        """
        cursor.execute(insertLink, (recipeId, ingName, quantity, ingredientMeasure))
        connect.commit()

        print(ingName + " (" + str(quantity) + " " + ingredientMeasure +
              ") added to " + recipeName)

        while True:
            repeat = input('Add another ingredient? (Y/N): ').strip().upper()
            if repeat in ('Y', 'YES'):
                break
            elif repeat in ('N', 'NO'):
                print("\nRecipe '" + recipeName + "' created successfully!")
                return
            else:
                print("Invalid choice. Enter Y or N.")


# View List recipe(s)
def showRecipes(cursor):
    print("\n-Current Recipes-")
    cursor.execute('SELECT * FROM Recipe_Table')
    recipes = cursor.fetchall()
    #just to remind the user that they added no recipes
    if not recipes:
        print("No recipes found.")
        return
    
    for recipe in recipes:
        recipeId, name, instructions = recipe
        print("\nID: " + str(recipeId) + " | Name: " + name)
        print("Instructions:", instructions)

        print("-Ingredients-")
        cursor.execute("""
            SELECT IngredientName, QuantityNeeded, Measure
            FROM Recipe_Ingredients_Table
            WHERE RecipeID = ?
        """, (recipeId,))
        for ingName, qty, measure in cursor.fetchall():
            print("  - " + str(qty) + " " + measure + " of " + ingName)


# Recipe removal function
def deleteRecipeFunction(cursor, connect):
    print("\n-Delete Recipe-")
    cursor.execute('SELECT RecipeID, RecipeName FROM Recipe_Table')
    recipes = cursor.fetchall()

    if not recipes:
        print("No recipes to delete.")
        return

    for recipeId, name in recipes:
        print("ID: " + str(recipeId) + ", Name: " + name)

    whatDelete = input('Recipe name to delete: ').strip()

    cursor.execute("DELETE FROM Recipe_Table WHERE RecipeName = ?;", (whatDelete,))
    connect.commit()

    if cursor.rowcount > 0:
        print("Recipe '" + whatDelete + "' has been removed.")
    else:
        print("No recipe named '" + whatDelete + "' found.")

    print("\n-Remaining Recipes-")
    cursor.execute('SELECT RecipeID, RecipeName FROM Recipe_Table')
    for row in cursor.fetchall():
        print("ID: " + str(row[0]) + ", Name: " + row[1])


## 'Main menu' loop
while True:
    print("\n=== MAIN MENU ===")
    print("I - Ingredient Menu")
    print("R - Recipe Menu")
    print("X - Exit Program")

    choice = input("Choice: ").strip().upper()

    if choice == "I":
        while True:
            sub = input("\nIngredient Menu: Change (C) or Delete (D)? ").strip().upper()

            if sub == "C":
                entryFunction(cursor, con)
                break
            elif sub == "D":
                removeFunction(cursor, con)
                break
            else:
                print("Invalid choice. Enter C or D.")

    elif choice == "R":
        while True:
            sub = input("\nRecipe Menu: Add (A), View (V), Delete (D)? ").strip().upper()

            if sub == "A":
                addRecipeFunction(cursor, con)
                break
            elif sub == "V":
                showRecipes(cursor)
                break
            elif sub == "D":
                deleteRecipeFunction(cursor, con)
                break
            else:
                print("Invalid choice. Enter A, V, or D.")

    elif choice == "X":
        print("\n-Exiting Program-")
        break

    else:
        print("Invalid choice. Enter I, R, or X.")

# Kill & Close block
print("\n-Closing Program-")
input("Press Enter to exit...")
cursor.close()
con.close()
print("DB Connection Closed")

