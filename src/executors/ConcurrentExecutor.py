import os
from datetime import datetime
from multiprocessing import Process, Queue, Value , Array

try:
    from Executor import Executor
except ImportError:
    sys.stderr.write('LSP needs Executor in src/executors/Executor.py.\n')
    sys.exit(2)

LSP_HOME = os.getenv('LSP_HOME')

class ConcurrentExecutor(Executor):
    def __init__(self, workloads_dict):
        Executor.__init__(self, workloads_dict)
        self.AllProcess = []

    def cleanup(self):
        ''' cleanup function , will be called after execution'''
        pass

    def handle_workload_done(self, process):
        ''' function that called every time when current workload has done'''
        pass

    def handle_workload_not_done(self, process):
        ''' function that called evert time when current workload not done'''
        pass

    def execute(self):
        # init workload and setup directories before execution
        self.setup()

        # routine of workload running 
        for workload in self.workloads:
            p = Process(target=workload.start)
            self.AllProcess.append(p)
            p.start()
 
        while True and not self.should_stop:
            for process in self.AllProcess[:]:
                process.join(timeout = 1)
                if process.is_alive():
                    self.handle_workload_not_done(process)
                    continue
                else:
                    self.handle_workload_done(process)
                    self.AllProcess.remove(process)
                    if len(self.AllProcess) == 0:
                        self.should_stop = True



        # clean up after execution 
        
        self.cleanup()
