import vlc
import datetime
import play_queue
import track


class StringPrinter(object):
    @staticmethod
    def time_elapsed_time_left(elapsed_ms, left_ms):
        date_elapsed = datetime.datetime.fromtimestamp(elapsed_ms/1000.0)
        date_left = datetime.datetime.fromtimestamp(left_ms/1000.0)
        return date_elapsed.strftime('%M:%S') + " / " + date_left.strftime('%M:%S')


class TrackPlayer(object):
    #  libvlc_media_player_get_position
    # vlm_get_media_instance_time(self, psz_name, i_instance):

    def song_finished(self, event):
        self.logger.debug("song finished!")

    def get_interface_lines(self, max_x):
        print_file = ""
        # current_time = ""
        if self.current_track:
            print_file = self.current_track.get_track_info_line()
            # current_time = self.current_track.get_current_time()
            line_2 = StringPrinter.time_elapsed_time_left(
                self.vlc_player.get_time(), self.vlc_player.get_length())
            progress_bar_bars = int(
                (((self.vlc_player.get_position() * 100.0) * (max_x - 2)) / 100))
        else:
            line_2 = ""
            progress_bar_bars = 0

        line_1 = " " + self.state + " " + print_file

        return line_1, line_2, progress_bar_bars

    def __init__(self, logger):
        self.instance = vlc.Instance()
        self.vlc_player = self.instance.media_player_new()
        self.events = self.vlc_player.event_manager()
        self.events.event_attach(
            vlc.EventType.MediaPlayerEndReached, self.song_finished)
        self.logger = logger
        self.logger.debug("PlayerClass instanced")
        self.state = "||"
        self.current_track = None

    def play(self, our_play_queue):
        fullpath = our_play_queue.pop_song().resolve()
        if self.current_track is not None and \
           self.current_track.fullpath == str(fullpath):
            if self.state == ">":
                self.logger.debug("PlayerClass:  set to pause")
                self.state = "||"
                self.vlc_player.pause()
            else:
                self.logger.debug("PlayerClass:  set to play")
                self.state = ">"
                self.vlc_player.play()
        else:
            self.logger.debug("PlayerClass:  playing new track")
            self.state = ">"
            self.current_track = track.Track(
                self.logger, self.instance, fullpath)

            self.vlc_player.set_media(self.current_track.media)
            self.vlc_player.play()
