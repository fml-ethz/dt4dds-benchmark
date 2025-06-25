import psutil
import pathlib
import dataclasses
import time

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ResourceStats():
    """ Collects resource stats of a subprocess. """

    _sum_cpu_percent = 0
    _sum_memory_percent = 0
    _sum_memory_value = 0
    n_data_points = 0

    cpu_percent = property(lambda self: self._sum_cpu_percent/max(self.n_data_points, 1))
    memory_percent = property(lambda self: self._sum_memory_percent/max(self.n_data_points, 1))
    memory_value = property(lambda self: self._sum_memory_value/max(self.n_data_points, 1))


    def update(self, process: psutil.Process):
        """ Will update the resource stats by adding the stats of the given process and all its children. """
        if not process.is_running(): return
        tot_cpu_percent, tot_memory_percent, tot_memory_value = self._get_process_stats(process)

        for pi in process.children(recursive=True):
            if pi.is_running():
                cpu_percent, memory_percent, memory_value = self._get_process_stats(pi)
                tot_cpu_percent += cpu_percent
                tot_memory_percent += memory_percent
                tot_memory_value += memory_value

        self._sum_cpu_percent += tot_cpu_percent
        self._sum_memory_percent += tot_memory_percent
        self._sum_memory_value += tot_memory_value
        self.n_data_points += 1

        
    def _get_process_stats(self, process: psutil.Process):
        """ Will return the CPU and memory stats of the given process. """
        cpu_percent = process.cpu_percent(interval=0.1)
        memory_percent = process.memory_percent('uss')
        memory_value = process.memory_full_info().uss / (1024.0 ** 3) # to GB

        return cpu_percent, memory_percent, memory_value

    
def kill_process_family(process):
    processes = process.children(recursive=True)
    processes.append(process)
    for p in processes:
        try:
            p.kill()
        except psutil.NoSuchProcess:
            pass
    gone, alive = psutil.wait_procs(processes, timeout=10)
    if alive:
        logger.warning(f"Some processes were not killed within timeout: [{','.join([str(p) for p in alive])}]")


@dataclasses.dataclass
class SubProcess():
    """  """

    command_args: list                      # list of arguments to pass to the subprocess
    monitor_interval: float = 0.2           # interval in seconds to collect subprocess resource data
    process_log_file: pathlib.Path = None   # path to the file to which the subprocess output will be written
    timeout: float = 1*60*60.0              # time in seconds until the subprocess is assumed to be dead and is killed

    process = None
    return_code = None
    start_time = None
    end_time = None
    resource_stats = None

    duration = property(lambda self: self.end_time - self.start_time)

    @property
    def metadata(self):
        """ Returns a dict with the metadata of the finished subprocess. """
        return {
            'return_code': self.return_code,
            'duration': self.duration,
            'cpu_percent': self.resource_stats.cpu_percent,
            'memory_percent': self.resource_stats.memory_percent,
            'memory_value': self.resource_stats.memory_value,
        }


    def __post_init__(self):

        # create the log file handler if enabled
        if self.process_log_file is not None:
            self.process_log_file.parent.mkdir(parents=True, exist_ok=True)
            stdout = self.process_log_file.open('w')
        else:
            stdout = None

        # start the process
        self.start_time = time.time()
        self.resource_stats = ResourceStats()
        logger.debug(f"Starting subprocess: {' '.join(self.command_args)}")
        self.process = psutil.Popen(self.command_args, stdout=stdout, stderr=stdout)

        # wait for the process to finish, while collecting resource stats and monitoring time-out
        last_update = 0
        while self.process.poll() is None:

            # check for resource stats update
            if time.time()-last_update > self.monitor_interval:
                try:
                    self.resource_stats.update(self.process)
                    last_update = time.time()
                except psutil.NoSuchProcess:
                    pass

            # check for time-out
            if time.time() - self.start_time > self.timeout:
                logger.critical(f"Subprocess timed out after {self.timeout} seconds, killing it.")
                kill_process_family(self.process)
                break

            # sleep for a bit
            time.sleep(0.05)

        # assign return code and end time
        self.return_code = self.process.wait()
        self.end_time = time.time()
