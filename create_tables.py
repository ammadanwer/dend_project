import configparser
import psycopg2
import psycopg2.extras

from sql_queries import drop_table_queries, create_table_queries


def connect_database():
    config = configparser.ConfigParser()
    config.read('credentials.cfg')

    host = config.get('POSTGRES_CREDENTIALS', 'HOST')
    port = config.get('POSTGRES_CREDENTIALS', 'PORT')
    database = config.get('POSTGRES_CREDENTIALS', 'DATABASE')
    user = config.get('POSTGRES_CREDENTIALS', 'USERNAME')
    password = config.get('POSTGRES_CREDENTIALS', 'PASSWORD')
    conn = psycopg2.connect(f"host={host} dbname={database} user={user} password={password} port={port}")
    conn.set_session(autocommit=True)
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    return cur, conn


def drop_tables(cur, conn):
    """
    This function iterates over all the drop table queries and executes them
    Args:
        cur: The cursor variable of the database
        conn: The connection variable of the database
    """
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    """
    This function iterates over all the create table queries and executes them.
    Args:
        cur: The cursor variable of the database
        conn: The connection variable of the database
    """
    for query in create_table_queries:
        cur.execute(query)
        conn.commit()


def main():
    cur, conn = connect_database()
    drop_tables(cur, conn)
    create_tables(cur, conn)
    conn.close()


if __name__ == "__main__":
    main()
