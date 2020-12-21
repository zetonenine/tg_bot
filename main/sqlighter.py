import sqlite3


class SQLighter:

    def __init__(self, tables):
        self.connection = sqlite3.connect(tables)
        self.cursor = self.connection.cursor()

    def add_user(self, chatID, status=False):
        """Добавляем нового юзера в бд (неуверен)"""

        with self.connection:
            print('sqlighter  -  add_user (' + str(chatID) + ')')
            return self.cursor.execute("INSERT or IGNORE into 'users' ('chatID', 'status') VALUES(?,?)",
                                       (chatID, status))

    def user_exists(self, chatID):
        """Проверяем есть ли юзер в базе (неуверен)"""

        with self.connection:
            result = self.cursor.execute('SELECT * FROM "users" WHERE "chatID" = ?', (chatID,)).fetchall()
            print('sqlighter  -  user_exists (' + str(chatID) + ')  - ', bool(result))
            return bool(len(result))

    def status_true(self, status, chatID):
        """Меняем status юзера на False"""

        with self.connection:
            print('sqlighter  -  status_true (' + str(chatID) + ')')
            return self.cursor.execute('UPDATE "users" SET "status" = ? WHERE "chatID" = ?', (status, chatID))

    def finding_free_chat(self, chatID, partner_chatID, status=False):
        """Ищем юзера с условием: status = 1, partner_chatID = Null/None
        Добавляем его chatID в partner_chatID и наоборот. У обоих сбрасываем status"""

        try:
            with self.connection:
                free_user = self.cursor.execute('SELECT chatID FROM "users" WHERE "chatID" !=? AND "status" = 1 '
                                                'AND "partner_chatID" IS NULL LIMIT 1', (chatID,)).fetchall()
                free_user = free_user[0][0]
                # Получаем переменную partner_chatID

                me_pcID = self.cursor.execute('UPDATE "users" SET "partner_chatID" = ? WHERE "chatID" = ?',
                                              (free_user, chatID)).fetchall()
                par_pcID = self.cursor.execute('UPDATE "users" SET "partner_chatID" = ? WHERE "chatID" = ?',
                                               (chatID, free_user))
                me_status = self.cursor.execute('UPDATE "users" SET "status" = ? WHERE "chatID" = ?', (status, chatID))
                par_status = self.cursor.execute('UPDATE "users" SET "status" = ? WHERE "chatID" = ?',
                                                 (status, free_user))

                # me_pcID и par_pcID - Добавляет id собеседников друг другу в partner_chatID
                # me_status и par_status - Сбрасывает status на 0

                print(free_user)
                return free_user
        except:
            return None

    def status_false_and_clear_partner(self, status, chatID, partner_chatID):
        """Меняем status юзера на False"""

        with self.connection:
            print('sqlighter  -  status_false_and_clear_partner (' + str(chatID) + ')')
            partner = self.cursor.execute('SELECT partner_chatID FROM "users" WHERE "chatID" = ?', (chatID,)).fetchall()
            partner = partner[0][0]
            status_result = self.cursor.execute('UPDATE "users" SET "status" = ? WHERE "chatID" = ?', (status, chatID))
            partner_chatID_result = self.cursor.execute('UPDATE "users" SET "partner_chatID" = ? WHERE "chatID" = ?',
                                                        (partner_chatID, chatID))
            partner_chatID_partner_chatID_result = self.cursor.execute('UPDATE "users" SET "partner_chatID" = ? '
                                                                       'WHERE "chatID" = ?', (partner_chatID, partner))

            return partner

    def pcID_checker(self, chatID):

        with self.connection:
            pcID = self.cursor.execute('SELECT partner_chatID FROM "users" WHERE "chatID" = ?', (chatID,)).fetchall()
            pcID = pcID[0][0]
            print(pcID)
            return pcID

    def user_deleting(self, chatID):
        """Удаляем из базы данных"""

        with self.connection:
            print('sqlighter  -  user_deleting (' + str(chatID) + ')')
            return self.cursor.execute('DELETE FROM "users" WHERE "chatID" = ?', (chatID,))


    # def user_exists2(self, chatID):
    # """Сторонний способ проверить наличие юзера"""
    #    with self.connection:
    #        result = self.cursor.execute('SELECT EXISTS (SELECT * FROM "users" WHERE "chatID" = ?)', (chatID, )).fetchall()
    #        print(bool(result))
    #        return bool(len(result))
