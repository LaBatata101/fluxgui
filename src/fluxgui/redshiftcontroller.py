import pexpect
import time
import weakref
from fluxgui.exceptions import XfluxError, MethodUnavailableError
from fluxgui import settings


class RedshiftController(object):
    """
    A controller that starts and interacts with an xflux process.
    """

    def __init__(self, color=settings.default_termaperature,
                 pause_color=settings.off_temperature, **kwargs):
        if 'longitude' not in kwargs and 'latitude' not in kwargs:
            raise XfluxError("Required key not found (either longitude and latitude)")

        self.init_kwargs = kwargs
        self._current_color = color
        self._pause_color = pause_color

        self.states = {
            "INIT": _InitState(self),
            "RUNNING": _RunningState(self),
            "PAUSED": _PauseState(self),
            "TERMINATED": _TerminatedState(self),
        }
        self.state = self.states["INIT"]

    def start(self, startup_args=None):
        self.state.start(startup_args)

    def stop(self):
        self.state.stop()

    def preview_color(self, preview_color):
        self.state.preview(preview_color)

    def toggle_pause(self):
        self.state.toggle_pause()

    def set_redshift_latitude(self, lat):
        self.state.set_setting(latitude=lat)

    def set_redshift_longitude(self, longit):
        self.state.set_setting(longitude=longit)

    def _set_redshift_color(self, col):
        self.state.set_setting(color=col)

    def _get_redshit_color(self):
        return self._current_color

    color = property(_get_redshit_color, _set_redshift_color)

    def _start(self, startup_args=None):
        if not startup_args:
            startup_args = self._create_startup_arg_list(self._current_color, **self.init_kwargs)
        try:
            user_name = pexpect.run('whoami').decode('utf-8').strip()
            command = 'pgrep -d, -u {} redshift'.format(user_name)
            previous_instances = pexpect.run(command).strip().decode('utf-8')
            if previous_instances != "":
                for process in previous_instances.split(","):
                    pexpect.run('kill -9 {}'.format(process))

            self._redshift = pexpect.spawn("redshift", startup_args)

        except pexpect.ExceptionPexpect:
            raise FileNotFoundError("\nError: Please install redshift in the PATH \n")

    def _stop(self):
        try:
            self._change_color_immediately(settings.off_temperature)
            # If we terminate xflux below too soon then the color
            # change doesn't take effect. Perhaps there's a more
            # gentle way to terminate xflux below -- the 'force=True'
            # means 'kill -9' ...
            time.sleep(1)
        except Exception as e:
            print('RedshiftController._stop: unexpected exception when resetting color:')
            print(e)
        try:
            return self._redshift.terminate(force=True)
        except Exception as e:
            # xflux has crashed in the meantime?
            print('RedshiftController._stop: unexpected exception when terminating redshift:')
            print(e)
            return True

    def _preview_color(self, preview_color, return_color):
        # WIthout first setting the color to the off color, the
        # preview does nothing when the preview_color and return_color
        # are equal, which happens in daytime when you try to preview
        # your currently chosen nighttime color. Don't know if this is
        # a fluxgui bug or an xflux bug.
        self._change_color_immediately(settings.off_temperature)
        self._change_color_immediately(preview_color)
        time.sleep(5)
        self._change_color_immediately(return_color)

    def _create_startup_arg_list(self, color='3400', **kwargs):
        startup_args = []
        if "latitude" in kwargs and kwargs['latitude']:
            startup_args += ["-l", f"{kwargs['latitude']}:{kwargs['longitude']}"]
        if "color" in kwargs and kwargs["color"]:
            startup_args += ["-t", f"6500K:{color}"]

        return startup_args

    def _change_color_immediately(self, new_color):
        self._set_redshift_screen_color(new_color)

    def _set_redshift_screen_color(self, color):
        self._current_color = color
        self._start()


class _RedshiftState(object):
    can_change_settings = False

    def __init__(self, controller_instance):
        self.controller_ref = weakref.ref(controller_instance)

    def start(self, startup_args):
        raise MethodUnavailableError("Redshift cannot start in its current state")

    def stop(self):
        raise MethodUnavailableError("Redshift cannot stop in its current state")

    def preview(self, preview_color):
        raise MethodUnavailableError("Redshift cannot preview in its current state")

    def toggle_pause(self):
        raise MethodUnavailableError("Redshift cannot pause/unpause in its current state")

    def set_setting(self, **kwargs):
        raise MethodUnavailableError("Redshift cannot alter settings in its current state")


class _InitState(_RedshiftState):
    def start(self, startup_args):
        self.controller_ref()._start(startup_args)
        self.controller_ref().state = self.controller_ref().states["RUNNING"]

    def stop(self):
        return True

    def set_setting(self, **kwargs):
        for key, value in kwargs.items():
            self.controller_ref().init_kwargs[key] = str(value)


class _TerminatedState(_RedshiftState):
    def stop(self):
        return True


class _AliveState(_RedshiftState):
    can_change_settings = True

    def stop(self):
        success = self.controller_ref()._stop()
        if success:
            self.controller_ref().state = self.controller_ref().states["TERMINATED"]
        return success

    def set_setting(self, **kwargs):
        self.controller_ref()._set_redshift_settings(**kwargs)


class _RunningState(_AliveState):
    def toggle_pause(self):
        self.controller_ref()._change_color_immediately(self.controller_ref()._pause_color)
        self.controller_ref().state = self.controller_ref().states["PAUSED"]

    def preview(self, preview_color):
        self.controller_ref()._preview_color(preview_color, self.controller_ref()._current_color)


class _PauseState(_AliveState):
    def toggle_pause(self):
        self.controller_ref()._change_color_immediately(self.controller_ref()._current_color)
        self.controller_ref().state = self.controller_ref().states["RUNNING"]

    def preview(self, preview_color):
        self.controller_ref()._preview_color(preview_color, self.controller_ref()._pause_color)
