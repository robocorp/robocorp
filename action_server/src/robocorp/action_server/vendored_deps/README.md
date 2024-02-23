These deps are installed directly from the github repository where they're hosted.

To update, erase the files in this directory (except the `__init__.py` in the root),
go into this directory and run:

pip install https://github.com/robocorp/vendored_deps/archive/master.zip --target .

Then, remove the `*.dist-info` folder and commit the results. 