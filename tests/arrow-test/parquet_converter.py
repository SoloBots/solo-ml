"""
check the size difference as well
"""
from google.protobuf.json_format import MessageToDict
from naoth.log import Reader as LogReader
from naoth.log import Parser
import pyarrow as pa
import pyarrow.parquet as pq
import math

def clean_proto_dict(obj):
    """
    1. Replaces 'Infinity', '-Infinity', 'NaN' strings with math floats.
    2. Converts empty dicts {} to None so Parquet doesn't choke on 0-field structs.
    """
    if isinstance(obj, dict):
        # Recursively clean children first
        cleaned_dict = {k: clean_proto_dict(v) for k, v in obj.items()}
        
        # Remove keys that resolved to empty dicts or retain them as None
        # Option: Convert empty child dicts to None
        cleaned_dict = {
            k: (None if v == {} else v) 
            for k, v in cleaned_dict.items()
        }
        
        # If the dict itself is empty, return None
        if not cleaned_dict:
            return None
            
        return cleaned_dict
        
    elif isinstance(obj, list):
        return [clean_proto_dict(v) for v in obj]
        
    elif isinstance(obj, str):
        if obj == "Infinity":
            return math.inf
        elif obj == "-Infinity":
            return -math.inf
        elif obj == "NaN":
            return math.nan
            
    return obj

my_parser = Parser()
my_parser.register("GoalPerceptTop", "GoalPercept")
my_parser.register("FieldPerceptTop", "FieldPercept")
my_parser.register("BallCandidatesTop", "BallCandidates")
my_parser.register("RoleDecisionModel", "RoleDecision")

parsed_messages = list()

with LogReader("game.log", my_parser) as reader:
    for frame in reader.read():
        try:
            frame_number = frame["FrameInfo"].frameNumber
        except Exception as e:
            print(
                f"FrameInfo not found in current frame  - will not parse any other frames from this log and continue with the next one"
            )
            break
        json_obj = {
            "frame_number": frame_number,
        }

        for repr_name in frame._fields:
            #print(repr_name, type(repr_name))
            #print(frame[repr_name])
            if frame[repr_name] == None:
                continue
            data = MessageToDict(frame[repr_name])
            if repr_name in ["BallCandidates", "BallCandidatesTop"]:
                for patch in data["patches"]:
                    del patch["data"]
                    del patch["type"]
            clean_msg_dict = clean_proto_dict(data)
            json_obj.update({repr_name: clean_msg_dict})

        parsed_messages.append(json_obj)


table = pa.Table.from_pylist(parsed_messages)
pq.write_table(table, "robot_run_02.parquet")
