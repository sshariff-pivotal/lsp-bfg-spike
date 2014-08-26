-- start ignore
explain
select
 supp_nation,
 cust_nation,
 l_year,
 sum(volume) as revenue
from
 (
 select
 n1.n_name as supp_nation,
 n2.n_name as cust_nation,
 extract(year from l_shipdate) as l_year,
 l_extendedprice * (1 - l_discount) as volume
 from
 TABLESUFFIX_supplier,
 TABLESUFFIX_lineitem,
 TABLESUFFIX_orders,
 TABLESUFFIX_customer,
 TABLESUFFIX_nation n1,
 TABLESUFFIX_nation n2
 where
 s_suppkey = l_suppkey
 and o_orderkey = l_orderkey
 and c_custkey = o_custkey
 and s_nationkey = n1.n_nationkey
 and c_nationkey = n2.n_nationkey
 and (
 (n1.n_name = 'MOROCCO' and n2.n_name = 'ETHIOPIA')
 or (n1.n_name = 'ETHIOPIA' and n2.n_name = 'MOROCCO')
 )
 and l_shipdate between date '1995-01-01' and date '1996-12-31'
 ) as shipping
group by
 supp_nation,
 cust_nation,
 l_year
order by
 supp_nation,
 cust_nation,
 l_year;
-- end ignore



select
 supp_nation,
 cust_nation,
 l_year,
 sum(volume) as revenue
from
 (
 select
 n1.n_name as supp_nation,
 n2.n_name as cust_nation,
 extract(year from l_shipdate) as l_year,
 l_extendedprice * (1 - l_discount) as volume
 from
 TABLESUFFIX_supplier,
 TABLESUFFIX_lineitem,
 TABLESUFFIX_orders,
 TABLESUFFIX_customer,
 TABLESUFFIX_nation n1,
 TABLESUFFIX_nation n2
 where
 s_suppkey = l_suppkey
 and o_orderkey = l_orderkey
 and c_custkey = o_custkey
 and s_nationkey = n1.n_nationkey
 and c_nationkey = n2.n_nationkey
 and (
 (n1.n_name = 'MOROCCO' and n2.n_name = 'ETHIOPIA')
 or (n1.n_name = 'ETHIOPIA' and n2.n_name = 'MOROCCO')
 )
 and l_shipdate between date '1995-01-01' and date '1996-12-31'
 ) as shipping
group by
 supp_nation,
 cust_nation,
 l_year
order by
 supp_nation,
 cust_nation,
 l_year;
