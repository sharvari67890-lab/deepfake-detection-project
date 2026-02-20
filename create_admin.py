# from database import create_user

# create_user("Admin", "admin@gmail.com", "admin123", is_admin=1)

# print("Admin account created!")


from database import init_db, create_user

# Create tables first
init_db()

# Then create admin
create_user("Admin", "admin@gmail.com", "admin123", is_admin=1)

print("Admin account created successfully!")
