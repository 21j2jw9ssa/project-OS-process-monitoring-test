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
import math
from pathlib import Path

# Base directory to save a log file
BASE_DIR = Path(__file__).parent.resolve().parent
DATA_DIR = BASE_DIR / "logs"

# Create a directory similar to "./../logs" if not exist
DATA_DIR.mkdir(exist_ok=True)

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

  :type memory_usage: float
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





def dataFormat(value, template):
  """
  use for formatting values in strings
  
  :param value: string to substitute into the template
  :param template: string template where value can be substituted
  """
  return template.format(x=value)





def drawSeparationLine(fields):
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
  line += "+\n"
  return line





def logHeader(fields):
  """
  Print fields and their names in a table sheet
  
  :param fields: a field tuple
  :param file: file to write headers to
  """
  fieldCtnt = ""
  for field in fields:
    fieldCtnt += f"| { field['name']:<{ field['column_width'] }} "
  fieldCtnt += "|\n"
  return fieldCtnt





def logRowInfo(fields, row):
  """
  Docstring for logRowInfo
  
  :param fields: a field tuple
  :param row: a row of data
  :param file: file to write the row info to
  """
  rowCtnt = ""

  # print the record in different field values
  for i in range( len(FIELDS) ):
    curCol = FIELDS[i]
    attrData = fields[i]
    if curCol["align"] == "right":
      rowCtnt += f"| {dataFormat( row[ curCol["name"] ], attrData['format'] ):>{attrData['column_width']}} "
    else:
      rowCtnt += f"| {dataFormat( row[ curCol["name"] ], attrData['format'] ):<{attrData['column_width']}} "
  rowCtnt += "|\n"
  return rowCtnt





def LogProcessTable(rows):
  """
  Print a table of processes
  """
  if len(rows) == 0:
    return ""

  for f in FIELDS:
    # how many spaces the unit occupies in the table. Set to zero by default unless specified
    unitOccupySpaces = 0
    fieldName = f["name"]
    if fieldName == "cpu_usage":      # uses percent (%), occupies 2 spaces
      unitOccupySpaces = 2
    elif fieldName == "memory_usage": # uses megabytes (Windows' MB), occupies 3 spaces
      unitOccupySpaces = 3
    elif fieldName == "runtime":      # uses seconds (sec.), occupies 5 spaces
      unitOccupySpaces = 5

    # Find the value of a specific field that occupies the most spaces...
    maxValueLength = max( [ len( str( r[ fieldName ] ) ) + unitOccupySpaces for r in rows ] )

    # ...then find the value of the header that occupies the most spaces.
    headerValueLength = len( fieldName )

    # Finally, set the more spacious one as the column width of the current field
    f["column_width"] = max( maxValueLength, headerValueLength )

  tableCtnt = ""

  # Draw headers of the sheet
  tableCtnt += drawSeparationLine(FIELDS) + logHeader(FIELDS) + drawSeparationLine(FIELDS)

  # Draw all rows of the sheet
  for i in range( len(rows) ):
    tableCtnt += logRowInfo( FIELDS, rows[i] )

  tableCtnt += drawSeparationLine( FIELDS )
  return tableCtnt





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





def duration_readable_format(secs: int):
  """
  Converts a number of seconds into a readable string in a human-readable format,
  such as "10 hours, 20 minutes and 30 seconds".
  """
  if ( not isinstance(secs, int) ) or secs < 0:
    raise Exception( f"Number of seconds must be a natural number, but received {secs}" )
  finTimeInfo :str = ""

  ( nMins, nSecs )  = divmod(secs, 60)
  ( nHrs, nMins )   = divmod(nMins, 60)
  ( nDays, nHrs )   = divmod(nHrs, 24)
  ( nWeeks, nDays ) = divmod(nDays, 7)

  weekInfo = f"{ "1 week" if nWeeks == 1 else ( "" if nWeeks == 0 else f"{nWeeks} weeks" ) }"
  dayInfo = f"{ "1 day" if nDays == 1 else ( "" if nDays == 0 else f"{nDays} days" ) }"
  hrInfo = f"{ "1 hour" if nHrs == 1 else ( "" if nHrs == 0 else f"{nHrs} hours" ) }"
  minInfo =  f"{ "1 minute" if nMins == 1 else ( "" if nMins == 0 else f"{nMins} minutes" ) }"
  secInfo = f"{ "1 second" if nSecs == 1 else ( "" if ( nSecs == 0 and ( nWeeks > 0 or nDays > 0 or nHrs > 0 or nMins > 0 ) ) else f"{nSecs} seconds" ) }"

  validTimeInfo = [ t for t in [ weekInfo, dayInfo, hrInfo, minInfo, secInfo ] if t != "" ]

  for i in range( len(validTimeInfo) ):
    finTimeInfo +=validTimeInfo[i]
    if i + 2 < len(validTimeInfo):
      finTimeInfo += ", "
    elif i + 2 == len(validTimeInfo):
      finTimeInfo += " and "

  return finTimeInfo





def clearScreen():
  """
  Clear terminal screen.
  Does not affect log file-writing.
  """
  # clears the terminal
  # For Windows: "cls"
  # For MacOS, Linux, etc.: "clear"
  os.system('cls' if os.name == 'nt' else 'clear')





