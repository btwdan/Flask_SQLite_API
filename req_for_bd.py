create_table_user = """CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    username TEXT,
    balance INTEGER
)
"""

insert_data = """INSERT INTO users (username, balance)
                 VALUES ('Evgeniy', 7239), 
                        ('Petr', 11300), 
                        ('Vladimir', 9860), 
                        ('Daniil', 14999), 
                        ('Artur', 5001)
                """

API_KEY = '44cbcb17caa7313b70cd2350ab4e87c6'