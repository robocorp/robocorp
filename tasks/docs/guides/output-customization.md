# Log output customization

By default, the log output will be saved to an `output` directory, where each file 
can be up to `1MB` and up to `5` files are kept before old ones are deleted. 
When the run finishes, a `log.html` file will be created in the output directory 
containing the log viewer with the log contents embedded.

However, you can customize the log output by changing the output directory, 
maximum number of log files to keep, and maximum size of each output file. 
You can do this through the command line by passing the appropriate arguments 
when running `python -m robocorp.tasks run`.

For example, to change the output directory to `my_output`, run:

```
python -m robocorp.tasks run path/to/tasks.py -o my_output
```

You can also set the maximum number of output files to keep by passing 
`--max-log-files` followed by a number. For example, to keep up to `10` log files, run:

```
python -m robocorp.tasks run path/to/tasks.py --max-log-files 10
```

Finally, you can set the maximum size of each output file by passing 
`--max-log-file-size` followed by a size in megabytes (e.g.: `2MB` or `1000kb`).

For example, to set the maximum size of each output file to `500kb`, run:

```
python -m robocorp.tasks run path/to/tasks.py --max-log-file-size 500kb
```
