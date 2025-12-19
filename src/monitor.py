"""
Operating system resource monitor

What this script does:
- show specified processes
- indicate problematic processes
- gives users suggestions to resolve problematic processes
"""

import os ;        # To detect system resources
import psutil ;    # necessary for system monitoring, particularly for industrial purposes
import time ;      # for monitoring for a fixed period
import datetime ;
from pathlib import Path ;

BASE_DIR = Path(__file__).parent.resolve().parent
DATA_DIR = BASE_DIR / "logs"
DATA_DIR.mkdir(exist_ok=True) 

RECORD_TIME = datetime.datetime.now() ;

# Log file name is based on the moment this program
# starts the first monitoring on OS resources
LOG_FILE_NAME = RECORD_TIME.strftime( "system_monitoring-%Y-%m-%d-%H_%M_%S.txt" )

path = DATA_DIR / LOG_FILE_NAME

INTERVAL = 59.7    # time gap between each monitoring, in seconds

# THRESHOLD VALUES TO DEMONSTRATE SYSTEM WARNINGS IF PASSED
THRESHOLD_CPU = 70.0        # as percent (%)
THRESHOLD_MEM = 500.0       # as MB
THRESHOLD_RUNTIME = 3600    # seconds

HEADERS = ["pid", "name", "cpu_usage_percent", "memory_usage_MB", "runtime_since_started_sec"]
ROWS_TO_COLLECT = [] ;

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





# Print a line of text on terminal screen and a file 
def PrintAndLog(str :str="", end :str="\n", file :str=f"{LOG_FILE_NAME}"):
  """
  Write a line of text to a new file.

  Then print a line of text in the terminal.
  
  :type str: str
  :param str: a line of string

  :type end: str
  :param end: string to be appended as the last value

  :type file: str
  :param file: a text file's name
  """
  path = DATA_DIR / file

  with path.open("a", encoding="utf-8") as f:
    f.write(str)
    f.write(end)
    print( str, end=end )











# format string
def apply_format(value, template):
  return template.format(x=value)





def drawSeparationLine(fields, file):
  """
    How length of a horizontal border in sheets is calculated:
    - Calculate how many spaces all headers' names uses.
    - Count gaps for each header: 1 space on both the left side and the right side
    - Count straight lines that separate headers from each other

      number of headers + 1
    
    For exmaple:
    ```
    ---------------------------
    | SAMPLE | DEMO | EXAMPLE |
    ---------------------------
    ```

    Length of the `SAMPLE` header:  6 chars + 1 left gap + 1 right gap = 8 spaces

    Length of the `DEMO` header:    4 chars + 1 left gap + 1 right gap = 6 spaces
    
    Length of the `EXAMPLE` header: 7 chars + 1 left gap + 1 right gap = 9 spaces

    Length needed for all headers: 3 headers + 1 straight line header separator = 4 spaces

    Length of a separation line needed: 8 + 6 + 9 + 4 = 27
  """
  line = ""
  for field in fields:
    line += f"{ "-" * ( 1 + field['column_width'] + 1 ) }" ;
  line += f"{ "-" * ( len(fields) + 1 ) }"
  PrintAndLog( line, file=file )





# PRINT FIELDS OF HEADERS
def logHeader(fields, file):
  PrintAndLog( "|", end=" ", file=file )
  for field in fields:
    PrintAndLog( f"{ field['name']:<{ field['column_width'] }}", end=" | ", file=file ) ;
  PrintAndLog( file=file ) ;





# Print process info
def logRowInfo(fields, row, file):  
  PrintAndLog("| ", end="", file=file)

  # print the record in different field values
  for i in range( len(FIELDS) ):
    if FIELDS[i]["align"] == "right":
      PrintAndLog( f"{apply_format( row[ FIELDS[i]["name"] ], fields[i]['format'] ):>{fields[i]['column_width']}}", end=" | ",  file=file )
    else:
      PrintAndLog( f"{apply_format( row[ FIELDS[i]["name"] ], fields[i]['format'] ):<{fields[i]['column_width']}}", end=" | ",  file=file )
  PrintAndLog("", file=file)

def LogProcessTable(rows, file=f"{LOG_FILE_NAME}"):
  if len(rows) == 0:
    return ;
  for f in FIELDS:
    unitOccupySpaces = 0 
    if f["name"] == "cpu_usage":
      unitOccupySpaces = 2
    elif f["name"] == "memory_usage":
      unitOccupySpaces = 3
    elif f["name"] == "runtime":
      unitOccupySpaces = 5

    maxValueLength = max( [ len( str( r[ f["name"] ] ) ) + unitOccupySpaces for r in rows ] )
    headerValueLength = len( f["name"] )

    f["column_width"] = max( maxValueLength, headerValueLength )

  drawSeparationLine( FIELDS, file )
  logHeader( FIELDS, file )
  drawSeparationLine( FIELDS, file )
  
  for i in range( len(rows) ):
    logRowInfo( FIELDS, rows[i], file )
  drawSeparationLine( FIELDS, file )





def getSnapshot( curTimeInSec: float, procList ):
  """
  Get a snapshot to test OS monitoring system
  """
  snapshots = []

  for proc in psutil.process_iter(
    attrs=["pid", "name", "cpu_percent", "memory_info", "create_time"]
  ):
    try:
      if procList != [] and proc.info["name"] not in procList:
        continue

      procId = int( proc.info["pid"] )                        # process id
      procName = proc.info["name"]                            # process name (may not be unique)
      procCPU = round( float( proc.info['cpu_percent'] ), 1 ) # CPU usage in percentage

      # Memory usage in megabytes.
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





