class Channel:
    """
    Channel:
    scheme <> auth <> location <> token <> channel <> subchannel <> platform <> package_filename

    Package Spec:
    channel <> subchannel <> namespace <> package_name

    """

    def __init__(
        self,
        scheme=None,
        auth=None,
        location=None,
        token=None,
        name=None,
        platform=None,
        package_filename=None,
    ):
        self.scheme = scheme
        self.auth = auth
        self.location = location
        self.token = token
        self.name = name or ""
        self.platform = platform
        self.package_filename = package_filename

    @property
    def channel_location(self):
        return self.location

    @property
    def channel_name(self):
        return self.name

    @property
    def subdir(self):
        return self.platform
