import os
import sys
from datetime import datetime, date, timedelta

try:
    from workloads.Workload import *
except ImportError:
    sys.stderr.write('TPCH needs workloads/Workload.py\n')
    sys.exit(2)

try:
    from pygresql import pg
except ImportError:
    sys.stderr.write('TPCH needs pygresql\n')
    sys.exit(2)

try:
    from lib.PSQL import psql
except ImportError:
    sys.stderr.write('TPCH needs psql in lib/PSQL.py\n')
    sys.exit(2)

try:
    from lib.QueryFile import QueryFile
except ImportError:
    sys.stderr.write('TPCH needs QueryFile in lib/QueryFile.py\n')
    sys.exit(2)


class Tpch(Workload):

    def __init__(self, workload_specification, workload_directory, report_directory, report_sql_file, cs_id): 
        # init base common setting such as dbname, load_data, run_workload , niteration etc
        Workload.__init__(self, workload_specification, workload_directory, report_directory, report_sql_file, cs_id)

    def setup(self):
        # check if the database exist
        try: 
            cnx = pg.connect(dbname = self.database_name)
        except Exception, e:
            cnx = pg.connect(dbname = 'postgres')
            cnx.query('CREATE DATABASE %s;' % (self.database_name))
        finally:
            cnx.close()

    def get_partition_suffix(self, num_partitions = 128, table_name = ''):
        beg_date = date(1992, 01, 01)
        end_date = date(1998, 12, 31)
        duration_days = int(round(float((end_date - beg_date).days) / float(num_partitions)))

        part = ''

        if table_name == 'lineitem':
            part = '''PARTITION BY RANGE(l_shipdate)\n    (\n'''
        elif table_name == 'orders':
            part = '''PARTITION BY RANGE(o_orderdate)\n    (\n'''
                
        for i in range(1, num_partitions+1):
            beg_cur = beg_date + timedelta(days = (i-1)*duration_days)
            end_cur = beg_date + timedelta(days = i*duration_days)

            part += '''        PARTITION p1_%s START (\'%s\'::date) END (\'%s\'::date) EVERY (\'%s days\'::interval) WITH (tablename=\'%s_part_1_prt_p1_%s\', %s )''' % (i, beg_cur, end_cur, duration_days, table_name + '_' + self.tbl_suffix, i, self.sql_suffix)
            
            if i != num_partitions:
                part += ''',\n'''
            else:
                part += '''\n'''

        part += '''    )'''
                
        return part 

    def replace_sql(self, sql, table_name):
        sql = sql.replace('TABLESUFFIX', self.tbl_suffix)
        sql = sql.replace('SQLSUFFIX', self.sql_suffix)
        sql = sql.replace('SCALEFACTOR', str(self.scale_factor))
        sql = sql.replace('NUMSEGMENTS', str(self.nsegs))
        if self.partitions == 0 or self.partitions is None:
            sql = sql.replace('PARTITIONS', '')
        else:
            part_suffix = self.get_partition_suffix(num_partitions = self.partitions, table_name = table_name)
            sql = sql.replace('PARTITIONS', part_suffix)
        return sql

    def load_data(self):
        self.output('-- Start loading data')

        # get the data dir
        data_directory = self.workload_directory + os.sep + 'data'
        if not os.path.exists(data_directory):
            self.output('ERROR: Cannot find DDL to create tables for TPC-H: %s does not exists' % (data_directory))
            sys.exit(2)

        tables = ['nation', 'region', 'part', 'supplier', 'partsupp', 'customer', 'orders','lineitem' ,'revenue']
        for table_name in tables:
            if self.continue_flag:
                if self.load_data_flag:
                    with open(data_directory + os.sep + table_name + '.sql', 'r') as f:
                        cmd = f.read()
                    cmd = self.replace_sql(sql = cmd, table_name = table_name)
                    with open('tpch_loading_data_tmp.sql', 'w') as f:
                        f.write(cmd)

                    self.output(cmd)
                    beg_time = datetime.now()
                    (ok, result) = psql.runfile(ifile = 'tpch_loading_data_tmp.sql', dbname = self.database_name)
                    end_time = datetime.now()
                    self.output('RESULT: ' + str(result))

                    if ok:
                        status = 'SUCCESS'
                    else:
                        status = 'ERROR'
                        self.continue_flag = False
                else:
                    status = 'SKIP'
                    beg_time = datetime.now()
                    end_time = beg_time
            else:
                status = 'ERROR'
                beg_time = datetime.now()
                end_time = beg_time
                
            duration = end_time - beg_time
            duration = duration.days*24*3600*1000 + duration.seconds*1000 + duration.microseconds /1000
            beg_time = str(beg_time).split('.')[0]
            end_time = str(end_time).split('.')[0]         
            self.output('   Loading=%s   Iteration=%d   Stream=%d   Status=%s   Time=%d' % (table_name, 1, 1, status, duration))
            self.report_sql("INSERT INTO hst.test_result VALUES (%d, %d, 'Loading', '%s', 1, 1, '%s', '%s', '%s', %d, NULL, NULL, NULL);" 
                % (self.tr_id, self.s_id, table_name, status, beg_time, end_time, duration))
               
        self.output('-- Complete loading data')

            
    
    def execute(self):
        self.output('-- Start running workload %s' % (self.workload_name))

        # setup
        self.setup()

        # load data
        self.load_data()

        # vacuum_analyze
        if self.load_data_flag:
            self.vacuum_analyze()

        # run workload concurrently and loop by iteration
        self.run_workload()

        # clean up 
        self.clean_up()
        
        self.output('-- Complete running workload %s' % (self.workload_name))
