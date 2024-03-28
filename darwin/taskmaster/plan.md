# Task Master Plan

## System
- Main process
  - Holds **task queue**
    - Process task synchronously, but task execution is done in parallel
    - When an unprocessed task is visited, put it in a processing list
    - Darwin will check all the currently processing tasks if any of them have completed to generate the next task
  - Instantiates **bridge** between each process and main process
    - Need to get multiple values from child process return output of task
      - Will be a dictionary of keys + values
  - 


