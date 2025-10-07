# Database Assistant MCP

A Model Context Protocol (MCP) server that enables Large Language Models to safely interact with PostgreSQL databases through read-only queries. Built with FastMCP 2.0, this server provides secure database access for AI assistants while preventing any data modification operations.

## 🚀 Features

- **Safe Database Access**: Only allows read-only operations (SELECT, WITH, EXPLAIN, DESCRIBE, SHOW)
- **Schema Introspection**: Automatic database schema discovery and exploration
- **Security First**: Built-in SQL validation to prevent write operations
- **FastMCP 2.0**: Modern MCP implementation with improved performance
- **PostgreSQL Support**: Optimized for PostgreSQL databases with psycopg2
- **VS Code Integration**: Seamless integration with GitHub Copilot Chat

## 🛠️ Installation

### Prerequisites

- Python 3.11+
- PostgreSQL database
- VS Code with GitHub Copilot extension

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Varun20112001/db-assistant-mcp.git
   cd db-assistant-mcp
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv env
   # On Windows
   env\Scripts\activate
   # On macOS/Linux
   source env/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install fastmcp sqlalchemy psycopg2-binary python-dotenv
   ```

4. **Configure environment variables**:
   Create a `.env` file in the project root:
   ```env
   DB_USER=your_db_username
   DB_PASSWORD=your_db_password
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=your_database_name
   ```

## ⚙️ Configuration

### VS Code MCP Configuration

Add the following to your VS Code `mcp.json` file (usually located at `%APPDATA%\Code\User\mcp.json` on Windows):

```json
{
  "servers": {
    "database-assistant": {
      "command": "path/to/your/project/env/Scripts/python.exe",
      "args": [
        "path/to/your/project/main.py"
      ],
      "env": {
        "DB_USER": "postgres",
        "DB_PASSWORD": "your_password",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "your_database"
      },
      "type": "stdio"
    }
  },
  "inputs": []
}
```

**Note**: Replace the paths and database credentials with your actual values.

### Environment Variables

The server supports the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_USER` | Database username | - |
| `DB_PASSWORD` | Database password | - |
| `DB_HOST` | Database host | localhost |
| `DB_PORT` | Database port | 5432 |
| `DB_NAME` | Database name | - |

## 🎯 Usage

### Testing the Server

Test the server locally before using with VS Code:

```bash
python main.py
```

### GitHub Copilot Integration

Once configured, you can use the Database Assistant in GitHub Copilot Chat:

#### Basic Queries
```
@database-assistant Show me the database schema
@database-assistant How many users are in the system?
@database-assistant List all active applications
```

#### Schema Exploration
```
@database-assistant What tables are available?
@database-assistant Describe the users table structure
@database-assistant Show me all foreign key relationships
```

#### Data Analysis
```
@database-assistant Find the top 10 most active users
@database-assistant Show me application usage statistics
@database-assistant What are the different user roles?
```

### Available Tools and Resources

The MCP server provides:

1. **`ask_db` tool**: Execute safe, read-only SQL queries
2. **`schema://` resource**: Get complete database schema information
3. **`greeting://{name}` resource**: Get personalized greetings (demo feature)

### Security Features

- **Read-only Operations**: Only SELECT, WITH, EXPLAIN, DESCRIBE, and SHOW statements are allowed
- **SQL Validation**: Advanced regex patterns prevent write operations
- **Comment Stripping**: Removes SQL comments to prevent injection
- **Multi-statement Handling**: Validates each statement in multi-query requests

## 🔧 Development

### Project Structure

```
db-assistant-mcp/
├── main.py              # Main MCP server implementation
├── .env                 # Environment variables (create this)
├── .env.example         # Environment template
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── env/                # Virtual environment
```

### Key Components

- **FastMCP Server**: Main server implementation with tools and resources
- **SQL Validator**: Security layer preventing write operations
- **Schema Inspector**: Automatic database schema discovery
- **Connection Manager**: Secure database connection handling

### Adding New Features

To extend the server:

1. **Add new tools**: Use the `@mcp.tool()` decorator
2. **Add new resources**: Use the `@mcp.resource()` decorator
3. **Modify SQL validation**: Update the `is_read_only_query()` function

## 🚨 Security Considerations

- **Database User**: Use a read-only database user for additional security
- **Network Access**: Ensure database is only accessible from trusted sources
- **Environment Variables**: Never commit `.env` files to version control
- **SQL Injection**: The server includes protection against common injection attempts

## 🐛 Troubleshooting

### Common Issues

1. **Server won't start**:
   - Check database connection credentials
   - Ensure PostgreSQL is running
   - Verify virtual environment is activated

2. **VS Code integration not working**:
   - Restart VS Code after configuration changes
   - Check MCP server paths in configuration
   - Verify environment variables are set correctly

3. **Permission errors**:
   - Ensure database user has SELECT permissions
   - Check database connection from command line

### Debug Mode

Run with environment variables for debugging:
```bash
DB_USER=postgres DB_PASSWORD=password python main.py
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Support

For support and questions:
- Open an issue on GitHub
- Contact: [your-email@example.com]

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/jlowin/fastmcp)
- Uses [SQLAlchemy](https://sqlalchemy.org/) for database operations
- Powered by [psycopg2](https://psycopg.org/) for PostgreSQL connectivity
