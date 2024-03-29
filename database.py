import sqlite3


class Database:
    def __init__(self, path):
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()

    def new_write(self, data, table):
        column_names = []
        insert_data = []

        for key, value in data.items():
            column_names.append(str(key))
            insert_data.append(value)

        ask_symbols = ', '.join(['?'] * len(column_names))

        insert_data = [tuple(insert_data)]
        column_names = ', '.join(column_names)

        query = f' INSERT INTO {table}({column_names}) VALUES({ask_symbols}) '

        self.cursor.executemany(query, insert_data)
        self.connection.commit()

    def update_data(self, data: dict(), filters: dict() = None, table=None):
        '''
        обновление данных в бд

        data - словарь в формате <колонна>:<значение> (можно несколько)
        id - обновление произойдет только у определенного пользователя, если None - у всех
        table - таблица, в которой произойдет обновление данных
        '''

        if filters != None:
            fiilters_list = []

            for filer in filters:
                query_text = f'{filer} = "{filters[filer]}"'
                fiilters_list.append(query_text)

            query_filters = ' AND '.join(fiilters_list)
            query_filters = 'where ' + query_filters

            for key in data:
                update_data = (data[key],)

                query = f'UPDATE {table} SET {key} = ? {query_filters}'
                self.cursor.execute(query, update_data)

        else:
            for key in data:
                update_data = (data[key],)

                query = f'UPDATE {table} SET {key} = ?'
                self.cursor.execute(query, update_data)

        self.connection.commit()

    def get_data(self, filters: dict() = None, table=None):
        '''
        Получает данные из базы данных и возвращает список словарей, где ключи - это названия колонок таблицы.
    
        filters - фильтры для поиска в формате {колонка: значение}.
        table - имя таблицы, из которой будут получены данные.
        '''

        query_filters = ""
        if filters:
            filter_list = [f"{column} = '{value}'" for column, value in filters.items()]
            query_filters = "WHERE " + " AND ".join(filter_list)

        select_query = f"SELECT * FROM {table} {query_filters}"
        self.cursor.execute(select_query)

        # Получаем имена столбцов из описания результата запроса
        columns = [description[0] for description in self.cursor.description]

        # Получаем все строки запроса
        rows = self.cursor.fetchall()

        # Формируем список словарей, где ключи - названия колонок, а значения - данные из строк результата запроса
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))

        return data

    def delete(self, table, filters: dict() = dict()):
        fiilters_list = []

        for filer in filters:
            query_text = f'{filer} = "{filters[filer]}"'
            fiilters_list.append(query_text)

        query = ' AND '.join(fiilters_list)
        query = 'where ' + query

        query = f"DELETE from {table} {query}"

        self.cursor.execute(query)
        self.connection.commit()
