def add_data_args(parser, defaults):
    parser.add_argument(
        "-d",
        "--datadir",
        metavar="PATH",
        default="",
        help=(
            "Directory to store the data for operating the actions server "
            "(by default a datadir will be generated based on the current directory)."
        ),
    )
    parser.add_argument(
        "--db-file",
        help=(
            "The name of the database file, relative to the datadir "
            "(default: %(default)s)"
        ),
        default=defaults["db_file"],
    )


def add_verbose_args(parser, defaults):
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Be more talkative (default: %(default)s)",
    )
