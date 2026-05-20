SCHEMA_CONTEXT = """
-- Drop tables safely (order + CASCADE matters)
DROP TABLE IF EXISTS orderdetails CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS offices CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS productlines CASCADE;

-- Tables
CREATE TABLE productlines (
  "productLine" VARCHAR(50) PRIMARY KEY,
  "textDescription" VARCHAR(4000),
  "htmlDescription" TEXT,
  "image" BYTEA
);

CREATE TABLE products (
  "productCode" VARCHAR(15) PRIMARY KEY,
  "productName" VARCHAR(70) NOT NULL,
  "productLine" VARCHAR(50) NOT NULL,
  "productScale" VARCHAR(10) NOT NULL,
  "productVendor" VARCHAR(50) NOT NULL,
  "productDescription" TEXT NOT NULL,
  "quantityInStock" INTEGER NOT NULL,
  "buyPrice" NUMERIC(10,2) NOT NULL,
  "MSRP" NUMERIC(10,2) NOT NULL,
  FOREIGN KEY ("productLine") REFERENCES productlines("productLine")
);

CREATE TABLE offices (
  "officeCode" VARCHAR(10) PRIMARY KEY,
  "city" VARCHAR(50) NOT NULL,
  "phone" VARCHAR(50) NOT NULL,
  "addressLine1" VARCHAR(50) NOT NULL,
  "addressLine2" VARCHAR(50),
  "state" VARCHAR(50),
  "country" VARCHAR(50) NOT NULL,
  "postalCode" VARCHAR(15) NOT NULL,
  "territory" VARCHAR(10) NOT NULL
);

CREATE TABLE employees (
  "employeeNumber" INTEGER PRIMARY KEY,
  "lastName" VARCHAR(50) NOT NULL,
  "firstName" VARCHAR(50) NOT NULL,
  "extension" VARCHAR(10) NOT NULL,
  "email" VARCHAR(100) NOT NULL,
  "officeCode" VARCHAR(10) NOT NULL,
  "reportsTo" INTEGER,
  "jobTitle" VARCHAR(50) NOT NULL,
  FOREIGN KEY ("reportsTo") REFERENCES employees("employeeNumber"),
  FOREIGN KEY ("officeCode") REFERENCES offices("officeCode")
);

CREATE TABLE customers (
  "customerNumber" INTEGER PRIMARY KEY,
  "customerName" VARCHAR(50) NOT NULL,
  "contactLastName" VARCHAR(50) NOT NULL,
  "contactFirstName" VARCHAR(50) NOT NULL,
  "phone" VARCHAR(50) NOT NULL,
  "addressLine1" VARCHAR(50) NOT NULL,
  "addressLine2" VARCHAR(50),
  "city" VARCHAR(50) NOT NULL,
  "state" VARCHAR(50),
  "postalCode" VARCHAR(15),
  "country" VARCHAR(50) NOT NULL,
  "salesRepEmployeeNumber" INTEGER,
  "creditLimit" NUMERIC(10,2),
  FOREIGN KEY ("salesRepEmployeeNumber") REFERENCES employees("employeeNumber")
);

CREATE TABLE payments (
  "customerNumber" INTEGER,
  "checkNumber" VARCHAR(50),
  "paymentDate" DATE NOT NULL,
  "amount" NUMERIC(10,2) NOT NULL,
  PRIMARY KEY ("customerNumber", "checkNumber"),
  FOREIGN KEY ("customerNumber") REFERENCES customers("customerNumber")
);

CREATE TABLE orders (
  "orderNumber" INTEGER PRIMARY KEY,
  "orderDate" DATE NOT NULL,
  "requiredDate" DATE NOT NULL,
  "shippedDate" DATE,
  "status" VARCHAR(15) NOT NULL,
  "comments" TEXT,
  "customerNumber" INTEGER NOT NULL,
  FOREIGN KEY ("customerNumber") REFERENCES customers("customerNumber")
);

CREATE TABLE orderdetails (
  "orderNumber" INTEGER,
  "productCode" VARCHAR(15),
  "quantityOrdered" INTEGER NOT NULL,
  "priceEach" NUMERIC(10,2) NOT NULL,
  "orderLineNumber" SMALLINT NOT NULL,
  PRIMARY KEY ("orderNumber", "productCode"),
  FOREIGN KEY ("orderNumber") REFERENCES orders("orderNumber"),
  FOREIGN KEY ("productCode") REFERENCES products("productCode")
);
"""

DECOMPOSE_PROMPT = """
You are an expert SQL analyst. Your task is to decompose a natural language question about a database into structured components.
Return a valid JSON object matching the following structure:
{{
  "Intent": "A brief summary of what the user wants",
  "Tables": ["list of table names that likely need to be queried"],
  "Columns": ["list of column names relevant to the query"],
  "Filters": ["list of specific conditions or filters mentioned"],
  "Joins": ["list of likely tables that need to be joined"]
}}

Only return the raw JSON object, without markdown formatting or code blocks.
Question: {question}
"""

GENERATE_SQL_PROMPT = """
You are an expert PostgreSQL developer. Write a raw PostgreSQL SELECT query to answer the user's question based on the provided schema and query decomposition.

IMPORTANT RULES:
1. Return ONLY the raw SQL query string. NO markdown formatting, NO code blocks, NO explanations.
2. The query MUST be a SELECT statement. Do not use INSERT, UPDATE, DELETE, etc.
3. Pay attention to exact column and table names from the schema.
4. Ensure quotes around column names if they are mixed case in the schema (e.g., "productName").
5. Only use the tables and columns provided in the schema context.

Schema Context:
{schema}

Query Decomposition:
{decomposition}

Question: {question}
"""

FIX_SQL_PROMPT = """
You are an expert PostgreSQL developer. A previously generated SQL query failed to execute due to a database error.
Please analyze the error and the original query, then provide a corrected raw PostgreSQL SELECT query.

IMPORTANT RULES:
1. Return ONLY the corrected raw SQL query string. NO markdown formatting, NO code blocks, NO explanations.
2. The query MUST be a SELECT statement. Do not use INSERT, UPDATE, DELETE, etc.
3. Pay attention to exact column and table names from the schema.
4. Ensure quotes around column names if they are mixed case in the schema.

Schema Context:
{schema}

Original Query:
{original_query}

Database Error:
{error_message}
"""
