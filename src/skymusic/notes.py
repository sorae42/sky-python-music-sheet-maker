
class Note:

    def __init__(self, instrument, pos=None):
        self.position = pos
        self.instrument = instrument #Instrument object owing the note
        if pos is not None:
            self.index = (pos[0] * instrument.get_num_columns()) + pos[1]
        else:
            self.index = None

    def get_position(self):
        '''Return the note position as a tuple row/column'''
        return self.position

    def set_position(self, pos):
        '''Sets the position tuple from row and column values'''
        self.position = pos
        self.index = (pos[0] * self.instrument.get_num_columns()) + pos[1]

    def get_index(self):
        '''Returns the note index in Sky grid'''
        return self.index

    def get_highlighted_frames(self):
        return self.instrument.get_highlighted_frames(self.get_position())

    def is_highlighted(self):
        highlighted_frames = self.get_highlighted_frames()
        if len(highlighted_frames) > 0:
            return True
        else:
            return False

    def __str__(self):
        return f"<{self.index}, pos={self.position}, highlighted frames={self.get_highlighted_frames()}>"

