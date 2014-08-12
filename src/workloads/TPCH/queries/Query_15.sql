-- start ignore
explain
select
 s_suppkey,
 s_name,
 s_address,
 s_phone,
 total_revenue
from
 supplierTABLESUFFIX,
 revenue
where
 s_suppkey = supplier_no
 and total_revenue = (
 select
 max(total_revenue)
 from
 revenue
 )
order by
 s_suppkey;
-- end ignore

select
 s_suppkey,
 s_name,
 s_address,
 s_phone,
 total_revenue
from
 supplierTABLESUFFIX,
 revenue
where
 s_suppkey = supplier_no
 and total_revenue = (
 select
 max(total_revenue)
 from
 revenue
 )
order by
 s_suppkey;
