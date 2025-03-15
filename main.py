import sys
from osu_parser import OsuParser
from beatmap import Beatmap, BeatmapProcessor
from ratings import Ratings

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <beatmap.osu>")
        sys.exit(1)
    file_path = sys.argv[1]
    
    timing_points, hit_objects = OsuParser.parse_osu_file(file_path)
    if not timing_points or not hit_objects:
        print("Parsing failed: Insufficient TimingPoints or HitObjects data")
        sys.exit(1)
    
    # Calculate stream (repeated hit objects) rating
    beatmap = Beatmap(circle_size=5)  # Adjust circle_size as needed
    processor = BeatmapProcessor(beatmap)
    beatmap = processor.process_beatmap(timing_points, hit_objects)
    stream_rating = Ratings.calculate_stream_rating(beatmap)
    
    # Calculate other ratings
    jump_rating = Ratings.calculate_jump_rating(hit_objects)
    finger_control_rating = Ratings.calculate_finger_control_rating(hit_objects)
    aim_control_rating = Ratings.calculate_aim_control_rating(hit_objects)
    
    print("Stream:", stream_rating)
    print("Jump:", jump_rating)
    print("Finger Control:", finger_control_rating)
    print("Aim Control:", aim_control_rating)

if __name__ == "__main__":
    main()
