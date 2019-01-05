import vlc


class Track(object):

    def __init__(self, logger, instance, mediapath):
        self.artist = None
        self.album = None
        self.title = None
        self.track_nb = None
        self.art_url = None

        self.path = mediapath
        self.fullpath = str(mediapath.resolve())
        self.instance = instance
        self.logger = logger
        self.logger.debug("track init: self.fullpath: %s", self.fullpath)

        self.media = self.instance.media_new(self.fullpath)
        self.has_id3 = self.parse_new_track(self.media)

    def parse_new_track(self, media):
        media.parse()
        self.artist = media.get_meta(vlc.Meta.Artist)
        self.album = media.get_meta(vlc.Meta.Album) or "Unknown Album"
        self.title = media.get_meta(vlc.Meta.Title)
        self.art_url = media.get_meta(vlc.Meta.ArtworkURL)
        # Display a little symbol instead of the track number if it's unknown
        self.track_nb = media.get_meta(vlc.Meta.TrackNumber) or "*"
        self.logger.debug(
            "parsed track with nb {s.track_nb} artist {s.artist} title {s.title} album {s.album}".format(s=self))
        # Display track info if we have at least an artist and a title,
        # else display the file name
        self.logger.debug("end parse_new_track")
        return self.artist and self.title

    def get_track_info_line(self):
        if self.has_id3:
            return "{s.track_nb} - {s.artist} - {s.title} ({s.album})".format(s=self)
        else:
            return self.fullpath

    def get_album_art_url(self):
        return self.art_url
