#Создание таблиц в Базе

queries_d ={
'history_tik':
    """CREATE TABLE cex_history_tik (
    tid        BIGINT          PRIMARY KEY ASC ON CONFLICT ROLLBACK,
    type       CHAR (6),
    unixdate   BIGINT,
    date       DATETIME,
    amount     DECIMAL (11, 8),
    price      DECIMAL (9, 2),
    sys_insert DATETIME
)"""

, 'im_history_tik':
    """CREATE TABLE im_cex_history_tik (
    tid      BIGINT          PRIMARY KEY ASC ON CONFLICT ROLLBACK,
    type     CHAR (6),
    unixdate BIGINT,
    date     DATETIME,
    amount   DECIMAL (11, 8),
    price    DECIMAL (9, 2) 
)"""

,'stg_history_tik':
    """CREATE TABLE stg_cex_history_tik (
    tid      BIGINT,
    type     CHAR (6),
    unixdate BIGINT,
    date     DATETIME,
    amount   DECIMAL (11, 8),
    price    DECIMAL (9, 2) 
)"""

,'active_orders':
    """CREATE TABLE active_orders (
    id         INTEGER        PRIMARY KEY,
    unix_date  INTEGER,
    pair       VARCHAR (20)   CHECK (pair IN ('BTC/USD') ),
    type       VARCHAR (5)    CHECK (type IN ('sell', 'buy') ),
    amount     DOUBLE (20, 8),
    price      DOUBLE (20, 4),
    order_type VARCHAR (10)   CHECK (order_type IN ('market', 'limit') ),
    sys_date   DATETIME
)"""
}
#Очистка таблиц перед тестированием


if __name__ == '__main__':
    from db.connection import DBConnect

    conn = DBConnect().getConnect()
    cursor = conn.cursor()

    #INIT DB
    #for sql in queries_d.values():
    #    cursor.execute(sql)

    #CLEAR TABLES
