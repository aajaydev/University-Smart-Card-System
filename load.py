import mysql.connector
from sqlalchemy import create_engine

def load(dfs, host, user, password, database="UniDB"):
    # Create a connection to the database
    connection = mysql.connector.connect(host=host, user=user, password=password, database=database)
    cursor = connection.cursor()

    # Drop existing tables in UniDB (Be cautious with this step)
    cursor.execute("DROP DATABASE IF EXISTS UniDB")
    cursor.execute("CREATE DATABASE UniDB")
    cursor.execute("USE UniDB")

    connection.commit()

    # SQLAlchemy engine for Pandas
    engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}', echo=False)

    # Load data into the new table
    table_names = {0:"swimming_pool_data", 1:"swimming_pool_non_membership_data", 2:"gym_data", 3:"equipment_data", 4:"equipment_loss_data", 
                   5:"sports_medicine_data", 6:"home_leave_data", 7:"hostel_data", 8:"hostel_medicine_data", 9:"courier_data",
                   10:"mess_1_data", 11:"mess_2_data", 12:"student_data", 13:"home_leave_data", 14:"integrated_data"}

    for df_index, df in enumerate(dfs):
        table_name = table_names[df_index]

        # Standardize Roll_No to VARCHAR if it's not already
        if 'Roll_No' in df.columns:
            df['Roll_No'] = df['Roll_No'].astype(str)

        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)

        # Modify the Roll_No column type
        alter_table_sql = f"ALTER TABLE `{table_name}` MODIFY `Roll_No` VARCHAR(255);"
        cursor.execute(alter_table_sql)

        # Check if primary key exists, and if not, add it
        cursor.execute(f"SHOW KEYS FROM `{table_name}` WHERE Key_name = 'PRIMARY'")
        if not cursor.fetchone():
            alter_table_sql = f"ALTER TABLE `{table_name}` ADD PRIMARY KEY (`Roll_No`, `Sr_No`);"
            cursor.execute(alter_table_sql)

    connection.commit()

    cursor.close()
    connection.close()
    print("Data Loaded into UniDB Warehouse")
