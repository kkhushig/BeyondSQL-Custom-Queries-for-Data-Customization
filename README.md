# BeyondSQL – Custom Queries for Data Customization

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Query Language](#query-language)
  - [Supported Queries](#supported-queries)
  - [Example Queries](#example-queries)
- [Chunking and Memory Management](#chunking-and-memory-management)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Folder Structure](#folder-structure)
- [Challenges Faced](#challenges-faced)
- [Future Enhancements](#future-enhancements)
- [Learning Outcomes](#learning-outcomes)
- [References](#references)

---

## Overview
BeyondSQL is a custom query system that allows users to interact with large datasets using a specialized query language inspired by SQL. It was designed to efficiently manage and process large datasets that cannot fit entirely into memory. Through its user-friendly command-line interface (CLI), BeyondSQL provides powerful data manipulation functionalities such as filtering, sorting, joining, and aggregating data.

This project was created to handle a large dataset of RF signal observations but can be adapted to work with other relational datasets. It offers a flexible way to interact with data by writing natural-language-inspired SQL queries without needing the complexity of standard database management systems.

## Features
- **Custom Query Language**: Easily interact with your data using natural-language-inspired SQL commands.
- **Memory-Efficient Processing**: Large datasets are chunked and processed in manageable parts to avoid memory overflows.
- **CRUD Operations**: Full support for Create, Read, Update, and Delete operations.
- **Data Exploration**: Efficiently project columns, filter data, and apply aggregation functions.
- **Join Operations**: Perform complex joins across tables using various join types (inner, left, right, cross).
- **Grouping and Aggregation**: Group data by one or more columns and apply aggregation functions like `sum`, `count`, and `average`.
- **Command-Line Interface**: Simple CLI for entering queries and interacting with data in real-time.
- **Dynamic Table Creation**: Create new tables from your datasets, customized to the structure you need.

## System Architecture
BeyondSQL is designed to efficiently manage and process data by splitting large datasets into smaller chunks, allowing operations to be performed on systems with limited memory. The architecture of the system includes:
- **Input Layer**: Handles the dataset by reading CSV files and chunking them into manageable pieces.
- **Processing Engine**: Executes user queries, interacts with the dataset chunks, and performs CRUD operations, joining, filtering, and aggregating data.
- **Output Layer**: Displays query results using a clean tabular format with the `PrettyTable` library.

### Flowchart
1. **User Input**: User enters a query in the CLI.
2. **Query Parsing**: The system parses the query and determines the type of operation.
3. **Data Chunking**: Data is retrieved from memory-efficient chunks.
4. **Query Execution**: The specified operation (e.g., filtering, sorting, joining) is performed on the data.
5. **Result Output**: The result is displayed as a formatted table.

## Query Language
BeyondSQL uses a custom query language with commands resembling MySQL but simplified for ease of use. This language includes a range of operations from basic data retrieval to complex joins and aggregation.

### Supported Queries
- **Projection**: Select specific columns from a table.
- **Filtering**: Select rows that match certain conditions.
- **Joining**: Combine data from multiple tables using various join types.
- **Grouping**: Group data by specific columns and apply aggregation functions.
- **Aggregation**: Compute summary statistics on datasets (e.g., sum, count, average).
- **Ordering**: Sort data in ascending or descending order.
- **CRUD**: Insert, update, or delete rows from tables.
- **Table Creation**: Dynamically create new tables with specific columns and data types.

### Example Queries
Here are some sample queries that demonstrate the power and flexibility of BeyondSQL's custom query language:

1. **Projection**:
    ```sql
    display AntennaType, DeviceType from SignalData
    ```
    Retrieves the `AntennaType` and `DeviceType` columns from the `SignalData` table.

2. **Filtering**:
    ```sql
    give the entries from Weather where WindSpeed > 10
    ```
    Filters rows in the `Weather` table where the wind speed is greater than 10.

3. **Joining**:
    ```sql
    combine SignalData and IQData using DeviceType with inner
    ```
    Performs an inner join between the `SignalData` and `IQData` tables using the `DeviceType` column as the key.

4. **Aggregation**:
    ```sql
    compute Temperature, Humidity from Weather using count
    ```
    Counts the number of rows for `Temperature` and `Humidity` columns in the `Weather` table.

5. **Ordering**:
    ```sql
    arrange the data in IQData by DeviceType with ascending order
    ```
    Sorts the `IQData` table in ascending order based on `DeviceType`.

6. **Data Insertion**:
    ```sql
    include a new entry in Weather with Timestamp == '2023-06-05 09:00', Temperature == 35, Humidity == 40, WindSpeed == 23, Precipitation == 0, WeatherCondition == 'Sunny'
    ```
    Inserts a new row into the `Weather` table.

## Chunking and Memory Management
BeyondSQL employs a chunking technique to handle large datasets that may not fit into the system's memory. Instead of loading the entire dataset at once, the system breaks the dataset into smaller chunks and processes them sequentially.

### How It Works
1. **Chunk Creation**: When the dataset is first loaded, it is split into smaller chunks based on a user-defined chunk size.
2. **Data Processing**: Queries are executed on these chunks, one at a time, and the results are merged.
3. **Efficiency**: This method ensures that memory is used efficiently and large datasets can be processed even on resource-constrained systems.

## Tech Stack
- **Python**: The core programming language used for building the system.
- **csv Module**: Used for reading and writing data in CSV format.
- **os Module**: For file system operations, such as creating directories and handling files.
- **PrettyTable**: A library used to display query results in a clean tabular format.
- **Jupyter Notebooks**: Initially used for testing and prototyping the functionality.
- **Visual Studio Code (VSCode)**: Used for final implementation and debugging.

## Installation
Follow these steps to install and run BeyondSQL:

1. Clone the repository:
    ```bash
    git clone https://github.com/your-repo/BeyondSQL.git
    cd BeyondSQL
    ```
2. Install required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Launch the command-line interface (CLI):
    ```bash
    python beyondsql_cli.py
    ```

## Usage
Once the CLI is running, you can enter any of the supported queries. Example:

```bash
Enter Query > display AntennaType, DeviceType from SignalData
```

## Folder Structure

The following folders are created to store chunks and tables:

- **/Chunks**: Contains the data chunks created during the chunking process.
- **/Tables**: Stores dynamically created tables as CSV files.

## Challenges Faced

- **ANTLR:** Originally, ANTLR was intended to be used for query parsing. However, it introduced complexities in debugging, and eventually, a Python-based parser was implemented instead.
- **Filtering:** Implementing complex filtering logic, especially with multiple conditions, was a challenge. It required significant effort to convert user-defined conditions into executable code.
- **Memory Management:** Ensuring the system could handle large datasets in a memory-efficient way was a key focus, leading to the development of the chunking system.

## Future Enhancements
- **Graphical User Interface (GUI):** Move from the CLI to a GUI-based application to make the system more user-friendly.
- **Advanced Filtering:** Improve the filtering functionality to handle more complex conditions, including filtering across multiple joined tables.
- **Enhanced Join Operations:** Expand the join functionality to support more complex join conditions and optimizations for large datasets.

## Learning Outcomes
- **Database Design:** Gained experience in designing and implementing a custom database system with query support.
- **Query Language:** Developed skills in creating a specialized query language and implementing query parsing and execution.
- **Memory Management:** Learned to manage large datasets efficiently using chunking to avoid memory overload.

## References
https://www.kaggle.com/datasets/suraj520/rf-signal-data
