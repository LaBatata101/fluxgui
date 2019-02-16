from fluxgui import xfluxcontroller, redshiftcontroller

class FluxController(xfluxcontroller.XfluxController):
    """
    FluxController is the same as XfluxController except that it
    requires a Settings instance and updates that instance when
    relevant controller calls are made.
    """
    def __init__(self, settings):
        self.settings = settings
        super().__init__(
                **self.settings.xflux_settings_dict())

    def start(self):
        if self.settings.zipcode == "" and self.settings.latitude == "":
            raise ValueError("Cannot start xflux, missing zipcode and latitude")
        super().start()

    # Controller methods that don't touch xflux
    def set_autostart(self, autos):
        self.settings.autostart = autos

    # xflux methods that should also update settings
    def set_xflux_latitude(self, lat):
        self.settings.latitude = lat
        super().set_xflux_latitude(lat)

    def set_xflux_longitude(self, longit):
        self.settings.longitude = longit
        super().set_xflux_longitude(longit)

    def set_xflux_zipcode(self, zipc):
        self.settings.zipcode = zipc
        super().set_xflux_zipcode(zipc)

    def _set_xflux_color(self, col):
        self.settings.color = col
        super()._set_xflux_color(col)

    def _get_xflux_color(self):
        return super()._get_xflux_color()

    color=property(_get_xflux_color, _set_xflux_color)

class RedShiftController(redshiftcontroller.RedshiftController):

    def __init__(self, settings):
        self.settings = settings
        super().__init__(**self.settings.redshift_settings.dict())

    def start(self):
        if self.settings.latitude == "" or self.settings.longitde == "":
            raise ValueError("Cannot start redshift, missing latitude or longitude")
        super().start()

    def set_autostart(self, autos):
        self.settings.autostart = autos

    def set_redshift_latitude(self, lat):
        self.settings.latitude = lat
        super().set_redshift_latitude(lat)

    def set_redshift_longitude(self, longit):
        self.settings.latitude = longit
        super().set_redshift_longitude(longit)

    def _set_redshift_color(self, col):
        self.settings.color = col
        super()._set_redshift_color(col)

    def _get_redshift_color(self):
        return super()._get_redshift_color()

    color = property(_get_redshift_color, _set_redshift_color)
