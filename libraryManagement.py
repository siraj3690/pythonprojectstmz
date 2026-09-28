import sqlite3
import getpass
from datetime import datetime, timedelta

conn =sqlite3.connect("libraryManagement.db")
cursor =conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS user(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(30) UNIQUE NOT NULL,
                    password TEXT,
                    role TEXT NOT NULL
                )
            """)

cursor.execute("""CREATE TABLE IF NOT EXISTS author(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aname VARCHAR(30) NOT NULL
                )   
            """)

cursor.execute("""CREATE TABLE IF NOT EXISTS books(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    a_id INTEGER,
                    isbn UNIQUE,
                    totalbook INTEGER NOT NULL,
                    available INTEGER NOT NULL,
                    FOREIGN KEY (a_id) REFERENCES author(id)
                )
            """)

cursor.execute("""CREATE TABLE IF NOT EXISTS transactions(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    book_id INTEGER NOT NULL,
                    issue_date TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    returned TEXT,
                    status TEXT NOT NULL,
                    FOREIGN KEY (book_id) REFERENCES books(id),
                    FOREIGN KEY (user_id) REFERENCES user(id)
                    )
            """)
conn.close()


#FUNCTION TO REGISTER USER
def adduser():
    conn=sqlite3.connect("library.db")
    cursor=conn.cursor()
    try:
        uname=input("enter the user name: ").lower()
        role=input("enter the user role like(admin/member): ").lower()
        while True:
            pas=getpass.getpass("enter the password: ")
            pas1=getpass.getpass("re-enter the password: ")
            if pas == pas1:
                cursor.execute("""
                            INSERT INTO user(username,password,role)
                            VALUES (?,?,?)""",(uname,pas,role)
                            )
                conn.commit()
                break
            else:
                print("password doesn't matched re-enter the password")
        print("user registered")
    except sqlite3.IntegrityError:
        print("username already exists....")
    except sqlite3.Error as error:
        print(f"user registration failed: {error}")
    finally:
        conn.close()

def login():  #FUCTION USED TO LOGIN USER BY VALIDATING THEIR USERNAME AND PASSWORD
    conn=sqlite3.connect("library.db")
    try:
        cursor=conn.cursor()
        uname=input("enter user name:- ").lower()
        pas=getpass.getpass("enter the password: ")
        cursor.execute("""SELECT id,role FROM user WHERE username=? AND password=?""",(uname,pas))
        user = cursor.fetchone()
        if user:
            print("logged in successfully")
            return user
        print("incorrect username or password!..try again")
    except sqlite3.Error as error:
        print(f"login failed: {error}")
    finally:
        conn.close()

#AUTHOR RELATED FUCTIONS

def add_author( ):
    conn=sqlite3.connect("library.db")
    cursor=conn.cursor()
    author_name=input("enter the author name: ")
    cursor.execute("""INSERT INTO author(aname) VALUES (?)""",(author_name,))
    conn.commit()
    print("Author added successfully")
    conn.close()

def view_author():
    conn=sqlite3.connect("library.db")
    cursor=conn.cursor()
    cursor.execute("""SELECT * FROM author""")
    author=cursor.fetchall()
    if author:
        print("author founded.....")
        for i in author:
            print(f"author_id:{i[0]}\tauthor_name:{i[1]}")
    else:
        print("author not founded")
    conn.close()


def delete_author():
    conn =sqlite3.connect("library.db")
    cursor=conn.cursor()
    author_id=int(input("Enter the author id: "))
    ch=input(f"are you sure you want to delete task\nY/N").lower()
    if ch =="y":
        cursor.execute(""" DELETE FROM author WHERE id = ? """,(author_id,))
        conn.commit()
        print("author is removed....")
    else:
        print("author isn removed... ")
    conn.close()


#book related function



def add_book():
    conn=sqlite3.connect("library.db")
    cursor=conn.cursor()
    title=input("enter the book title: ")
    view_author()
    author_id=int(input("enter the author id for this book: "))
    isbn=input("enter the isbn: ")
    total=int(input("enter the total number of copies: "))
    cursor.execute("""INSERT INTO books(title,a_id,isbn,totalbook,available)
                    VALUES (?,?,?,?,?)""",(title,author_id,isbn,total,total))
    conn.commit()
    print("book added successfully")
    conn.close()

def view_book():
    conn=sqlite3.connect("library.db")
    cursor=conn.cursor()
    cursor.execute("""SELECT books.id,books.title,author.aname,books.isbn,books.totalbook,books.available
                    FROM books LEFT JOIN author ON books.a_id=author.id""")
    books=cursor.fetchall()
    if books:
        print("books founded.....")
        for i in books:
            print(f"book_id:{i[0]}\ttitle:{i[1]}\tauthor:{i[2]}\tisbn:{i[3]}\ttotal:{i[4]}\tavailable:{i[5]}")
    else:
        print("no books founded")
    conn.close()

def delete_book():
    conn=sqlite3.connect("library.db")
    cursor=conn.cursor()
    book_id=int(input("enter the book id: "))
    ch=input("are you sure you want to delete book\nY/N").lower()
    if ch =="y":
        cursor.execute("""DELETE FROM books WHERE id=?""",(book_id,))
        conn.commit()
        print("book is removed....")
    else:
        print("book is not removed...")
    conn.close()

#MEMBER RELATED FUCTIONS FOR ADMIN
 
def view_member():
    conn=sqlite3.connect("library.db")
    cursor=conn.cursor()
    cursor.execute("""SELECT id,username FROM user WHERE role='member'""")
    members=cursor.fetchall()
    if members:
        print("members founded.....")
        for i in members:
            print(f"member_id:{i[0]}\tusername:{i[1]}")
    else:
        print("no members founded")
    conn.close()
 
 
def delete_member():
    conn=sqlite3.connect("library.db")
    cursor=conn.cursor()
    member_id=int(input("enter the member id: "))
    ch=input("are you sure you want to delete member\nY/N").lower()
    if ch =="y":
        cursor.execute("""DELETE FROM user WHERE id=? AND role='member'""",(member_id,))
        conn.commit()
        print("member is removed....")
    else:
        print("member isn removed...")
    conn.close()
 
#TRANSACTION RELATED FUCTIONS


def view_transactions():
    conn=sqlite3.connect("library.db")
    cursor=conn.cursor()
    cursor.execute("""SELECT transactions.id,user.username,books.title,transactions.issue_date,
                    transactions.due_date,transactions.returned,transactions.status
                    FROM transactions
                    JOIN user ON transactions.user_id=user.id
                    JOIN books ON transactions.book_id=books.id""")
    trans=cursor.fetchall()
    if trans:
        print("transactions founded.....")
        for i in trans:
            print(f"trans_id:{i[0]}\tuser:{i[1]}\tbook:{i[2]}\tissue_date:{i[3]}\tdue_date:{i[4]}\treturned:{i[5]}\tstatus:{i[6]}")
    else:
        print("no transactions founded")
    conn.close()



def view_overdue_books():
    conn=sqlite3.connect("library.db")
    cursor=conn.cursor()
    today=datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""SELECT transactions.id,user.username,books.title,transactions.due_date
                    FROM transactions
                    JOIN user ON transactions.user_id=user.id
                    JOIN books ON transactions.book_id=books.id
                    WHERE transactions.status='issued' AND transactions.due_date < ?""",(today,))
    overdue=cursor.fetchall()
    if overdue:
        print("overdue books founded.....")
        for i in overdue:
            print(f"trans_id:{i[0]}\tuser:{i[1]}\tbook:{i[2]}\tdue_date:{i[3]}")
    else:
        print("no overdue books founded")
    conn.close()

