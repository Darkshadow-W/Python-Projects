#!/usr/bin/env python
"""
Database initialization script
Run this script to set up the database and tables
"""

import os
import sys
from dotenv import load_dotenv
import mysql.connector

# Load environment variables
load_dotenv()

def init_database():
    """Initialize the database and create tables"""
    
    # Get configuration
    host = os.getenv('MYSQL_HOST', 'localhost')
    user = os.getenv('MYSQL_USER', 'root')
    password = os.getenv('MYSQL_PASSWORD', '')
    database = os.getenv('MYSQL_DATABASE', 'pdf_converter_db')
    port = int(os.getenv('MYSQL_PORT', 3306))
    
    print("Initializing PDF Converter Database...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Database: {database}")
    print()
    
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        
        cursor = conn.cursor()
        
        # Create database
        print("Creating database...")
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {database} "
            f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        
        # Switch to database
        cursor.execute(f"USE {database}")
        
        # Create users table
        print("Creating users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(120) NOT NULL UNIQUE,
                username VARCHAR(80) NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_email (email),
                INDEX idx_username (username)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Create conversions table
        print("Creating conversions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                original_filename VARCHAR(255) NOT NULL,
                converted_filename VARCHAR(255) NOT NULL,
                original_format VARCHAR(10) NOT NULL,
                target_format VARCHAR(10) NOT NULL,
                file_size INT,
                status VARCHAR(20) DEFAULT 'pending',
                error_message TEXT,
                original_file_path VARCHAR(500) NOT NULL,
                converted_file_path VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL,
                INDEX idx_user_id (user_id),
                INDEX idx_created_at (created_at),
                INDEX idx_status (status),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        # Create file_metadata table
        print("Creating file_metadata table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_metadata (
                id INT AUTO_INCREMENT PRIMARY KEY,
                conversion_id INT NOT NULL,
                pages INT,
                width FLOAT,
                height FLOAT,
                duration INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_conversion_id (conversion_id),
                FOREIGN KEY (conversion_id) REFERENCES conversions(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print()
        print("✓ Database initialized successfully!")
        print()
        print("Next steps:")
        print("1. Update .env file with your MySQL credentials")
        print("2. Run: python app.py")
        print("3. Visit: http://localhost:5000")
        
        return True
        
    except mysql.connector.Error as err:
        if err.errno == 2003:
            print("✗ Error: Cannot connect to MySQL server")
            print("  Make sure MySQL is running")
        elif err.errno == 1045:
            print("✗ Error: Access denied (wrong username/password)")
        else:
            print(f"✗ Database error: {err}")
        return False
    
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)
