#  CSV Processor API: CSV-to-JSON-to-PostgreSQL

This project implements a Python-based FastAPI application that reads a large CSV file, applies custom transformation and nesting logic, calculates demographic metrics, and performs a bulk upload to a PostgreSQL database.

---

##  Features

* **Custom Parsing:** Converts flat CSV columns (e.g., `name.firstName`, `address.city`) into nested JSON objects.
* **Schema Mapping:** Maps the converted JSON data to a defined PostgreSQL schema using `VARCHAR`, `INT`, and `JSONB` data types.
* **Bulk Insertion:** Efficiently uploads processed data to PostgreSQL using batch insertion methods.
* **Reporting:** Generates a real-time age distribution report printed to the console upon successful processing.
* **API Trigger:** Runs the entire pipeline via an HTTP POST request.

---

##  Prerequisites

Ensure you have the following software installed on your machine:

* Python 3.12+
* PostgreSQL 15+ (Running and accessible)
* Git (For cloning and version control)

---

##  Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/samruddhi0411/csv_processor.git
cd csv_processor
```

### 2. Create and Activate Virtual Environment

It is crucial to use a virtual environment to manage dependencies.

```bash
# Create the environment
python -m venv venv

# Activate the environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

Install the required Python packages (`fastapi`, `uvicorn`, `psycopg2-binary`, `python-dotenv`).

```bash
(venv) PS C:\Users\SAMRUDDHI\csv_processor> python -m pip install -r requirements.txt
```

> **Note:** You will need a `requirements.txt` file listing the dependencies:
> `fastapi`, `uvicorn`, `psycopg2-binary`, `python-dotenv`.

---

##  Database Configuration

The application requires a running PostgreSQL database named `csv_import` and a `users` table.

### 1. Create the Database

Using `psql` or `pgAdmin 4`, create the target database:

```sql
CREATE DATABASE csv_processor;
```

### 2. Create the `users` Table

Connect to the newly created `csv_import` database and execute:

```sql
CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    "name" VARCHAR NOT NULL,
    age INT NOT NULL,
    address JSONB,              -- Stores nested address details
    additional_info JSONB       -- Stores all other unmapped fields (e.g., gender)
);
```

### 3. Configure `.env` File

Create a `.env` file in the root directory and populate it with your database credentials:

```env
# Database Connection String: Ensure dbname=csv_import
DATABASE_URL="dbname=csv_import user=postgres password=YOUR_DB_PASSWORD host=localhost port=5432"

# Path to the CSV file to be processed
CSV_FILE_PATH=./data/users.csv
```

---

##  Running the API Server

The server is run using **Uvicorn**, which hosts the FastAPI application defined in `main.py`.

### 1. Place Input File

Ensure your input file `users.csv` is located in the `data/` directory.

### 2. Start the Server

```bash
(venv) PS C:\Users\SAMRUDDHI\csv_processor> python -m uvicorn main:app --reload --port 8000
```

The server will start at [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

##  API Usage

The conversion pipeline is triggered via a **POST request** to the `/api/convert` endpoint.

### Endpoint Details

| Method | Endpoint     | Description                                                          |
| ------ | ------------ | -------------------------------------------------------------------- |
| POST   | /api/convert | Triggers the full CSV processing and bulk data upload to PostgreSQL. |
| GET    | /            | Basic health check.                                                  |

### Example Trigger (Using cURL)

```bash
curl -X POST http://127.0.0.1:8000/api/convert
```

### Response

The API returns a JSON object confirming the status and providing the calculated age distribution report:

```json
{
  "status": "success",
  "message": "CSV processing complete and 4 age groups reported.",
  "age_distribution": {
    "< 20": "25.00%",
    "20 to 40": "25.00%",
    "40 to 60": "25.00%",
    "> 60": "25.00%"
  }
}
```

> **Note:** Detailed insertion logs and the final Age Distribution Report are also printed directly to the console where Uvicorn is running.