def OS_monitoring_summary( recTime,
                           recProcs: int | float,
                           cpuFaultProcs,
                           memFaultProcs,
                           runTooLongProcs ):
  """
  Print a summary of the OS monitoring results.

  Includes:
  - all monitored processes (as a table sheet)
  - all problematic processes (if any)
    - processes with excessive CPU usage (over 70% by default)
    - processes with excessive memory usage (over 500 MB by default)
    - processes running too long (over an hour by default)
    - suggestions to resolve the problems
  """

  # Threshold values to show system warnings if passed
  THRESHOLD_CPU = 70.0        # as percent (%)
  THRESHOLD_MEM = 500.0       # as MB
  THRESHOLD_RUNTIME = 3600    # seconds

  resultCtnt = ""

  if len(recProcs) == 0:
    return f"No filtered processes detected { recTime }\n"

  resultCtnt += f"Monitored processes recorded { recTime }\ncan be seen in the following table.\n\n"
  resultCtnt += LogProcessTable(recProcs)

  # Display all the problems among the filtered, monitored processes
  if len(cpuFaultProcs) > 0 or len(memFaultProcs) > 0 or len(runTooLongProcs) > 0:
    resultCtnt += "\nBeware: "
    if cpuFaultProcs:
      resultCtnt += f"{ len(cpuFaultProcs) } { "PROCESS" if len(cpuFaultProcs) == 1 else "PROCESSES" }\n"
      resultCtnt += f"WITH HIGH CPU USAGE (OVER {THRESHOLD_CPU} %) DETECTED:\n"
      resultCtnt += LogProcessTable(cpuFaultProcs)
      resultCtnt += "Suggestion:\n"
      resultCtnt += "1. Restart your computer/laptop to clear all running processes\n"
      resultCtnt += "2. End/restart processes that consume too much CPU\n"
      resultCtnt += "3. Update drivers to enhance CPU efficiency\n"
      resultCtnt += "4. Scan for malwares or other harmful softwares\n"
    if memFaultProcs:
      resultCtnt += f"{ len(memFaultProcs) } { "PROCESS" if len(memFaultProcs) == 1 else "PROCESSES" }\n"
      resultCtnt += f"WITH HIGH MEMORY USAGE (OVER {THRESHOLD_MEM} MB) DETECTED:\n"
      resultCtnt += LogProcessTable(memFaultProcs)
      resultCtnt += "Suggestion:\n"
      resultCtnt += "Turn off the processes that occupies too much memory\n"
      resultCtnt += "and release it to the other needed processes.\n"
    if runTooLongProcs:
      resultCtnt += f"{ len(runTooLongProcs) } { "PROCESS" if len(runTooLongProcs) == 1 else "PROCESSES" } "
      resultCtnt += f"WITH RUNTIME OVER {duration_readable_format(THRESHOLD_RUNTIME).upper()} DETECTED:\n"
      resultCtnt += LogProcessTable(runTooLongProcs)
      resultCtnt += "Suggestion:\nTurn off these unused processes to release CPU and memory\n"
      resultCtnt += "resources to the other needed processes.\n"
      resultCtnt += "NOTE: Only close them if necessary.\n"
      resultCtnt += "Turning off indispensable programs may result in system failure.\n"
  else:
    resultCtnt += f"\nNo problematic processes found {recTime}\n"

  return resultCtnt





def monitor(procList, nSecs):
  """
  Monitors operating system usages such as CPU, memory, etc. for long-running processes
  """

  LOG_FILE_NAME = datetime.datetime.now().strftime( "system_monitoring-%Y-%m-%d-%H_%M_%S.txt" )

  while True:
    clearScreen()

    curTime = datetime.datetime.now()
    now = curTime.timestamp()

    print( f"Attempting to record operating system processes at", end=" ")
    print( f"{ curTime.strftime( "%H:%M:%S on %Y-%m-%d" ) }\n\nMonitoring system processes...." )

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
    result = OS_monitoring_summary(
      curTime.strftime( "at %H:%M:%S on %Y-%m-%d" ),
      procs, CPU_OUTAGE_PROCS, MEM_OUTAGE_PROCS, RUN_TOO_LONG_PROCS
    )

    # Clear all process list before the next monitoring
    CPU_OUTAGE_PROCS.clear()
    MEM_OUTAGE_PROCS.clear()
    RUN_TOO_LONG_PROCS.clear()
    procs.clear()

    PrintAndLog( result, file=LOG_FILE_NAME )

    time.sleep(nSecs)

    PrintAndLog( "-" * 120, end="\n\n", file=LOG_FILE_NAME )





### Entry point of this program. Similar to C++'s int main()
if __name__ == "__main__":
  try:
    clearScreen()
    # Warning: setting it too low may result in more data written to a log file
    #          and can consume too much storage space unnecessarily quickly.
    INTERVAL = 59.4    # time gap between each monitoring, in seconds

    print( "Welcome to the system-monitoring application." )
    print( f"While monitoring, it records the result to a log file about every ", end="" )
    print( f"{math.ceil(INTERVAL)} {"second" if math.ceil(INTERVAL) == 1 else "seconds"}.\n" )
    print( "Press Ctrl+C to close this application.\n" )

    enterInput = input("For now, press Enter to activate the monitoring process.")

    # Processes to monitor with specific names.
    # Only will the following processes be monitored.
    # When the following list is empty, though,
    # every process available will be monitored all together. 

    # This process list is adjustable
    # and will monitor the processes you assigned.
    # You can adjust what you wish to monitor
    # by changing the process names below, though.
    procList = [
      "MicrosoftSecurityApp.exe",   # Microsoft security
      "OneDrive.exe",               # OneDrive cloud
      "SafeConnect.Entry.exe",      # McAfee Safe Connect
      "dwm.exe",                    # Desktop window manager
    ]

    monitor(procList, INTERVAL)
  except KeyboardInterrupt:
    clearScreen()
    print( "Now shutting this application down...." )
    clearScreen()
