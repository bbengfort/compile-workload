#!/bin/bash
# Executes the test protocol for MemFS

# Create the results file
DATE=$(date +%Y%m%d%H%M)
MEMFSLOG="memfs-$DATE.log"
RESULTS="results-$DATE.csv"

# Test Paths
TESTDIR="disk"
MEMFSDIR="memfs"

# Executables
WORKLOAD="./workload.py"

# Run the standard file system tests
mkdir $TESTDIR
# $WORKLOAD -p redis -H -o $RESULTS $TESTDIR
# $WORKLOAD -p postgres -o $RESULTS $TESTDIR
# $WORKLOAD -p nginx -o $RESULTS $TESTDIR
# $WORKLOAD -p apache -o $RESULTS $TESTDIR
# $WORKLOAD -p ruby -o $RESULTS $TESTDIR
# $WORKLOAD -p python -o $RESULTS $TESTDIR
rmdir $TESTDIR

# Run the MemFS tests
mkdir $MEMFSDIR

run_memfs_workload() {
    memfs -c memfs.json memfs/ > $MEMFSLOG 2>&1 &
    PID=$!
    $WORKLOAD -p $1 -o $RESULTS $MEMFSDIR
    kill -INT $PID
    sleep 10
}

run_memfs_workload redis
# run_memfs_workload postgres
# run_memfs_workload nginx
# run_memfs_workload apache
# run_memfs_workload ruby
# run_memfs_workload python

rmdir $MEMFSDIR
