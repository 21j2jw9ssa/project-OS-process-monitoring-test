"""
Operating system resource monitor

What this script does:
- show specified processes
- indicate problematic processes
- gives users suggestions to resolve problematic processes
"""

import os          # To detect system resources
import psutil      # necessary for system monitoring, particularly for industrial purposes
import time        # for monitoring for a fixed period
import datetime
from pathlib import Path

# Base directory to save a log file
BASE_DIR = Path(__file__).parent.resolve().parent
DATA_DIR = BASE_DIR / "logs"

# Create a directory similar to "./../logs" if not exist
DATA_DIR.mkdir(exist_ok=True)

INTERVAL = 59.7    # time gap between each monitoring, in seconds

# Threshold values to demonstrate system warnings if passed
THRESHOLD_CPU = 70.0        # as percent (%)
THRESHOLD_MEM = 500.0       # as MB
THRESHOLD_RUNTIME = 3600    # seconds

# Fields to draw a table sheet
FIELDS = [
  {"name": "process_id",   "column_width": 10, "align": "right", "format": "{x}" },
  {"name": "process_name", "column_width": 50, "align": "left",  "format": "{x}"},
  {"name": "cpu_usage",    "column_width": 9,  "align": "right", "format": "{x:.1f} %"},
  {"name": "memory_usage", "column_width": 12, "align": "right", "format": "{x:.1f} MB"},
  {"name": "runtime",      "column_width": 13, "align": "right", "format": "{x:d} sec." }
]





def Process(pid:int, name:str, cpu_usage, memory_usage, runtime:int):
  """
  Docstring for Process

  :type pid: int
  :param pid: identifying number of this process

  :type name: str
  :param name: Description

  :type cpu_usage: float
  :param cpu_usage: how much CPU has been consumed by this process, in percent (%)

  :type cpu_usage: float
  :param memory_usage: how much memory has been occupied by this process, in MB

  :type runtime: int
  :param runtime: how long has this process been running since started up, in seconds
  """
  return {
    "process_id": pid,
    "process_name": name,
    "cpu_usage": cpu_usage,
    "memory_usage": memory_usage,
    "runtime": runtime
  }





def PrintAndLog(str :str="", end :str="\n", file :str="OS_process_monitoring-log.txt"):
  """
  Write a line of text to a new file.

  Then print a line of text in the terminal.
  """

  # The full path to the log file
  path = DATA_DIR / file

  with path.open("a", encoding="utf-8") as f:
    f.write(str)
    f.write(end)
  print( str, end=end )





def apply_format(value, template):
  """
  use for formatting values in strings
  
  :param value: string to substitute into the template
  :param template: string template where value can be substituted
  """
  return template.format(x=value)





def drawSeparationLine(fields, file):
  """
  How length of a horizontal border in sheets is calculated:
  - Calculate how many spaces all headers' names uses.
  - Count gaps for each header: 1 space on both the left side and the right side
  - Count straight lines that separate headers from each other

    number of headers + 1
    
  For example:
  ```
  +--------+------+---------+
  | SAMPLE | DEMO | EXAMPLE |
  +--------+------+---------+
  ```

  Length of the `SAMPLE` header:  6 chars + 1 left gap + 1 right gap = 8 spaces (dashes)

  Length of the `DEMO` header:    4 chars + 1 left gap + 1 right gap = 6 spaces (dashes)
    
  Length of the `EXAMPLE` header: 7 chars + 1 left gap + 1 right gap = 9 spaces (dashes)

  Plus signs needed for all headers: 3 headers + 1 = 4 spaces (plus signs)
  """
  line = ""
  for field in fields:
    line += f"+{ "-" * ( 1 + field['column_width'] + 1 ) }"
  line += "+"
  PrintAndLog( line, file=file )





