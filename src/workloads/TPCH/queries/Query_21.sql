-- start ignore
explain
select
 s_name,
 count(*) as numwait
from
 supplierTABLESUFFIX,
 lineitemTABLESUFFIX l1,
 ordersTABLESUFFIX,
 nationTABLESUFFIX
where
 s_suppkey = l1.l_suppkey
 and o_orderkey = l1.l_orderkey
 and o_orderstatus = 'F'
 and l1.l_receiptdate > l1.l_commitdate
 and exists (
 select
 *
 from
 lineitemTABLESUFFIX l2
 where
 l2.l_orderkey = l1.l_orderkey
 and l2.l_suppkey <> l1.l_suppkey
 )
 and not exists (
 select
 *
 from
 lineitemTABLESUFFIX l3
 where
 l3.l_orderkey = l1.l_orderkey
 and l3.l_suppkey <> l1.l_suppkey
 and l3.l_receiptdate > l3.l_commitdate
 )
 and s_nationkey = n_nationkey
 and n_name = 'RUSSIA'
group by
 s_name
order by
 numwait desc,
 s_name
LIMIT 100;
-- end ignore

select
 s_name,
 count(*) as numwait
from
 supplierTABLESUFFIX,
 lineitemTABLESUFFIX l1,
 ordersTABLESUFFIX,
 nationTABLESUFFIX
where
 s_suppkey = l1.l_suppkey
 and o_orderkey = l1.l_orderkey
 and o_orderstatus = 'F'
 and l1.l_receiptdate > l1.l_commitdate
 and exists (
 select
 *
 from
 lineitemTABLESUFFIX l2
 where
 l2.l_orderkey = l1.l_orderkey
 and l2.l_suppkey <> l1.l_suppkey
 )
 and not exists (
 select
 *
 from
 lineitemTABLESUFFIX l3
 where
 l3.l_orderkey = l1.l_orderkey
 and l3.l_suppkey <> l1.l_suppkey
 and l3.l_receiptdate > l3.l_commitdate
 )
 and s_nationkey = n_nationkey
 and n_name = 'RUSSIA'
group by
 s_name
order by
 numwait desc,
 s_name
LIMIT 100;
