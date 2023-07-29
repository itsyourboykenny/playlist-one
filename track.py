class Track:
    def __init__(self, id: int | str = None, title: str = None, artist: str = None, album: str = None, duration: int = None, explicit = True, release_date: int = None, album_type: int = None):
        # album_type
        #   0 = album
        #   1 = single
        #   2 = compilation
        
        if id == None:
            print("Error: Cannot initialize a Track object with a blank ID")
            raise ValueError()

        self.id: int | str = id
        self.title: str = title
        self.artist: str = artist
        self.album: str = album
        self.duration: int = duration
        self.explicit = explicit
        self.release_date: int = release_date
        self.album_type: int = album_type