def logHeader(fields, file):
  """
  Print fields and their names in a table sheet
  
  :param fields: a field tuple
  :param file: file to write headers to
  """
  for field in fields:
    PrintAndLog( f"| { field['name']:<{ field['column_width'] }}", end=" ", file=file )
  PrintAndLog( "|", file=file )





def logRowInfo(fields, row, file):
  """
  Docstring for logRowInfo
  
  :param fields: a field tuple
  :param row: a row of data
  :param file: file to write the row info to
  """
  PrintAndLog("| ", end="", file=file)

  # print the record in different field values
  for i in range( len(FIELDS) ):
    if FIELDS[i]["align"] == "right":
      PrintAndLog( f"{apply_format( row[ FIELDS[i]["name"] ], fields[i]['format'] ):>{fields[i]['column_width']}}", end=" | ",  file=file )
    else:
      PrintAndLog( f"{apply_format( row[ FIELDS[i]["name"] ], fields[i]['format'] ):<{fields[i]['column_width']}}", end=" | ",  file=file )
  PrintAndLog("", file=file)





def LogProcessTable(rows, file):
  """
  Print a table of processes
  """
  if len(rows) == 0:
    return
  for f in FIELDS:

    # how many spaces the unit occupies in the table. Set to zero by default unless specified
    unitOccupySpaces = 0

    if f["name"] == "cpu_usage":      # uses percent (%), occupies 2 spaces
      unitOccupySpaces = 2
    elif f["name"] == "memory_usage": # uses megabytes (Windows' MB), occupies 3 spaces
      unitOccupySpaces = 3
    elif f["name"] == "runtime":      # uses seconds (sec.), occupies 5 spaces
      unitOccupySpaces = 5

    # Find the value of a specific field that occupies the most spaces...
    maxValueLength = max( [ len( str( r[ f["name"] ] ) ) + unitOccupySpaces for r in rows ] )

    # ...then find the value of the header that occupies the most spaces.
    headerValueLength = len( f["name"] )

    # Finally, set the more spacious one as the column width of the current field
    f["column_width"] = max( maxValueLength, headerValueLength )

  # Draw headers of the sheet
  drawSeparationLine( FIELDS, file )
  logHeader( FIELDS, file )
  drawSeparationLine( FIELDS, file )

  # Draw all rows of the sheet
  for i in range( len(rows) ):
    logRowInfo( FIELDS, rows[i], file )
  drawSeparationLine( FIELDS, file )





def getSnapshot( curTimeInSec: int | float, procList ):
  """
  Get a snapshot to test OS monitoring system
  """
  snapshots = []

  for proc in psutil.process_iter(
    attrs=["pid", "name", "cpu_percent", "memory_info", "create_time"]
  ):
    try:
      if len(procList) > 0 and proc.info["name"] not in procList:
        continue

      procId = int( proc.info["pid"] )                           # process id
      procName = proc.info["name"]                               # process name (may not be unique)

      CPU_COUNT = psutil.cpu_count(True) ;
      procCPU = round( proc.info["cpu_percent"] / CPU_COUNT, 1 ) # CPU usage in percentage

      # Memory usage in megabytes.
      # RSS shows memory consumption of a process when it runs alone
      # and shares nothing with other processes.
      #
      # In practice, though, libraries are often shared among several processes,
      # causing RSS to overestimate the memory consumption
      #
      # This parameter, i.e. proc.info['memory_info'], is originally recorded as bytes.
      #
      # Since Windows' MB is equivalent to MiB, which is equal to
      # 1024 KiB and 1024 x 1024 B,
      # this parameter is divided by 1024 twice to display the memory usage in Windows' MB.
      procMem = round( float( proc.info['memory_info'].rss / 1024 / 1024 ), 1 )

      # Time running since started up, in seconds
      procRuntime = int( curTimeInSec - proc.info["create_time"] )

      curProc = Process( procId, procName, procCPU, procMem, procRuntime )
      snapshots.append( curProc )

    except (psutil.NoSuchProcess, psutil.AccessDenied):
      continue

  return snapshots