def SecsToMinsOrHrs(secs):
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





### Clear the terminal screen if needed
def clearScreen():
  # clears the terminal
  # For Windows: "cls"
  # For MacOS, Linux, etc.: "clear"
  os.system('cls' if os.name == 'nt' else 'clear')





def OS_monitoring_summary( recTime, recProcs, cpuFaultProcs, memFaultProcs, runTooLongProcs, file=LOG_FILE_NAME ):
  if len(recProcs) > 0:
    PrintAndLog( f"Monitored processes recorded\n{ recTime }\ncan be seen in the following table.\n", file=file )
    LogProcessTable( recProcs, file=file )

    # Display all the problems among the filtered, monitored processes
    if len(cpuFaultProcs) > 0 or len(memFaultProcs) > 0 or len(runTooLongProcs) > 0:
      PrintAndLog( "\nBeware: ", file=file ) ;
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
        PrintAndLog( f"WITH RUNTIME OVER {SecsToMinsOrHrs(THRESHOLD_RUNTIME).upper()} DETECTED:", file=file )
        LogProcessTable(runTooLongProcs, file=file)
        PrintAndLog("Suggestion:\nTurn off unused processes to prevent them from", end=" ", file=file)
        PrintAndLog("occupying CPU and memory", file=file)
        PrintAndLog("NOTE: Only close them if necessary.", end=" ", file=file)
        PrintAndLog("Turning off necessary programs may result in system failure.\n", file=file)
    else:
      PrintAndLog( "\nNo potentially problematic processes found.", file=file )
  else:
    PrintAndLog( f"No processes detected { recTime }", file=file )





### Monitors system usages such as CPU, memory, etc. for long-running processes
def monitor(procList):
  while True:
    clearScreen()

    curTime = datetime.datetime.now()
    now = curTime.timestamp() ;

    print( f"Attempting to record system usages at", end=" ")
    print( f"{ curTime.strftime( "%H:%M:%S on %Y-%m-%d" ) }\n" )
    print( "Monitoring system processes...." )

    procs = [] # List of processes to monitor
 
    # Lists of (potentially) problematic processes
    CPU_OUTAGE_PROCS = []; MEM_OUTAGE_PROCS = []; RUN_TOO_LONG_PROCS = [] ;

    for proc in psutil.process_iter(
      # Will be used to fetch process info
      attrs=["pid", "name", "cpu_percent", "memory_info", "create_time"]
    ):
      try:
        if ( len(procList) == 0 ) or ( proc.info["name"] in procList ):
          procId = int( proc.info["pid"] ) ;                        # process id
          procName = proc.info["name"] ;                            # process name (may not be unique)
          procCPU = round( float( proc.info['cpu_percent'] ), 1 ) ; # CPU usage in percentage

          # Memory usage in megabytes.
          # This parameter, i.e. proc.info['memory_info'], is originally recorded as bytes.
          #
          # Since Windows' MB is equivalent to MiB, which is equal to
          # 1024 KiB and 1024 x 1024 B,
          # this parameter is divided by 1024 twice to display the memory usage in Windows' MB.
          procMem = round( float( proc.info['memory_info'].rss / 1024 / 1024 ), 1 ) ;

          # Time running since started up, in seconds
          procRuntime = int( now - proc.info["create_time"] )

          curProc = Process( procId, procName, procCPU, procMem, procRuntime )

          ### Detect potentially problematic processes. Again, with filtered processes only
          procs.append(curProc) ;
          if ( procCPU is not None ) and procCPU > THRESHOLD_CPU:
            CPU_OUTAGE_PROCS.append(curProc) ;
          if ( procMem is not None ) and procMem > THRESHOLD_MEM:
            MEM_OUTAGE_PROCS.append(curProc) ;
          if ( procRuntime is not None ) and procRuntime > THRESHOLD_RUNTIME: # Process has run for beyond an hour since started up
            RUN_TOO_LONG_PROCS.append(curProc) ;

      except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue

    clearScreen()

    if len(procs) > 0:
      print( "Done!", end=" " )

      # Display all the problems among the filtered, monitored processes
      OS_monitoring_summary(
        curTime.strftime( "at %H:%M:%S on %Y-%m-%d" ),
        procs,
        CPU_OUTAGE_PROCS,
        MEM_OUTAGE_PROCS,
        RUN_TOO_LONG_PROCS
      )

      CPU_OUTAGE_PROCS.clear()
      MEM_OUTAGE_PROCS.clear()
      RUN_TOO_LONG_PROCS.clear()
      procs.clear()
  
    else:
      PrintAndLog( f"No processes detected { curTime.strftime( "at %H:%M:%S on %Y-%m-%d" ) }" )
    time.sleep(INTERVAL)





### Entry point of this program. Similar to C++'s int main()
if __name__ == "__main__":
  try:
    print( "Welcome to the system-monitoring application." ) ;
    print( f"While monitoring, it records the result to a log file about every ", end="" ) ;
    print( f"{round(INTERVAL)} {"second" if INTERVAL == 1 else "seconds"}.\n" ) ;
    print( "Press Ctrl+C to close this application\n" ) ;

    enterInput = input("For now, press Enter to activate the monitoring process.") ;

    # Processes to monitor with specific names.
    # Only will the following processes be monitored.
    # When the following list is empty, though,
    # every process available will be monitored all together. 
    procList = [
      # "MicrosoftSecurityApp.exe", # Microsoft security
      "chrome.exe",
      # "SafeConnect.Entry.exe"     # McAfee Safe Connect
    ] ;

    monitor(procList) ;
  except KeyboardInterrupt:
    print( "Now shutting this application down...." ) ;