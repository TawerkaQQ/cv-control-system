import psycopg2
import datetime
import os
from dotenv import load_dotenv


class Db_connector:
    def __init__(self, db_name: str, user: str, password: str, host: str):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host

    def connect_to_db(self):
        try:
            # пытаемся подключиться к базе данных
            conn = psycopg2.connect(dbname=self.db_name, user=self.user, password=self.password, host=self.host)
            print("Successfully connect to database")

        except:
            # в случае сбоя подключения будет выведено сообщение в STDOUT
            print('Error connection')

        return conn

    def execute(self, connector, transaction: str):
        with connector:
            with connector.cursor() as cursor:
                cursor.execute(transaction)
                connector.commit()
                cursor.close()
        connector.close()
        print("Successfully transaction")
        return self

    def add_user(self, connector, user_id, user_name: str,):
        with connector:
            with connector.cursor() as cursor:
                cursor.execute(f'''
                INSERT INTO users
                VALUES ({user_id}, '{user_name}') 
                            ''')
                connector.commit()
                cursor.close()
        connector.close()
        print("Successfully add new user")
        return self

    def add_input_log(self, connector, id):
        with connector:
            with connector.cursor() as cursor:
                cursor.execute(f'''
                INSERT INTO logs (id, input_time)
                VALUES ({id}, '{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
                            ''')
                connector.commit()
                cursor.close()
        connector.close()
        print("Successfully add new log")
        return self

    def add_output_log(self, connector, id):
        with connector:
            with connector.cursor() as cursor:
                cursor.execute(f'''
                UPDATE logs 
                SET output_time = '{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
                work_time = (SELECT output_time - input_time FROM logs WHERE id = '{id}')
                WHERE id ='{id}';
                            ''')

                connector.commit()

                cursor.close()
        self.update_work_time(connector, id)
        connector.close()

        print("Successfully update log")
        return self

    def update_work_time(self, connector, id):
        with connector:
            with connector.cursor() as cursor:
                cursor.execute(f'''UPDATE logs
                                SET work_time= (output_time - input_time) WHERE id = '{id}';
                                    ''')
                connector.commit()
                cursor.close()

        connector.close()
        return self


if __name__ == '__main__':

    load_dotenv()

    db_name = os.getenv('db_name')
    user = os.getenv('user')
    db_pass = os.getenv('db_pass')
    host = os.getenv('host')

    db = Db_connector(db_name, user, db_pass, host)
    conn = db.connect_to_db()

