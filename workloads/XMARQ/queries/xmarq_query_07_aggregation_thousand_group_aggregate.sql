-- START_IGNORE
EXPLAIN
SELECT
 l_receiptdate,
 COUNT(*) AS num
FROM
 lineitem_TABLESUFFIX
GROUP BY
 l_receiptdate
ORDER BY
 l_receiptdate;
-- EDN_IGNORE

SELECT
 l_receiptdate,
 COUNT(*) AS num
FROM
 lineitem_TABLESUFFIX
GROUP BY
 l_receiptdate
ORDER BY
 l_receiptdate;
