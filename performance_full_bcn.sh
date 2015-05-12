#!/bin/sh

source ~/.bashrc
source ~/qa.sh

hawqconfig -c default_segment_num -v 64
hawqconfig -c hawq_resourcemanager_query_vsegment_number_per_segment_limit -v 4
hawq stop cluster -a
hawq start cluster -a
psql -d postgres -c "drop table if exists test; create table test(a int); insert into test values (1);"
sleep 20

python -u lsp.py -s performance_tpch_10g  -c  > ./performance_tpch_10g.log 2>&1
sleep 10
python -u lsp.py -s performance_tpch_200g_full  -c > ./performance_tpch_200g.log 2>&1
sleep 10
#python -u lsp.py -s performance_xmarq_200g  > ./performance_xmarq_200g.log 2>&1
#sleep 10
python -u lsp.py -s performance_tpch_stream  -c > ./performance_tpch_stream.log 2>&1
sleep 10
python -u lsp.py -s performance_tpch_concurrent  -c  > ./performance_tpch_concurrent.log 2>&1
