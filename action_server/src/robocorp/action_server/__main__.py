if __name__ == "__main__":
    from robocorp.action_server.cli import main

    args = None
    # args = "start -v -p 8090".split()
    import os

    os.chdir(r"X:\temp\check-action-server\action_package")
    args = ["start", "--reuse-process"]
    # args = ["start", "--expose"]

    main(args)
