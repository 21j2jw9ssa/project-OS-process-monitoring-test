import time

def cpu_load( target_cpu_percent_work=40, duration=60 ):
  """
  Controlled CPU workload with duration
  """

  # Short intervals can make this program smoother and more stable
  interval = 0.1 # in seconds

  # Work time can be determined by the total interval time
  # and how much portion of it should be spent on working
  workTime = interval * ( target_cpu_percent_work / 100 )

  # To ensure the total cycle duration is stable,
  # the time when this process is not working
  # will be used to take a rest
  idleTime = interval - workTime

  # To maintain time-bound stress and
  # to avoid infinite loop fiasco
  end = time.time() + duration

  # Repeats the control cycles until time is up
  while time.time() < end:

    # Now the process begins to work
    start = time.time()
    while time.time() - start < workTime:
      pass

    # As this process rests,
    # CPU scheduler can run other processes.
    # This keeps the load staying close to a constant
    # instead of increasing the load.
    time.sleep( max(0, idleTime) )