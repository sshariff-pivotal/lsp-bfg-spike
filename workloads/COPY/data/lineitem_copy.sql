DROP TABLE IF EXISTS lineitem_TABLESUFFIX_copy_NUMBER CASCADE;

CREATE TABLE lineitem_TABLESUFFIX_copy_NUMBER ( 
    L_ORDERKEY INTEGER ,
    L_PARTKEY INTEGER ,
    L_SUPPKEY INTEGER ,
    L_LINENUMBER INTEGER ,
    L_QUANTITY DECIMAL(15,2) ,
    L_EXTENDEDPRICE DECIMAL(15,2) ,
    L_DISCOUNT DECIMAL(15,2) ,
    L_TAX DECIMAL(15,2) ,
    L_RETURNFLAG CHAR(1) ,
    L_LINESTATUS CHAR(1) ,
    L_SHIPDATE DATE ,
    L_COMMITDATE DATE ,
    L_RECEIPTDATE DATE ,
    L_SHIPINSTRUCT CHAR(25) ,
    L_SHIPMODE CHAR(10) ,
    L_COMMENT VARCHAR(44) ) 
WITH (SQLSUFFIX)
DISTRIBUTED BY(L_ORDERKEY);

COPY lineitem_TABLESUFFIX_copy_NUMBER FROM 'FNAME' WITH DELIMITER '|' SEGMENT REJECT LIMIT 10 ROWS;
