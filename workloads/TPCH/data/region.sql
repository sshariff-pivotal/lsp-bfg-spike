DROP TABLE IF EXISTS region_TABLESUFFIX;
DROP EXTERNAL WEB TABLE IF EXISTS e_region_TABLESUFFIX;

CREATE TABLE region_TABLESUFFIX (
    R_REGIONKEY  INTEGER NOT NULL,
    R_NAME       CHAR(25) NOT NULL,
    R_COMMENT    VARCHAR(152) )
WITH (SQLSUFFIX)
DISTRIBUTED BY(R_REGIONKEY);

CREATE EXTERNAL WEB TABLE e_region_TABLESUFFIX (
    R_REGIONKEY  INTEGER,
    R_NAME       CHAR(25),
    R_COMMENT    VARCHAR(152) )
EXECUTE E'bash -c "$GPHOME/bin/dbgen -b $GPHOME/bin/dists.dss -T r -s SCALEFACTOR"' ---N NUMSEGMENTS -n $((GP_SEGMENT_ID + 1))"' 
ON 1 FORMAT 'TEXT' (DELIMITER '|');

INSERT INTO region_TABLESUFFIX SELECT * FROM e_region_TABLESUFFIX;
