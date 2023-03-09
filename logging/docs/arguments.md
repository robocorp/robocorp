# Listener Arguments

  `--dir`
  
    Points to a directory where the output files should be written.
    (default: '.' -- i.e.: working dir).
    
    Example:
    
      --dir=./output
      --dir=c<COLON>/temp/output

  `--max-file-size`
  
    Specifies the maximum file size before a rotation for the output file occurs.
    
    The size can be specified with its unit.
    The following units are supported: `gb, g, mb, m, kb, k, b`
    (to support gigabytes=gb or g, megabytes=mb or m, kilobytes=kb or k, bytes=b).
    
    Note: if no unit is specified, it's considered as bytes.
    
    Example:
    
      --max-file-size=200kb
      --max-file-size=2mb
      --max-file-size=1gb
      --max-file-size=10000b

  `--max-files`
  
    Specifies the maximum number of files to be generated in the logging before
    starting to prune old files.
    
    i.e.: If `--max-files=2`, it will generate `output.rfstream`, `output_2.rfstream`
    and when `output_3.rfstream` is about to be generated, it'll erase `output.rfstream`.
    
    Example:
    
      --max-files=3

  `--log`
  
    If specified, writes HTML contents that enable the log contents to be
    viewed embedded in an HTML file.
    It should point to a path in the filesystem.
    
    Note: if a ':' is used, it should be changed to <COLON> (because a ':'
    char is used as the separator by Robot Framework).
    So, something as `c:/temp/log.html` should be written as `c<COLON>/temp/log.html`.
    
    Note: The contents embedded in the file will contain the files written on the disk
    but embedded as compressed information (so its size should be less than
    the size of the contents on disk), note that contents pruned from the log
    (due to the --max-files setting) will NOT appear in the log.html.
    
    Example:
    
      --log=./logs/log.html
      --log=c<COLON>/temp/log.html