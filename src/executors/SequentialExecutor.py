import os
from datetime import datetime
from multiprocessing import Process, Queue, Value , Array

try:
    from Executor import Executor
except ImportError:
    sys.stderr.write('LSP needs Executor in src/executors/Executor.py.\n')
    sys.exit(2)

LSP_HOME = os.getenv('LSP_HOME')

class SequentialExecutor(Executor):
    def __init__(self, workloads_list, workloads_content):
        Executor.__init__(self, workloads_list, workloads_content)
        self.AllProcess = []

    def handle_finished_workload(self, pid):
        '''routine to handle the situation when workload is finished'''
        pass

    def handle_ongoing_workload(self, pid):
        '''routine to handle the situation when workload is ongoing'''
        pass

    def cleanup(self):
        '''routine clean up environment after all workloads are finished'''
        pass

    def execute(self):
        # instantiate and prepare workloads, prepare report directory
        self.setup()

        # execute workloads sequentially
        for wl in self.workloads_inst:
            p = Process(target=wl.start)
            p.start()
            while True:
                if p.is_alive():
                    self.handle_ongoing_workload(p)
                else:
                    break

        # clean up environment after all workload are finished
        self.cleanup()