#MEMBER RELATED FUCTIONS

def search_book():
    conn=sqlite3.connect("library.db")
    cursor=conn.cursor()
    keyword=input("enter the leter or title related to the book to search: ")
    cursor.execute("""SELECT books.id,books.title,author.aname,books.available
                    FROM books LEFT JOIN author ON books.a_id=author.id
                    WHERE books.title LIKE ?""",('%'+keyword+'%',))
    books=cursor.fetchall()
    if books:
        print("books founded.....")
        for i in books:
            print(f"book_id:{i[0]}\ttitle:{i[1]}\tauthor:{i[2]}\tavailable:{i[3]}")
    else:
        print("no books founded")
    conn.close()
 
 
def borrow_book(user_id):
    conn=sqlite3.connect("library.db")
    cursor=conn.cursor()
    book_id=int(input("enter the book id to borrow: "))
    cursor.execute("""SELECT available FROM books WHERE id=?""",(book_id,))
    book=cursor.fetchone()
    if book and book[0] > 0:
        issue_date=input("enter the issue date (YYYY-MM-DD): ")
        due_date=input("enter the due date (YYYY-MM-DD): ")
        cursor.execute("""INSERT INTO transactions(user_id,book_id,issue_date,due_date,returned,status)
                        VALUES (?,?,?,?,?,?)""",(user_id,book_id,issue_date,due_date,None,"issued"))
        cursor.execute("""UPDATE books SET available=available-1 WHERE id=?""",(book_id,))
        conn.commit()
        print(f"book borrowed successfully, due date: {due_date}")
    else:
        print("book not available")
    conn.close()
 
 
