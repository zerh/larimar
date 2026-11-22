# Plan 1.13: the standard library

## Done

- **A task talks through a `Channel`**: `run(channel: Channel): void throws ProcessError`; tasks have
  their own messages over shared memory, not `std.os.rpc`.

## To do

### C only in processes apart: `UnsafeTask`

The C of a library is used only from a task, in a copy of the program: when it fails, the task fails,
not the program. The process is the region of that C: what it took and did not free goes when it ends.

- `interface UnsafeTask extends Task` with one more method, `setup(loader: LibraryLoader): void throws
  LoadError`, called once in each process (a ProcessPool keeps the library for the next tasks).
- `LibraryLoader`: `bind(Interface, "path of the library")` looks up each function of a native
  interface declared in the task's class (`dlsym`, `GetProcAddress`), with a typed pointer for each: no
  libffi. A missing library or function is a `LoadError` that names it, before `run()`.
- **Callbacks**: a lambda the library keeps is given to the loader (`keep`), which holds it as long as
  the process. A callback without a `void* userdata` needs a C function of its own for each lambda (a
  fixed number for each signature). A callback from a thread of the library is a panic: the task fails.
  What a callback has to tell the program goes through the channel.
- **The rule** (`rules.lar`): a `native interface` outside std is declared only in a class that
  implements `UnsafeTask`.
- C pointers do not leave the process: what crosses is what crosses through a channel.
