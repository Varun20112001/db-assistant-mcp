from fastmcp import FastMCP
from sqlalchemy import create_engine, text
from sqlalchemy import inspect
from dotenv import load_dotenv
import os
import re
import json

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

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

@mcp.tool("test_simple")
def test_simple() -> str:
    """Test if basic tool works"""
    return "Simple test works"

@mcp.tool("get_schema")
def get_schema() -> str:
    """
    Get database schema information as a formatted string
    """
    try:
        with engine.connect() as conn:
            # Get all table names
            table_query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name
            """
            table_result = conn.execute(text(table_query)).fetchall()
            
            schema_text = "Database Schema:\n\n"
            
            for table_row in table_result:
                table_name = table_row[0]
                if table_name.startswith("django_"):
                    continue
                
                schema_text += f"Table: {table_name}\n"
                schema_text += "-" * (len(table_name) + 7) + "\n"
                
                # Get column information
                column_query = """
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default
                    FROM information_schema.columns 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                    ORDER BY ordinal_position
                """
                column_result = conn.execute(text(column_query), (table_name,)).fetchall()
                
                for col_row in column_result:
                    col_name, data_type, nullable, default = col_row
                    nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                    default_str = f" DEFAULT {default}" if default else ""
                    schema_text += f"  {col_name}: {data_type} {nullable_str}{default_str}\n"
                
                # Get primary keys
                pk_query = """
                    SELECT column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.table_schema = 'public'
                    AND tc.table_name = %s
                    AND tc.constraint_type = 'PRIMARY KEY'
                """
                pk_result = conn.execute(text(pk_query), (table_name,)).fetchall()
                if pk_result:
                    pk_columns = [row[0] for row in pk_result]
                    schema_text += f"  PRIMARY KEY: {', '.join(pk_columns)}\n"
                
                # Get foreign keys
                fk_query = """
                    SELECT 
                        kcu.column_name,
                        ccu.table_name AS foreign_table_name,
                        ccu.column_name AS foreign_column_name
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = 'public'
                    AND tc.table_name = %s
                """
                fk_result = conn.execute(text(fk_query), (table_name,)).fetchall()
                
                for fk_row in fk_result:
                    col_name, ref_table, ref_col = fk_row
                    schema_text += f"  FOREIGN KEY: {col_name} -> {ref_table}.{ref_col}\n"
                
                schema_text += "\n"
            
            return schema_text
    
    except Exception as e:
        return f"Error getting schema: {str(e)}"
        
    except Exception as e:
        return {"error": f"Failed to get schema: {str(e)}"}


@mcp.tool("ask_db")
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
