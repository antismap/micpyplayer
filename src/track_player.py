import vlc
import datetime
import play_queue
import track
from enum import Enum


class PlayerState(Enum):
    PLAYING = ">"
    PAUSED = "||"


class StringPrinter(object):
    @staticmethod
    def time_elapsed_time_left(elapsed_ms, left_ms):
        date_elapsed = datetime.datetime.fromtimestamp(elapsed_ms / 1000.0)
        date_left = datetime.datetime.fromtimestamp(left_ms / 1000.0)
        return date_elapsed.strftime('%M:%S') + " / " + date_left.strftime('%M:%S')


class TrackPlayer(object):

    def __init__(self, logger):
        self.instance = vlc.Instance()
        self.init_vlc_player()
        self.logger = logger
        self.logger.debug("PlayerClass instanced")
        self.state = PlayerState.PAUSED
        self.current_track = None

    def get_volume(self):
        return self.vlc_player.audio_get_volume()

    def volume_up(self):
        self.logger.debug("volume up")
        self.vlc_player.audio_set_volume(min(100, self.vlc_player.audio_get_volume() + 10))
        volume = self.vlc_player.audio_get_volume()
        self.logger.debug("current volume " + str(volume))
        return volume

    def volume_down(self):
        self.vlc_player.audio_set_volume(max(0, self.vlc_player.audio_get_volume() - 10))
        volume = self.vlc_player.audio_get_volume()
        self.logger.debug("current volume " + str(volume))
        return volume

    #  libvlc_media_player_get_position
    # vlm_get_media_instance_time(self, psz_name, i_instance):
    def init_vlc_player(self):
        self.vlc_player = self.instance.media_player_new()
        self.events = self.vlc_player.event_manager()
        self.events.event_attach(
            vlc.EventType.MediaPlayerEndReached, self.song_finished)

    def song_finished(self, event):
        self.logger.debug("got SongFinished event")
        popped_song = self.current_queue.pop_song()
        if popped_song is not None:
            current_track_fullpath = popped_song.resolve()
            self.logger.debug("resolved path " + str(current_track_fullpath))
            self.init_vlc_player()
            self.__play_track(current_track_fullpath)
        else:
            self.play_pause()

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

        line_1 = " " + self.state.value + " " + print_file

        return line_1, line_2, progress_bar_bars

    def play_pause(self):
        if self.state == PlayerState.PLAYING:
            self.logger.debug("PlayerClass:  set to pause")
            self.state = PlayerState.PAUSED
            self.vlc_player.pause()
        else:
            self.logger.debug("PlayerClass:  set to play")
            self.state = PlayerState.PLAYING
            self.vlc_player.play()

    def __play_track(self, song_full_path):
        if self.current_track is not None and \
                self.current_track.fullpath == str(song_full_path):
            self.play_pause()
        else:
            self.logger.debug("PlayerClass:  playing new track")
            self.state = PlayerState.PLAYING
            self.current_track = track.Track(
                self.logger, self.instance, song_full_path)
            self.logger.debug("current track set")
            self.vlc_player.set_media(self.current_track.media)
            self.logger.debug("media set")
            self.vlc_player.play()
            self.logger.debug("after play")

    def play_new_queue(self, our_play_queue):
        self.current_queue = our_play_queue
        current_track_fullpath = our_play_queue.pop_song().resolve()
        self.__play_track(current_track_fullpath)
