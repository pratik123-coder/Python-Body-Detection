import random

class MyPerson:
    """
    Represents a person being tracked.
    Tracks their position, direction, and state.
    """
    def __init__(self, person_id, x, y, max_age):
        self.person_id = person_id  # Unique identifier
        self.x = x                 # Current X-coordinate
        self.y = y                 # Current Y-coordinate
        self.tracks = []           # History of positions (track path)
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.done = False          # Whether the person is no longer being tracked
        self.state = '0'           # Tracking state (e.g., '0' for not yet crossed a line)
        self.age = 0               # Age of the person in frames
        self.max_age = max_age     # Max age before a person is considered "timed out"
        self.direction = None      # Direction of movement ('up' or 'down')

    def get_color(self):
        return self.color

    def get_tracks(self):
        return self.tracks

    def get_id(self):
        return self.person_id

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def is_timed_out(self):
        return self.done

    def update_position(self, new_x, new_y):
        self.age = 0
        self.tracks.append((self.x, self.y))
        self.x, self.y = new_x, new_y

    def mark_done(self):
        self.done = True

    def increment_age(self):
        self.age += 1
        if self.age > self.max_age:
            self.done = True

    def moving_up(self, line_start, line_end):
        if len(self.tracks) >= 2:
            prev_y, curr_y = self.tracks[-2][1], self.tracks[-1][1]
            if self.state == '0' and prev_y >= line_end > curr_y:
                self.state = '1'
                self.direction = 'up'
                return True
        return False

    def moving_down(self, line_start, line_end):
        if len(self.tracks) >= 2:
            prev_y, curr_y = self.tracks[-2][1], self.tracks[-1][1]
            if self.state == '0' and prev_y <= line_start < curr_y:
                self.state = '1'
                self.direction = 'down'
                return True
        return False