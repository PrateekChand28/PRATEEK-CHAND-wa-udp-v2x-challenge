#Author: Prateek Chand
#Date: 09/14/2025
#This should be the only file you edit. You are free to look at other files for reference, but do not change them.
#Below are are two methods which you must implement: euclidean_dist_to_origin and nearest_neighbor as well as the main function beacon handling. 
#Helper Functions are allowed, but not required. You must not change the imports, the main function signature, or the return value of the main function.


"""
Neighbor Table

Listen on UDP 127.0.0.1:5005 for beacon messages:
  {"id":"veh_XXX","pos":[x,y],"speed":mps,"ts":epoch_ms}

Collect beacons for ~1 second starting from the *first* message.
Then print exactly ONE JSON line and exit:

{
  "topic": "/v2x/neighbor_summary",
  "count": <int>,
  "nearest": {"id": "...", "dist": <float>} OR null,
  "ts": <now_ms>
}

Constraints:
- Python 3 stdlib only.
- Ignore malformed messages; don’t crash.
- Do NOT listen to ticks (5006).
"""

import socket, json, time, math, sys
from typing import Dict, Any, Optional, Tuple

HOST = "127.0.0.1"
PORT_BEACON = 5005
COLLECT_WINDOW_MS = 1000  # ~1 second

def now_ms() -> int:
    return int(time.time() * 1000)

def euclidean_dist_to_origin(pos) -> float:
    # TODO: validate pos is [x,y] of numbers; compute distance
    # return float(math.hypot(x, y))

    if not isinstance(pos, list) or len(pos) != 2 or not all(isinstance(x, (int, float)) for x in pos):
        return float('inf')
    
    return math.hypot(pos[0], pos[1])

def nearest_neighbor(neighbors: Dict[str, Dict[str, Any]]) -> Optional[Tuple[str, float]]:
    if not neighbors or not isinstance(neighbors, dict):
        return None
    
    min_dist = float('inf')
    min_id = None
    # iterate over neighbors
    for car_id, car_info in neighbors.items():
        # compute the distance
        dist = euclidean_dist_to_origin(car_info["pos"])
        if dist < min_dist:
            min_dist = dist
            min_id = car_id

    if min_id is not None and min_dist != float('inf'):
        return min_id, min_dist
    else:
        return None

def main() -> int:
    """
    Basically this is the main method that listens at the beacon port and collects the beacons.
    The beacons are collected for 1 second starting from the first message.
    If the 1 second is over, the method will break and return the nearest neighbor.
    In case no message is received for 1.5 seconds, the method will break and return the nearest neighbor.
    The beacons received are in json format which needs to be parsed and validated.
    Then the beacons are turned into neighbors dictionary.
    """
    neighbors: Dict[str, Dict[str, Any]] = {}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT_BEACON))
    sock.settimeout(1.5) # if no message for 1.5 seconds, break

    first_ts: Optional[int] = None
    try:
        while True:
            # tries to recieve UDP message (up to 4096 bytes)
            try:
                data, _ = sock.recvfrom(4096)
            # if no message for 1.5 seconds, break
            except socket.timeout:
                break  
            # try to decode the message as JSON
            try:
                msg = json.loads(data.decode("utf-8"))
            except json.JSONDecodeError:
                # if not valid JSON, continue to next message
                continue  
            
            if not isinstance(msg, dict):
                continue
            
            req_keys = ["id", "pos", "speed", "ts"]

            if not all(key in msg for key in req_keys):
                continue
            
            if not isinstance(msg["id"], str):
                continue

            if not isinstance(msg["pos"], list) or len(msg["pos"]) != 2 or not all(isinstance(x, (int, float)) for x in msg["pos"]):
                continue

            if not isinstance(msg["speed"], (int, float)):
                continue

            if not isinstance(msg["ts"], int):
                continue

            neighbors[msg["id"]] = {
                    "pos": msg["pos"], 
                    "speed": msg["speed"], 
                    "last_ts": msg["ts"]
            }

            now = now_ms()
            if first_ts is None:
                first_ts = now
            # stop after ~1 second from first message
            if first_ts is not None and (now - first_ts) >= COLLECT_WINDOW_MS:
                break

    finally:
        sock.close()

    # Build summary
    nn = nearest_neighbor(neighbors)
    summary = {
        "topic": "/v2x/neighbor_summary",
        "count": len(neighbors),
        "nearest": None if nn is None else {"id": nn[0], "dist": nn[1]},
        "ts": now_ms(),
    }
    print(json.dumps(summary), flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
