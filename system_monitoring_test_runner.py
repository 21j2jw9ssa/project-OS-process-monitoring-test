"""
System test harness:

What this script demonstrates:
1. Controlled workload generation
2. Concurrent system monitoring
3. Post-run evaluation of system behavior

Designed to simulate how datacenter system tests
validate telemetry under load.
"""

import time      # For CPU loading processes
import datetime  # For issuing current date and time
import threading
from src.monitor import PrintAndLog, clearScreen, getSnapshot, OS_monitoring_summary
from src.evaluator import evaluate
from src.workload import cpu_load

snapshots = []
times_snapshots = []

def monitor_loop(duration, procList):
  """
  A monitoring tester that observes the processes
  in the operating system.

  What this function can do:
  - prevent runaway or unexpected/undefined threads
  - make small-scaled tests deterministic
  - keep execution logic simple
  """
  end = time.time() + duration
  while time.time() < end:
    now = time.time()
    times_snapshots.append( datetime.datetime.now().strftime( "at %H:%M:%S on %Y-%m-%d" ) ) ;
    snapshots.append( getSnapshot(now, procList) )
    time.sleep(1)

def print_monitor_test_result(all_results):
  LOG_TEST_FILE = datetime.datetime.now().strftime( "system_monitoring-test-%Y-%m-%d-%H_%M_%S.txt" )

  resultCtnt = f"Total snapshots taken during the monitoring test: { len(all_results) }\n\n"

  for i in range( len(all_results) ):
    cpuExceed = all_results[i]["cpu_violations"]
    memExceed = all_results[i]["mem_violations"]
    runExceed = all_results[i]["runtime_violations"]

    resultCtnt += OS_monitoring_summary(
      times_snapshots[i], snapshots[i],
      cpuExceed, memExceed, runExceed
    ) ;

    if i + 1 < len(all_results):
      resultCtnt += '\n' + "-" * 120 + "\n\n"

  PrintAndLog(resultCtnt, file=LOG_TEST_FILE)

if __name__ == "__main__":
  clearScreen()

  # duration spent in testing; in seconds
  DURATION = 10

  # How much of an interval to spent on work for CPU load, in percent (%)
  WORK_PERCENTAGE = 70

  print( "This test will monitor the resources in the operating system.\n" )
  print( f"It will last about {DURATION} { "second" if DURATION == 1 else "seconds" },", end="\n" )
  print( f"with {WORK_PERCENTAGE}% of the time spent on CPU loading.\n")
  print( "Now testing monitoring processes..." )

  # Processes to monitor with specific names.
  # Only will the following processes be monitored.
  # When the following list is empty, though,
  # every process available will be monitored all together.

  # This process list will monitor all the processes shown in the following list.
  # If not specified, all processes will be monitored.
  # You may change the processes to monitor as needed.
  procList = [
    # "MicrosoftSecurityApp.exe",   # Microsoft security
    # "chrome.exe",                 # Chrome browser
    "dwm.exe",                    # Desktop window manager
    "OneDrive.exe",               # OneDrive cloud
    "SafeConnect.Entry.exe"       # McAfee Safe Connect
  ] ;

  # Two threads (can be executed concurrently)
  thread_monitorSysProcs = threading.Thread( target=monitor_loop, args=( DURATION, procList ) )
  thread_loads_of_CPU = threading.Thread( target=cpu_load, args=( WORK_PERCENTAGE, DURATION ) )

  thread_monitorSysProcs.start()
  thread_loads_of_CPU.start()

  thread_monitorSysProcs.join()
  thread_loads_of_CPU.join()

  # Evaluation phase (no side effects)
  all_results = []

  for s in snapshots:
    # Threshold setup:
    # CPU usage: 70%
    # memory usage: 500MB
    # running time: 3600 seconds since started
    all_results.append( evaluate( s, 70, 500, 3600 ) )

  clearScreen()
  print_monitor_test_result(all_results)
  print( f"Test completed." )
