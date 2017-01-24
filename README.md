# Compile Workload

**Python script to create a compiler workload and evaluate external performance.**

This script is intended to be used with [MemFS](https://github.com/bbengfort/memfs) to create a workload for evaluating system performance. The primary workload script does the following activities in the specified directory:

1. Clone a repository
2. Make/build in the repository
3. Stat every file
4. Report time and stats

Because compilation of a project is different on every system, project-specific steps are embedded in the workload file. The following projects are supported:

1. [Redis](https://github.com/antirez/redis) (76MB, 591 files, 137,475 LOC)
2. [Postgres](https://github.com/postgres/postgres) (422MB, 4,807 files, 910,948 LOC)
3. [Nginx](https://github.com/nginx/nginx) (62MB, 440 files, 155,056 LOC)
4. [Apache Web Server](https://github.com/apache/httpd) (362MB, 4,059 files, 503,006 LOC)
5. [Ruby](https://github.com/ruby/ruby) (197MB, 3,281 files, 918,052 LOC)
6. [Python 3](https://github.com/python/cpython) (382MB, 3,570 files, 931,814 LOC)

Running a workload is as follows:

```
$ python3 workload.py -o results.csv -p nginx /tmp/testdir
```

This will run the workload on the Nginx repository, building in `/tmp/testdir` and appending the results to `results.csv`. Various options and defaults are provided and can be further inspected with:

```
$ python3 workload.py --help
```

Note that this script depends on many system and compiling dependencies to be available. Because they were already available on my system, I don't necessarily have a list of that I can expose through a requirements file. However, at a minimum, Git is required as are Xcode developer tools on a Macbook Pro.

For testing MemFS, I've created a simple script that runs through a single instance of the testing protocol. This should be used with care, however, as it is built for a specific system. 
