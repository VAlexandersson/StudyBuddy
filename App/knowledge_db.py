import sqlite3
from  .document_processing import ingest_document
from typing import Dict 

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(f"Error occurred while connecting to the database: {e}")
    
    return conn

def create_table(conn, table_name, table_schema):
    cursor = conn.cursor()
    cursor.execute(table_schema)
    cursor.close()
    
# TODO: Move to a schema file instead.
def create_tables(conn):
    # Create the Course table
    course_table_schema = '''
        CREATE TABLE IF NOT EXISTS Course (
            CourseID INTEGER PRIMARY KEY,
            CourseName TEXT,
            CourseCode TEXT,
            Term TEXT,
            Description TEXT,
            Keywords TEXT,
            Department TEXT,
            Prerequisites TEXT,
            UNIQUE (CourseCode, Term)
        )
    '''

    # Create the Materials table
    reference_table_schema = '''
        CREATE TABLE IF NOT EXISTS Reference (
            ReferenceID INTEGER PRIMARY KEY,
            CourseID INTEGER,
            Type TEXT,
            Title TEXT,
            Summary TEXT,
            Keywords TEXT,
            Path TEXT,
            DateAdded DATE,
            FOREIGN KEY (CourseID) REFERENCES Course (CourseID),
            UNIQUE (Title)
        )
    '''

    # Create the Reference  table
    chunk_table_schema = '''
        CREATE TABLE IF NOT EXISTS Chunk (
            ChunkID INTEGER PRIMARY KEY,
            ReferenceID INTEGER,
            OrderID INTEGER,
            Type TEXT,
            Chunk TEXT,
            Summary TEXT,
            Page INTEGER,
            Keywords TEXT,
            Chapter TEXT,
            ParentChapter,
            FOREIGN KEY (ReferenceID) REFERENCES Reference (ReferenceID)
            UNIQUE (OrderID, ReferenceID)
        )
    '''
    """
#    # Create the CourseInfo table
#    course_info_table_schema = '''
#        CREATE TABLE IF NOT EXISTS CourseInfo (
#            InfoID INTEGER PRIMARY KEY,
#            CourseID INTEGER,
#            InfoType TEXT,
#            Term TEXT,
#            Year INTEGER,
#            FOREIGN KEY (CourseID) REFERENCES Course (CourseID)
#        )
#    '''
#
#    # Create the Resources table
#    resources_table_schema = '''
#        CREATE TABLE IF NOT EXISTS Resources (
#            ResourceID INTEGER PRIMARY KEY,
#            CourseID INTEGER,
#            Title TEXT,
#            URL TEXT,
#            Description TEXT,
#            FOREIGN KEY (CourseID) REFERENCES Course (CourseID)
#        )
#    '''
    """    
    # Create tables
    create_table(conn, "Course", course_table_schema)
    create_table(conn, "Reference", reference_table_schema)
    create_table(conn, "Chunk", chunk_table_schema)
    # create_table(conn, "CourseInfo", course_info_table_schema)
    # create_table(conn, "Resources", resources_table_schema)


def insert_course(conn, CourseCode, CourseName, Term, Description, Department, Keywords):
    cursor = conn.cursor()
    # Check if a course with the same code or Term already exists
    cursor.execute("SELECT * FROM Course WHERE CourseCode = ? AND Term = ?", (CourseCode, Term))
    existing_course = cursor.fetchone()

    # If the course doesn't exist, insert it into the Course table
    if existing_course is None:
        cursor.execute(
            "INSERT INTO Course (CourseCode, CourseName, Term, Description, Department, Keywords) VALUES (?, ?, ?, ?, ?, ?)", 
            (CourseCode, CourseName, Term, Description, Department, Keywords))
    
    conn.commit()
    cursor.close()

def insert_reference(conn, CourseCode, Title, Path, Type, StartPage=None, EndPage=None, Summary = None, Keywords = None):
    cursor = conn.cursor()
    # Check if the Reference with the same CourseCode and Title already exists
    cursor.execute("SELECT CourseID FROM Course WHERE CourseCode = ?", (CourseCode, ))
    course_id = cursor.fetchone()

    
    cursor.execute("SELECT * FROM Reference WHERE CourseID = ? AND Title = ?", (course_id[0], Title))
    existing_reference = cursor.fetchone()

    
    # If the Reference doesn't exist, insert it into the Reference table
    if existing_reference is None:
        cursor.execute(
            "INSERT INTO Reference (CourseID, Title, Type, Summary, Keywords, Path) VALUES (?, ?, ?, ?, ?, ?)", 
            (course_id[0], Title, Type, Summary, Keywords, Path))
        conn.commit()
        
        reference_id = cursor.lastrowid
    else:
        print("Refrence already exist.")
        reference_id = existing_reference[0]
    cursor.close()
    
    return reference_id


def insert_chunk(conn, chunk_data: Dict, ReferenceID):
    cursor = conn.cursor()
    # Check if the chunk with the same ChunkID already exists
    cursor.execute("SELECT * FROM Chunk WHERE ReferenceID = ? AND OrderID = ?", (ReferenceID, chunk_data['OrderID']))
    existing_chunk = cursor.fetchone()
    if existing_chunk:
        print("Chunk exists")
    # If the chunk doesn't exist, insert it into the Chunks table
    if existing_chunk is None:
        cursor.execute(
            "INSERT INTO Chunk (ReferenceID, OrderID, Type, Chunk, Summary, Page, Keywords, Chapter, ParentChapter) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
            (ReferenceID, chunk_data['OrderID'], chunk_data['Type'], chunk_data['Chunk'], chunk_data['Summary'], chunk_data['Page'], chunk_data['Keywords'], chunk_data['Chapter'], chunk_data['ParentChapter'],))
    conn.commit()
    cursor.close()


def insert_data(conn, data):
    courses = data["courses"]
    references = data["references"]
    
    for course in courses:
        insert_course(conn, **course)
    for content in references:
        
        reference_id = insert_reference(conn, **content)

        list_of_chunks_dicts = ingest_document(content["Path"], content["StartPage"], content["EndPage"])
        for chunk in list_of_chunks_dicts:
            insert_chunk(conn, chunk, reference_id)
            