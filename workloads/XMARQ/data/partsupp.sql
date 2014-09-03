DROP TABLE IF EXISTS partsupp_TABLESUFFIX;
DROP EXTERNAL WEB TABLE IF EXISTS e_partsupp_TABLESUFFIX;

CREATE TABLE partsupp_TABLESUFFIX (
    PS_PARTKEY     INTEGER NOT NULL,
    PS_SUPPKEY     INTEGER NOT NULL,
    PS_AVAILQTY    INTEGER NOT NULL,
    PS_SUPPLYCOST  DECIMAL(15,2)  NOT NULL,
    PS_COMMENT     VARCHAR(199) NOT NULL )
WITH (SQLSUFFIX);

CREATE EXTERNAL WEB TABLE e_partsupp_TABLESUFFIX (
    PS_PARTKEY     INTEGER,
    PS_SUPPKEY     INTEGER,
    PS_AVAILQTY    INTEGER,
    PS_SUPPLYCOST  DECIMAL(15,2),
    PS_COMMENT     VARCHAR(199) ) 
EXECUTE 'bash -c \"$GPHOME/bin/dbgen -b $GPHOME/bin/dists.dss -T S -s SCALEFACTOR -N NUMSEGMENTS -n $((GP_SEGMENT_ID + 1))\"'
ON NUMSEGMENTS FORMAT 'TEXT' (DELIMITER '|');

INSERT INTO partsupp_TABLESUFFIX SELECT * FROM e_partsupp_TABLESUFFIX;
