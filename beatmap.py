import math

class Beatmap:
    def __init__(self, difficulty):
        self.circle_size = difficulty.get("CircleSize", 4)
        self.hp_drain = difficulty.get("HPDrainRate", 2)
        self.overall_difficulty = difficulty.get("OverallDifficulty", 8)
        self.approach_rate = difficulty.get("ApproachRate", 9)

        self.skipped_bpms = set()   # BPM values to exclude
        self.streams = []           # Each stream is a dict with keys 'length' and 'spacing'
        self.longest_stream = 0
        self.streams_length = 0     # Overall stream length statistic (cube-root of weighted sum)
        self.bpm_frequencies = {}   # {bpm: {"streams": count, "non_streams": count}}

    def update_bpm_frequencies(self, is_stream, bpm):
        if bpm not in self.bpm_frequencies:
            self.bpm_frequencies[bpm] = {"streams": 0, "non_streams": 0}
        if is_stream:
            self.bpm_frequencies[bpm]["streams"] += 1
        else:
            self.bpm_frequencies[bpm]["non_streams"] += 1

    def reset_streams(self):
        self.streams = []
        self.longest_stream = 0
        self.streams_length = 0

class Stream:
    def __init__(self):
        self.length = 0         # Number of consecutive stream objects
        self.last_interval = 0  # Last calculated BPM
        self.spacing = 0.0      # Accumulated spacing within the stream

    def add_bpm(self, bpm, spacing):
        self.last_interval = bpm
        self.length += 1
        self.spacing += spacing

    def reset(self):
        self.length = 0
        self.last_interval = 0
        self.spacing = 0.0

class BeatmapProcessor:
    """
    Class that processes the osu! beatmap to compute stream (repeated hit objects) statistics.
    The process_beatmap method calculates stream statistics based on hit objects.
    """
    def __init__(self, beatmap):
        self.beatmap = beatmap
        self.stream = Stream()

    def process_beatmap(self, timing_points, hit_objects):
        prev = None
        # Iterate through hit_objects (ignoring exceptions like spinners)
        for obj in hit_objects:
            if prev is not None:
                # For current time, use the first TimingPoint (simple implementation)
                timing_point = timing_points[0]
                self.process_interval(prev, obj, timing_point)
            prev = obj
        self.terminate_stream()
        self.calculate_streams_statistics()

        # Slight correction if longest_stream is greater than 0
        if self.beatmap.longest_stream > 0:
            self.beatmap.longest_stream += 1
            self.beatmap.streams_length += 1
        return self.beatmap

    def process_interval(self, prev_obj, cur_obj, timing_point):
        """
        Converts the time difference to BPM and processes the stream calculation.
        """
        time_diff = cur_obj['time'] - prev_obj['time']
        if time_diff <= 0:
            return

        interval_bpm = 60000.0 / time_diff
        timing_point_bpm = round(60000.0 / timing_point['beat_length'])
        division = round(interval_bpm / timing_point_bpm)
        if division >= 3:
            bpm = round(timing_point_bpm * division / 4)
            denom = 54.4 - 4.48 * self.beatmap.circle_size  # Default circle_size = 5
            spacing = time_diff / denom if denom != 0 else 0
            max_spacing = 4

            if (bpm in self.beatmap.skipped_bpms) or (spacing > max_spacing):
                self.beatmap.update_bpm_frequencies(is_stream=False, bpm=bpm)
                self.terminate_stream()
            elif (self.stream.last_interval == 0) or (abs(bpm - self.stream.last_interval) <= self.stream.last_interval / 5):
                self.beatmap.update_bpm_frequencies(is_stream=True, bpm=bpm)
                self.stream.add_bpm(bpm, spacing)
            else:
                self.terminate_stream()
                # Recursively process the current interval again
                self.process_interval(prev_obj, cur_obj, timing_point)
        else:
            self.terminate_stream()

    def terminate_stream(self):
        """
        If a stream exists, add it to the beatmap's streams list and then reset the stream.
        """
        if self.stream.length > 0:
            self.beatmap.streams.append({'length': self.stream.length, 'spacing': self.stream.spacing})
        self.stream.reset()

    def calculate_streams_statistics(self):
        """
        Sorts all streams in descending order by length and calculates the longest_stream and streams_length statistics.
        """
        if not self.beatmap.streams:
            self.beatmap.longest_stream = 0
            self.beatmap.streams_length = 0
            return

        self.beatmap.streams.sort(key=lambda s: s['length'], reverse=True)
        self.beatmap.longest_stream = self.beatmap.streams[0]['length']
        n = len(self.beatmap.streams)
        streams_length_acc = 0.0
        for idx, s in enumerate(self.beatmap.streams):
            weight = 1 - (idx / n)
            streams_length_acc += (s['length'] ** 3) * weight * 2.0 / n
        self.beatmap.streams_length = round(streams_length_acc ** (1/3))
