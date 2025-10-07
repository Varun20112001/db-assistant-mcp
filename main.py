from fastmcp import FastMCP
from sqlalchemy import create_engine, text
from sqlalchemy import inspect
from dotenv import load_dotenv
import os
import re

load_dotenv()

mcp = FastMCP(
    name="Database Assistant"
)

import sys

def is_read_only_query(sql: str) -> bool:
    """
    Validate if a SQL query is read-only (safe to execute).
    
    :param sql: The SQL query to validate
    :return: True if the query is read-only, False otherwise
    """
    # Remove comments and normalize whitespace
    sql_clean = re.sub(r'--.*?$', '', sql, flags=re.MULTILINE)  # Remove line comments
    sql_clean = re.sub(r'/\*.*?\*/', '', sql_clean, flags=re.DOTALL)  # Remove block comments
    sql_clean = sql_clean.strip()
    
    # Split into statements (handle multiple statements)
    statements = [stmt.strip() for stmt in sql_clean.split(';') if stmt.strip()]
    
    # If no statements after cleaning, it's safe (empty or comments only)
    if not statements:
        return True
    
    # Define allowed read-only statement types
    read_only_patterns = [
        r'^SELECT\b',
        r'^WITH\b.*SELECT\b',
        r'^EXPLAIN\b',
        r'^DESCRIBE\b',
        r'^SHOW\b',
        r'^PRAGMA\b.*=\s*off$',  # Only allow PRAGMA statements that turn things off
    ]
    
    # Define forbidden write operations
    forbidden_patterns = [
        r'\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|REPLACE)\b',
        r'\b(GRANT|REVOKE|SET|RESET)\b',
        r'\bCALL\b',
        r'\bEXECUTE\b',
        r'\bPRAGMA\b.*=\s*on$',  # Forbid PRAGMA statements that turn things on
    ]
    
    for statement in statements:
        if not statement:
            continue
            
        statement_upper = statement.upper()
        
        # Check if statement matches any forbidden pattern
        for pattern in forbidden_patterns:
            if re.search(pattern, statement_upper, re.IGNORECASE):
                return False
        
        # Check if statement matches any allowed pattern
        allowed = False
        for pattern in read_only_patterns:
            if re.search(pattern, statement_upper, re.IGNORECASE):
                allowed = True
                break
        
        if not allowed:
            return False
    
    return True

# Database setup
try:
    db_url = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME')}"
    )
    engine = create_engine(db_url)
except Exception as e:
    print(f"Failed to create engine: {e}", file=sys.stderr)
    raise

# Introspect schema
try:
    inspector = inspect(engine)
except Exception as e:
    print(f"Failed to inspect engine: {e}", file=sys.stderr)
    raise

class Get_schema:
    schema = {}
    def __init__(self, engine):
        self.engine = engine

    def get_schema(self):
        if self.schema:
            return self.schema
        else:
            # Get the schema of the database
            tables = inspector.get_table_names()

            for table in tables:
                if table.startswith("django_"):
                    continue
                columns = inspector.get_columns(table)
                self.schema[table] = [col for col in columns]
            return self.schema

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

@mcp.resource("schema://")
def get_schema() -> str:
    """
    This Python function retrieves the schema of a database by getting the table names and columns using
    an inspector object.
    :return: A dictionary containing the schema of the database, where the keys are table names and the
    values are lists of column information for each table.
    """
    return Get_schema(engine).get_schema()
    


@mcp.tool()
def ask_db(sql: str) -> dict:
    """
    The function `ask_db` executes a SQL query and returns the result in a dictionary format.
    Only read-only queries (SELECT, WITH, EXPLAIN, etc.) are allowed for security.
    
    :param sql: The `ask_db` function takes a SQL query as input and executes it against a database
    using an SQLAlchemy engine. The function then returns a dictionary containing the SQL query and the
    result of the query execution
    :type sql: str
    :return: The function `ask_db` returns a dictionary with two keys: "sql" and "result". The "sql" key
    contains the SQL query that was executed, and the "result" key contains the result of the query in a
    nicely formatted list of dictionaries. If an error occurs during the SQL execution, the function
    returns a dictionary with an "error" key containing the error message and the original
    """
    sql = sql.strip()
    # Validate that the query is read-only
    if not is_read_only_query(sql):
        return {
            "error": "Only read-only queries are allowed. Permitted operations: SELECT, WITH...SELECT, EXPLAIN, DESCRIBE, SHOW",
            "sql": sql
        }
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql)).fetchall()
            result = [dict(row._mapping) for row in result]  # Format nicely
    except Exception as e:
        return {"error": f"SQL execution failed: {str(e)}", "sql": sql}

    return {
        "sql": sql,
        "result": result
    }

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
