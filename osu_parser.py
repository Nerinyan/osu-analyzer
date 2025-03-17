import sys

class OsuParser:
    @staticmethod
    def parse_osu_file(file_path):
        """
        Reads the osu! file and parses the [TimingPoints], [HitObjects], and [Difficulty] sections.
        - TimingPoints: Each line is in the format "offset,beatLength,...".
        - HitObjects: Each line is in the format "x,y,time,...", extracting coordinates and timing.
        - Difficulty: Extracts key-value pairs for HPDrainRate, CircleSize, OverallDifficulty, and ApproachRate.
        """
        timing_points = []
        hit_objects = []
        difficulty = {}
        section = None
        try:
            with open(file_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("//"):
                        continue
                    # Change section when encountering a new header
                    if line.startswith("[") and line.endswith("]"):
                        section = line[1:-1]
                        continue
                    if section == "TimingPoints":
                        parts = line.split(',')
                        if len(parts) >= 2:
                            try:
                                offset = float(parts[0])
                                beat_length = float(parts[1])
                                timing_points.append({'offset': offset, 'beat_length': beat_length})
                            except ValueError:
                                continue
                    elif section == "HitObjects":
                        parts = line.split(',')
                        if len(parts) >= 3:
                            try:
                                x = float(parts[0])
                                y = float(parts[1])
                                time = float(parts[2])
                                hit_objects.append({'x': x, 'y': y, 'time': time})
                            except ValueError:
                                continue
                    elif section == "Difficulty":
                        # Expect lines like "CircleSize:5" (or float value)
                        if ":" in line:
                            key, value = line.split(":", 1)
                            key = key.strip()
                            try:
                                difficulty[key] = float(value.strip())
                            except ValueError:
                                continue
        except FileNotFoundError:
            sys.exit(f"File not found: {file_path}")

        # Sort hit_objects by time
        hit_objects.sort(key=lambda obj: obj['time'])
        # Sort TimingPoints by offset
        timing_points.sort(key=lambda tp: tp['offset'])
        
        return timing_points, hit_objects, difficulty