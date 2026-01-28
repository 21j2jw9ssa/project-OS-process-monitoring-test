def evaluate(snapshot, cpu_threshold: int|float, mem_threshold: int|float, runtime_threshold: int|float ):
  """
  :type snapshot: tuple
  :param snapshot: identifying number of this process

  :type cpu_threshold: int | float
  :param cpu_threshold: how much CPU has been consumed by this process, in percent (%)

  :type mem_threshold: int | float
  :param mem_threshold: how much memory has been occupied by this process, in MB

  :type runtime_threshold: int | float
  :param runtime_threshold: how long has this process run since starting up

  Evaluate a monitoring snapshot on an operating system's resources.
  Must detect three kinds of violations:
  - excessive CPU usage
  - excessive memory usage
  - runtime way too long (typcially over an hour)
  """
  results = {
    "cpu_violations": [],
    "mem_violations": [],
    "runtime_violations": []
  }

  # Detect any processes that either:
  # - consumes too much CPU (over 70 %)
  # - occupies too much memory (over 500 MB)
  # - has been running for at least an hour
  for proc in snapshot:
    if proc["cpu_usage"] is not None and proc["cpu_usage"] > cpu_threshold:
      results["cpu_violations"].append(proc)
    if proc["memory_usage"] is not None and proc["memory_usage"] > mem_threshold:
      results["mem_violations"].append(proc)
    if proc["runtime"] > runtime_threshold:
      results["runtime_violations"].append(proc)

  return results
