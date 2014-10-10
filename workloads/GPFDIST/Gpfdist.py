import os
import sys
import commands, socket, shutil
from datetime import datetime, date, timedelta

try:
    from workloads.Workload import *
except ImportError:
    sys.stderr.write('GPFDIST needs workloads/Workload.py\n')
    sys.exit(2)

try:
    from pygresql import pg
except ImportError:
    sys.stderr.write('GPFDIST needs pygresql\n')
    sys.exit(2)

try:
    from lib.PSQL import psql
except ImportError:
    sys.stderr.write('GPFDIST needs psql in lib/PSQL.py\n')
    sys.exit(2)

try:
    from lib.Config import config
except ImportError:
    sys.stderr.write('GPFDIST needs config in lib/Config.py\n')
    sys.exit(2)
    

class Gpfdist(Workload):
    def __init__(self, workload_specification, workload_directory, report_directory, report_sql_file, cs_id): 
        # init base common setting such as dbname, load_data, run_workload , niteration etc
        Workload.__init__(self, workload_specification, workload_directory, report_directory, report_sql_file, cs_id)
        self.fname = self.workload_directory + os.sep + 'gpfdist.lineitem.tbl'
        self.dss = self.workload_directory + os.sep + 'dists.dss'
        self.host_name = config.getMasterHostName()

    def setup(self):
        # check if the database exist
        try: 
            cnx = pg.connect(dbname = self.database_name)
        except Exception, e:
            cnx = pg.connect(dbname = 'postgres')
            cnx.query('CREATE DATABASE %s;' % (self.database_name))
        finally:
            cnx.close()

    def replace_sql(self, sql, table_name, num):
        sql = sql.replace('TABLESUFFIX', self.tbl_suffix)
        sql = sql.replace('SQLSUFFIX', self.sql_suffix)
        sql = sql.replace('NUMBER', str(num))
        sql = sql.replace('HOSTNAME', self.host_name)
        sql = sql.replace('GPFDIST_PORT', str(self.gpfdist_port))
        return sql


    def load_data(self):
        self.output('-- Start loading data ')

        # get the data dir
        data_directory = self.workload_directory + os.sep + 'data'
        if not os.path.exists(data_directory):
            self.output('ERROR: Cannot find DDL to create tables for Copy: %s does not exists' % (data_directory))
            return
        
        self.output('-- start gpfdist service')
        self.gpfdist_port = self._getOpenPort()

        cmd = "gpssh -h %s -e 'gpfdist -d %s -p %d -l ./gpfdist.log &' "% (self.host_name, self.workload_directory, self.gpfdist_port)
        (status, output) = commands.getstatusoutput(cmd)
        self.output(cmd)
        cmd = 'ps -ef | grep gpfdist'
        self.output(cmd)
        output = commands.getoutput(cmd)
        self.output(output)
        
        self.output('-- generate data file: %s' % (self.fname))
        cmd = "dbgen -b %s -s %d -T L > %s " % (self.dss, self.scale_factor, self.fname)
        (status, output) = commands.getstatusoutput(cmd)
        self.output(cmd)
        self.output(output)
        if status != 0:
            print("generate data file %s error. " % (self.fname))
            sys.exit(2)
        self.output('generate data file successed. ')

        tables = ['lineitem_gpfdist']
        
        niteration = 1
        while niteration <= self.num_iteration:
            self.output('-- Start iteration %d' % (niteration))
            if self.load_data_flag or self.run_workload_flag:
                for table_name in tables:
                    load_success_flag = True
                    qf_path = QueryFile(os.path.join(data_directory, table_name + '.sql'))
                    beg_time = datetime.now()
                    # run all sql in each loading data file
                    for cmd in qf_path:
                        cmd = self.replace_sql(sql = cmd, table_name = table_name, num = niteration)
                        self.output(cmd)
                        (ok, result) = psql.runcmd(cmd = cmd, dbname = self.database_name, flag = '')
                        self.output('RESULT: ' + str(result))
                        if not ok:
                            load_success_flag = False

                    end_time = datetime.now()
                    duration = end_time - beg_time
                    duration = duration.days*24*3600*1000 + duration.seconds*1000 + duration.microseconds /1000
          
                    if load_success_flag:    
                        self.output('   Loading=%s   Iteration=%d   Stream=%d   Status=%s   Time=%d' % (table_name, niteration, 1, 'SUCCESS', duration))
                        self.report('   Loading=%s   Iteration=%d   Stream=%d   Status=%s   Time=%d' % (table_name, niteration, 1, 'SUCCESS', duration))
                        self.report_sql("INSERT INTO hst.test_result VALUES (%d, %d, 'Loading', '%s', %d, 1, 'SUCCESS', '%s', '%s', %d, NULL, NULL, NULL);" 
                            % (self.tr_id, self.s_id, table_name, niteration, str(beg_time).split('.')[0], str(end_time).split('.')[0], duration))
                    else:
                        self.output('ERROR: Failed to load data for table %s' % (table_name))
                        self.report('   Loading=%s   Iteration=%d   Stream=%d   Status=%s   Time=%d' % (table_name, niteration, 1, 'ERROR', 0)) 
                        self.report_sql("INSERT INTO hst.test_result VALUES (%d, %d, 'Loading', '%s', %d, 1, 'ERROR', '%s', '%s', %d, NULL, NULL, NULL);" 
                            % (self.tr_id, self.s_id, table_name, niteration, str(beg_time).split('.')[0], str(end_time).split('.')[0], duration))
                
            else:
                beg_time = str(datetime.now()).split('.')[0]
                for table_name in tables:
                    self.output('   Loading=%s   Iteration=%d   Stream=%d   Status=%s   Time=%d' % (table_name, niteration, 1, 'SKIP', 0))
                    self.report('   Loading=%s   Iteration=%d   Stream=%d   Status=%s   Time=%d' % (table_name, niteration, 1, 'SKIP', 0)) 
                    self.report_sql("INSERT INTO hst.test_result VALUES (%d, %d, 'Loading', '%s', %d, 1, 'SKIP', '%s', '%s', 0, NULL, NULL, NULL);" 
                        % (self.tr_id, self.s_id, table_name, niteration, beg_time, beg_time))
                
            self.output('-- Complete iteration %d' % (niteration))
            niteration += 1

        cmd = "ps -ef|grep gpfdist|grep %s|grep -v grep|awk \'{print $2}\'|xargs kill -9" % (self.gpfdist_port)
        self.output(cmd)
        (status, output) = commands.getstatusoutput(cmd)
        self.output(output)
        self.output('kill gpfdist succeed. ')
        self.output('-- Complete loading data')      
    
    def _getOpenPort(self, port = 8050):
        defaultPort = port
        tryAgain = True
        s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        while tryAgain:
            try:
                s.bind( ( "localhost", defaultPort ) )
            except:
                defaultPort += 1
            finally:
                tryAgain = False
                s.close()
        return defaultPort
        
    
    def execute(self):
        self.output('-- Start running workload %s' % (self.workload_name))
        self.report('-- Start running workload %s' % (self.workload_name))

        # setup
        self.setup()

        # load data
        self.load_data()

        # clean up 
        self.clean_up()
        
        self.output('-- Complete running workload %s' % (self.workload_name))
        self.report('-- Complete running workload %s' % (self.workload_name))