def format_duration(secs):
  """
  Converts a number of seconds into a readable string in a human-readable format,
  such as "10 hours, 20 minutes and 30 seconds".
  """
  nHrs :int = 0
  nMins:int = 0
  nSecs:int = secs
  while nSecs >= 3600:
    nSecs -= 3600
    nHrs += 1
  while nSecs >= 60:
    nSecs -= 60
    nMins += 1
  hourInfo = f"{ "1 hour" if nHrs == 1 else ( "" if nHrs == 0 else f"{nHrs} hours" ) }"
  minInfo =  f"{ "1 minute" if nMins == 1 else ( "" if nMins == 0 else f"{nMins} minutes" ) }"
  secInfo =  f"{ "1 second" if nSecs == 1 else ( "" if nSecs == 0 else f"{nSecs} seconds" ) }"
  hrMinConcat = f"{ ( ( ( ", " if nSecs > 0 else " and " ) if nMins > 0 else "" ) if nMins > 0 or nSecs > 0 else "" ) if nHrs > 0 else "" }"
  minSecConcat = f"{ ( ( " and " if nHrs > 0 or nMins > 0 else "" ) if nSecs > 0 else "" ) }"
  return f"{hourInfo}{hrMinConcat}{minInfo}{minSecConcat}{secInfo}" if nHrs > 0 or nMins > 0 or nSecs > 0 else "0 seconds"





def clearScreen():
  """
  Clear terminal screen.
  Does not affect log file-writing.
  """
  # clears the terminal
  # For Windows: "cls"
  # For MacOS, Linux, etc.: "clear"
  os.system('cls' if os.name == 'nt' else 'clear')





def OS_monitoring_summary( recTime, recProcs, cpuFaultProcs, memFaultProcs, runTooLongProcs, file ):
  """
  Print a summary of the OS monitoring results.

  Includes:
  - all monitored processes (as a table sheet)
  - all problematic processes (if any)
    - processes with excessive CPU usage (over 70 % by default)
    - processes with excessive memory usage (over 500 MB by default)
    - processes running too long (over an hour by default)
    - suggestions to resolve the problems
  """
  if len(recProcs) == 0:
    PrintAndLog( f"No processes found monitored", file=file )
    return
  PrintAndLog( f"Monitored processes recorded\n{ recTime }\ncan be seen in the following table.\n", file=file )
  LogProcessTable( recProcs, file=file )

  # Display all the problems among the filtered, monitored processes
  if len(cpuFaultProcs) > 0 or len(memFaultProcs) > 0 or len(runTooLongProcs) > 0:
    PrintAndLog( "\nBeware: ", file=file )
    if cpuFaultProcs:
      PrintAndLog( f"{ len(cpuFaultProcs) } { "PROCESS" if len(cpuFaultProcs) == 1 else "PROCESSES" }", end="", file=file )
      PrintAndLog( f"WITH HIGH CPU USAGE (OVER {THRESHOLD_CPU} %) DETECTED:", file=file )
      LogProcessTable(cpuFaultProcs, file=file)
      PrintAndLog("Suggestion:", file=file)
      PrintAndLog("1. Restart your computer/laptop to clear all running processes", file=file)
      PrintAndLog("2. End/restart processes that consume too much CPU", file=file)
      PrintAndLog("3. Update drivers to enhance CPU efficiency", file=file)
      PrintAndLog("4. Scan for malwares or other harmful softwares\n", file=file)
    if memFaultProcs:
      PrintAndLog( f"{ len(memFaultProcs) } { "PROCESS" if len(memFaultProcs) == 1 else "PROCESSES" } ", end="", file=file )
      PrintAndLog( f"WITH HIGH MEMORY USAGE (OVER {THRESHOLD_MEM} MB) DETECTED:", file=file )
      LogProcessTable(memFaultProcs, file=file)
      PrintAndLog("Suggestion:", file=file)
      PrintAndLog("Turn off the processes that occupies too much memory\n", file=file)
    if runTooLongProcs:
      PrintAndLog( f"{ len(runTooLongProcs) } { "PROCESS" if len(runTooLongProcs) == 1 else "PROCESSES" } ", end="", file=file )
      PrintAndLog( f"WITH RUNTIME OVER {format_duration(THRESHOLD_RUNTIME).upper()} DETECTED:", file=file )
      LogProcessTable(runTooLongProcs, file=file)
      PrintAndLog("Suggestion:\nTurn off unused processes to prevent them from", end=" ", file=file)
      PrintAndLog("occupying CPU and memory", file=file)
      PrintAndLog("NOTE: Only close them if necessary.", end=" ", file=file)
      PrintAndLog("Turning off necessary programs may result in system failure.\n", file=file)
  else:
    PrintAndLog( f"\nNo problematic processes found {recTime}", file=file )





