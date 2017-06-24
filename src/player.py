import vlc


class Track():

    def __init__(self, logger, instance, mediapath):
        self.path = mediapath
        self.fullpath = str(mediapath.resolve())
        self.instance = instance
        self.logger = logger
        self.logger.debug("self.fullpath: " + self.fullpath)

        self.media = self.instance.media_new(self.fullpath)
        self.has_id3 = self.parse_new_track(self.media)

    def parse_new_track(self, media):
        media.parse()
        self.artist = media.get_meta(vlc.Meta.Artist)
        self.album = media.get_meta(vlc.Meta.Album)
        self.title = media.get_meta(vlc.Meta.Title)
        self.track_nb = media.get_meta(vlc.Meta.TrackNumber)

        if self.artist is None or self.album is None or self.title is None \
           or self.track_nb is None:
            return False
        else:
            return True

    def get_track_info_line(self):
        if self.has_id3 is False:
            return self.fullpath
        else:
            return self.track_nb + " - " + \
                self.artist + " - " + \
                self.title + " (" + \
                self.album + ")"


class Player():

    def get_interface_lines(self):
        print_file = ""
        if self.current_track:
            print_file = self.current_track.get_track_info_line()

        line_1 = " " + self.state + " " + print_file
        line_2 = ""
        return line_1, line_2

    def __init__(self, logger):
        self.instance = vlc.Instance()
        self.vlc_player = self.instance.media_player_new()
        self.logger = logger
        self.logger.debug("PlayerClass instanced")
        self.current_track = None
        self.state = "||"

    def play(self, file_path):
        fullpath = file_path.resolve()
        if self.current_track is not None and \
           self.current_track.fullpath == fullpath:
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
            self.current_track = Track(self.logger, self.instance,  fullpath)
            self.vlc_player.set_media(self.current_track.media)
            self.vlc_player.play()
