import math

class Ratings:
    @staticmethod
    def calculate_stream_rating(beatmap):
        """
        Converts the computed beatmap.streams_length into an integer stream rating between 0 and 5.
        """
        s = beatmap.streams_length
        if s < 6:
            return 0
        elif s < 12:
            return 1
        elif s < 18:
            return 2
        elif s < 24:
            return 3
        elif s < 30:
            return 4
        else:
            return 5

    @staticmethod
    def calculate_jump_rating(hit_objects, stream_threshold=150):
        """
        Calculates the jump rating:
          - Computes the Euclidean distance between consecutive hit_objects that are not part of a stream
            (i.e. the time difference is greater than stream_threshold).
          - For example, divides the average distance by 100 to generate a rating (maximum 5 points).
        """
        distances = []
        for i in range(1, len(hit_objects)):
            interval = hit_objects[i]['time'] - hit_objects[i-1]['time']
            if interval > stream_threshold:
                dx = hit_objects[i]['x'] - hit_objects[i-1]['x']
                dy = hit_objects[i]['y'] - hit_objects[i-1]['y']
                dist = math.sqrt(dx**2 + dy**2)
                distances.append(dist)
        if not distances:
            return 0
        avg_distance = sum(distances) / len(distances)
        rating = int(avg_distance // 100)
        return min(rating, 5)

    @staticmethod
    def calculate_finger_control_rating(hit_objects):
        """
        Calculates the finger control rating:
          - For each sequence of three consecutive hit_objects, computes the angle between the two vectors.
          - A lower average angle (indicating sharper changes) is assumed to be more difficult.
          - Uses linear interpolation: if avg_angle is 45 degrees or less then rating is 5; if 135 degrees or more then 0.
        """
        if len(hit_objects) < 3:
            return 0
        angles = []
        for i in range(1, len(hit_objects) - 1):
            p0 = hit_objects[i - 1]
            p1 = hit_objects[i]
            p2 = hit_objects[i + 1]
            v1 = (p1['x'] - p0['x'], p1['y'] - p0['y'])
            v2 = (p2['x'] - p1['x'], p2['y'] - p1['y'])
            mag1 = math.hypot(*v1)
            mag2 = math.hypot(*v2)
            if mag1 == 0 or mag2 == 0:
                continue
            dot = v1[0] * v2[0] + v1[1] * v2[1]
            cos_angle = max(min(dot / (mag1 * mag2), 1), -1)
            angle_rad = math.acos(cos_angle)
            angle_deg = math.degrees(angle_rad)
            angles.append(angle_deg)
        if not angles:
            return 0
        avg_angle = sum(angles) / len(angles)
        rating = (135 - avg_angle) / 90 * 5
        return int(round(max(0, min(rating, 5))))

    @staticmethod
    def calculate_aim_control_rating(hit_objects):
        """
        Calculates the aim control rating:
          - Computes the total distance between consecutive hit_objects to obtain an average distance.
          - A larger average distance is assumed to indicate higher aim control difficulty.
          - For this example, the average distance is divided by 50 to produce a rating (maximum 5 points).
        """
        if len(hit_objects) < 2:
            return 0
        total_distance = 0
        for i in range(1, len(hit_objects)):
            dx = hit_objects[i]['x'] - hit_objects[i-1]['x']
            dy = hit_objects[i]['y'] - hit_objects[i-1]['y']
            total_distance += math.hypot(dx, dy)
        avg_distance = total_distance / (len(hit_objects) - 1)
        rating = int(avg_distance // 50)
        return min(rating, 5)