def return_book(user_id):
    conn=sqlite3.connect("library.db")
    cursor=conn.cursor()
    book_id=int(input("enter the book id to return: "))
    cursor.execute("""SELECT id FROM transactions WHERE user_id=? AND book_id=? AND status='issued'""",
                    (user_id,book_id))
    trans=cursor.fetchone()
    if trans:
        returned_date=input("enter the return date (YYYY-MM-DD): ")
        cursor.execute("""UPDATE transactions SET returned=?,status='returned' WHERE id=?""",
                        (returned_date,trans[0]))
        cursor.execute("""UPDATE books SET available=available+1 WHERE id=?""",(book_id,))
        conn.commit()
        print("book returned successfully")
    else:
        print("no matching issued book founded for this user")
    conn.close()
 
 
def see_overdue_books(user_id):
    conn=sqlite3.connect("library.db")
    cursor=conn.cursor()
    today=datetime.now().strftime("%Y-%m-%d")
    cursor.execute("""SELECT transactions.id,books.title,transactions.due_date
                    FROM transactions
                    JOIN books ON transactions.book_id=books.id
                    WHERE transactions.user_id=? AND transactions.status='issued' AND transactions.due_date < ?""",
                    (user_id,today))
    overdue=cursor.fetchall()
    if overdue:
        print("your overdue books.....")
        for i in overdue:
            print(f"trans_id:{i[0]}\tbook:{i[1]}\tdue_date:{i[2]}")
    else:
        print("no overdue books founded")
    conn.close()




def admin_menu():
    while True:
        try:
            print('=' * 60)
            print("ADMIN MENU".center(60))
            print('=' * 60)
            print("Select an option:\n")

            menu_items = [
                ("1. Add Author",        "2. View Author"),
                ("3. Delete Author",     "4. Add Book"),
                ( "5. View Book",        "6. Delete Book" ),
                ("7. View Member",       "8. Delete Member"),
                ("9. View Transactions","10. View Overdue Books"),
                ("11. Logout",           ""),
            ]

            for left, right in menu_items:
                print(f"{left:<28}{right}")

            print('=' * 60)
            ch=int(input())

            if ch==1:
                add_author()
            elif ch == 2:
                view_author()
            elif ch ==3:
                delete_author()
            elif ch == 4:
                add_book()
            elif ch == 5:
                view_book()
            elif ch == 6:
                delete_book()
            elif ch == 7:
                view_member()
            elif ch == 8:
                view_member()
                delete_member()
            elif ch == 9:
                view_transactions()
            elif ch == 10:
                view_overdue_books()
            elif ch == 11:
                print("logging out.....")
                dash()
                break
            else:
                print("invalid option !...")
        except ValueError:
            print("Only select an number from the given option")




    

def member_menu(user_id):
    while True:
        try:
            print('=' * 60)
            print("MEMBER MENU".center(60))
            print('=' * 60)
            print("Select an option:\n")
            menu_items = [
                "1. View All Books",
                "2. Search Book",
                "3. Borrow Book",
                "4. Return Book",
                "5. See Overdue Books",
                "6. Logout",
            ]
            for item in menu_items:
                print(item)
            print('=' * 60)
            ch = int(input("\nEnter your choice: "))
            if ch == 1:
                view_book()
            elif ch == 2:
                search_book()
            elif ch == 3:
                view_book()
                borrow_book(user_id)
            elif ch == 4:
                return_book(user_id)
            elif ch == 5:
                see_overdue_books(user_id)
            elif ch == 6:
                print("logging out.....")
                dash()
                break
            else:
                print("invalid option !...")
        except ValueError:
            print("Please selct the an number from the option")

        

def dash():
    print('='*25,"LIBRARY MANAGEMENT  SYSTEM",'='*25)
    while True:
        try:
            ch = int(input("please select an option :\n1.Register\n2.Login\n3.exit\n:"))
            if ch == 1:
                adduser()
            elif ch == 2:
                user = login()
                if user:          
                    user_id=user[0]
                    role=user[1]
                    if role == "admin":
                        admin_menu()
                    elif role == "member":
                        member_menu(user_id)
            elif ch == 3:
                break
            else:
                print("invalid option !...")
        except ValueError:
            print("input error only enters numbers between 1-3")
        print('='*25,"LIBRARY MANAGEMENT  SYSTEM",'='*25)

dash()