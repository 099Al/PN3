#Создание таблиц в Базе

queries_d ={
  'im_cex_history_tik':
    """CREATE TABLE im_cex_history_tik (
    tid      BIGINT          PRIMARY KEY ASC ON CONFLICT ROLLBACK,
    unixdate BIGINT,
    date     DATETIME,
    side     CHAR (6),
    amount   DECIMAL (11, 8),
    price    DECIMAL (9, 2),
    trade_data STRING (1000) 
    
)"""

,'im_stg_cex_history_tik':
    """CREATE TABLE im_stg_cex_history_tik (
    tid      BIGINT          PRIMARY KEY ASC ON CONFLICT ROLLBACK,
    unixdate BIGINT,
    date     DATETIME,
    side     CHAR (6),
    amount   DECIMAL (11, 8),
    price    DECIMAL (9, 2),
    trade_data STRING (1000)   
)"""

#im_balance - аналог баланса на сайте. Обновляется во время тестовых рассчетов
,'im_balance':"""CREATE TABLE im_balance (
    curr      CHAR (5),
    amount    decimal(15,8),
    reserved  decimal(15,8)
    , CONSTRAINT PK_ID PRIMARY KEY (curr));
   insert into im_balance valuest('BTC',0,0);
   insert into im_balance valuest('USD',0,0);
    """

#активный ордер. аналог записи на сайте
,'im_active_orders':
    """CREATE TABLE im_active_orders (
    id         INTEGER        PRIMARY KEY,
    date       DATETIME,
    unix_date  INTEGER,
    base       CHAR (5),
    quote      CHAR (5),
    side       VARCHAR (5)    CHECK (side IN ('sell', 'buy') ),
    amount     DOUBLE (20, 8),
    price      DOUBLE (20, 4),
    reserved   DOUBLE (20, 4),
    order_type VARCHAR (10)   CHECK (order_type IN ('market', 'limit') ),
    full_traid TEXT,
    algo        CHAR (20),
    sys_date   DATETIME
)"""

,'im_transactions':
    """CREATE TABLE im_transactions (
    
    order_id INTEGER,
    order_amount   DECIMAL (11, 8),
    order_price    DECIMAL (9, 2),
    order_reserved   DOUBLE (20, 4),
    order_side     CHAR (6),
    
    tid      BIGINT,          
    unixdate BIGINT,
    date     DATETIME,
    
    transact_info TEXT
)"""


#history_tik - таблица для хранения данных полученный с источника (сайта или эмуляции)
,'history_tik':
    """CREATE TABLE cex_history_tik (
    tid        BIGINT          PRIMARY KEY ASC ON CONFLICT ROLLBACK,
    side       CHAR (6),
    unixdate   BIGINT,
    date       DATETIME,
    amount     DECIMAL (11, 8),
    price      DECIMAL (9, 2),
    base       CHAR (6),
    sys_insert DATETIME
)"""

#таблица для временного хранения данных для наполнения таблицы history_tik
,'stg_history_tik':
    """CREATE TABLE stg_cex_history_tik (
    tid      BIGINT,
    side     CHAR (6),
    unixdate BIGINT,
    date     DATETIME,
    amount   DECIMAL (11, 8),
    price    DECIMAL (9, 2),
    base     CHAR (6)
)"""

,'active_orders':
    """CREATE TABLE active_orders (
    id         INTEGER        PRIMARY KEY,
    date       DATETIME,
    unix_date  INTEGER,
    base       CHAR (5),
    quote      CHAR (5),
    side       VARCHAR (5)    CHECK (side IN ('sell', 'buy') ),
    amount     DOUBLE (20, 8),
    price      DOUBLE (20, 4),
    reserved   DOUBLE (20, 4),
    order_type VARCHAR (10)   CHECK (order_type IN ('market', 'limit') ),
    full_traid TEXT,
    algo        CHAR (20),
    sys_date   DATETIME
)"""

,'log_orders':"""CREATE TABLE log_orders (
    status   CHAR (15)  CHECK (status IN ('NEW','CANCELED','DONE','REJECTED') ),
    id         CHAR (20),
    side       CHAR (5)  CHECK (side IN ('SELL', 'BUY') ),
    date       DATETIME,
    unixdate   INTEGER,
    base       CHAR (5),
    quote      CHAR (5),
    amount     DECIMAL (15, 8),
    price      DECIMAL (15, 8),
    reserved      DECIMAL (15, 8),
    fee        DECIAML (15, 2),
    reject_reason TEXT,
    order_type VARCHAR (10)   CHECK (order_type IN ('market', 'limit') ),
    expire     INTEGER,
    full_traid TEXT,
    algo        CHAR (20),
    flag_reason TEXT,
    CONSTRAINT PK_ID_STATUS PRIMARY KEY (
        status,
        id
    )
)"""


#balance - повторояет таблицу im_balance. Заносится баланс, рассчитанный по алгоритмам. В режиме TRAID может отличаться от того, что на самом деле
,'balance':"""CREATE TABLE balance (
    curr      CHAR (5),
    amount    decimal(15,8),
    reserved  decimal(15,8)
    , CONSTRAINT PK_ID PRIMARY KEY (curr)
)"""

,'log_balance':"""CREATE TABLE log_balance (
    date      DATETIME,
    unix_date INTEGER,
    curr      CHAR (5),
    amount    DECIMAL (15, 8),
    algo_name  CHAR (20),
    tid       CHAR (30),
    activity CHAR (20)   CHECK (activity IN ('BUY', 'SELL','DONE','CANCELED') ),
    sys_date DATETIME
    )
    """

}
#Очистка таблиц перед тестированием


if __name__ == '__main__':
    from trade_data.db.connection import DBConnect

    conn = DBConnect().getConnect()
    cursor = conn.cursor()

    #INIT DB
    #for sql in queries_d.values():
    #    cursor.execute(sql)

    #CLEAR TABLES
