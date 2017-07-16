import vlc


class Track(object):

    def __init__(self, logger, instance, mediapath):
        self.path = mediapath
        self.fullpath = str(mediapath.resolve())
        self.instance = instance
        self.logger = logger
        self.logger.debug("self.fullpath: %s", self.fullpath)

        self.media = self.instance.media_new(self.fullpath)
        self.has_id3 = self.parse_new_track(self.media)

    def parse_new_track(self, media):
        media.parse()
        self.artist = media.get_meta(vlc.Meta.Artist)
        self.album = media.get_meta(vlc.Meta.Album) or "Unknown Album"
        self.title = media.get_meta(vlc.Meta.Title)
        # Display a little symbol instead of the track number if it's unknown
        self.track_nb = media.get_meta(vlc.Meta.TrackNumber) or "*"

        # Display track info if we have at least an artist and a title,
        # else display the file name
        return self.artist and self.title

    def get_track_info_line(self):
        if self.has_id3:
            return "{s.track_nb} - {s.artist} - {s.title} ({s.album})"\
                   .format(s=self)
        else:
            return self.fullpath

#    def get_current_time(self):


class Player(object):
    #  libvlc_media_player_get_position
    # vlm_get_media_instance_time(self, psz_name, i_instance):

    def song_finished(self, event):
        self.logger.debug("song finished!")

    def get_interface_lines(self):
        print_file = ""
        #current_time = ""
        if self.current_track:
            print_file = self.current_track.get_track_info_line()
            #current_time = self.current_track.get_current_time()

        line_1 = " " + self.state + " " + print_file
        line_2 = "current %: " + str(self.vlc_player.get_position())
        return line_1, line_2

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

    def play(self, file_path):
        fullpath = file_path.resolve()
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
            self.current_track = Track(self.logger, self.instance, fullpath)

            self.vlc_player.set_media(self.current_track.media)
            self.vlc_player.play()