def monitor(procList):
  """
  Monitors operating system usages such as CPU, memory, etc. for long-running processes
  """

  LOG_FILE_NAME = datetime.datetime.now().strftime( "system_monitoring-%Y-%m-%d-%H_%M_%S.txt" )

  while True:
    clearScreen()

    curTime = datetime.datetime.now()
    now = curTime.timestamp()

    print( f"Attempting to record operating system processes at", end=" ")
    print( f"{ curTime.strftime( "%H:%M:%S on %Y-%m-%d" ) }\n" )
    print( "Monitoring system processes...." )

    procs = [] # List of processes to monitor
 
    # Lists of (potentially) problematic processes
    CPU_OUTAGE_PROCS = []
    MEM_OUTAGE_PROCS = []
    RUN_TOO_LONG_PROCS = []

    procs = getSnapshot( now, procList )

    for p in procs:
      if p["cpu_usage"] > 70.0:
        CPU_OUTAGE_PROCS.append(p)
      elif p["memory_usage"] > 500.0:
        MEM_OUTAGE_PROCS.append(p)
      elif p["runtime"] > 3600.0:
        RUN_TOO_LONG_PROCS.append(p)

    clearScreen()

    if len(procs) > 0:
      print( "Done!", end=" " )

    # Display all the problems among the filtered, monitored processes
    OS_monitoring_summary(
      curTime.strftime( "at %H:%M:%S on %Y-%m-%d" ),
      procs, CPU_OUTAGE_PROCS, MEM_OUTAGE_PROCS, RUN_TOO_LONG_PROCS, LOG_FILE_NAME
    )

    # Clear all process list before the next monitoring
    CPU_OUTAGE_PROCS.clear()
    MEM_OUTAGE_PROCS.clear()
    RUN_TOO_LONG_PROCS.clear()
    procs.clear()

    time.sleep(INTERVAL)

    PrintAndLog( "-" * 120, end="\n\n", file=LOG_FILE_NAME )





### Entry point of this program. Similar to C++'s int main()
if __name__ == "__main__":
  try:
    print( "Welcome to the system-monitoring application." )
    print( f"While monitoring, it records the result to a log file about every ", end="" )
    print( f"{round(INTERVAL)} {"second" if INTERVAL == 1 else "seconds"}.\n" )
    print( "Press Ctrl+C to close this application\n" )

    enterInput = input("For now, press Enter to activate the monitoring process.")

    # Processes to monitor with specific names.
    # Only will the following processes be monitored.
    # When the following list is empty, though,
    # every process available will be monitored all together. 

    # This process list is adjustable
    # and will monitor the processes you assigned.
    procList = [
      # "MicrosoftSecurityApp.exe",   # Microsoft security
      "OneDrive.exe",               # OneDrive cloud
      "SafeConnect.Entry.exe",      # McAfee Safe Connect
      "dwm.exe",                    # Desktop window manager
    ]

    monitor(procList)
  except KeyboardInterrupt:
    clearScreen()
    print( "Now shutting this application down...." )
    clearScreen()