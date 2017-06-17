import vlc


class Track():
    logger = None
    path = None
    instance = None
    media = None
    fullpath = ""
    artist = ""
    album = ""
    title = ""
    track_nb = ""

    def __init__(self, logger, instance, mediapath):
        self.path = mediapath
        self.fullpath = str(mediapath.resolve())
        self.instance = instance
        self.logger = logger
        self.logger.debug("self.fullpath: " + self.fullpath)

        self.media = self.instance.media_new(self.fullpath)
        self.parse_new_track(self.media)

    def parse_new_track(self, media):
        media.parse()
        self.artist = media.get_meta(vlc.Meta.Artist)
        self.album = media.get_meta(vlc.Meta.Album)
        self.title = media.get_meta(vlc.Meta.Title)
        self.track_nb = media.get_meta(vlc.Meta.TrackNumber)


class Player():

    state = "||"
    current_track = None
    instance = None
    vlc_player = None
    logger = None

    def get_interface_lines(self):
        print_file = ""
        if self.current_track:
            print_file = self.current_track.track_nb + " - " + \
                self.current_track.artist + " - " + \
                self.current_track.title + " (" + \
                self.current_track.album + ")"

        line_1 = " " + self.state + " " + print_file
        line_2 = ""
        return line_1, line_2

    def __init__(self, logger):
        self.instance = vlc.Instance()
        self.vlc_player = self.instance.media_player_new()
        self.logger = logger
        self.logger.debug("PlayerClass instanced")

    def play(self, file_path):
        fullpath = file_path.resolve()
        if self.current_track is not None and \
           self.current_track.fullpath == fullpath:
            if self.state == ">":
                self.state = "||"
                self.vlc_player.pause()
            else:
                self.state = ">"
                self.vlc_player.play()
        else:
            self.state = ">"
            self.current_track = Track(self.logger, self.instance,  fullpath)
            self.vlc_player.set_media(self.current_track.media)
            self.vlc_player.play()
