# DO NOT CHANGE THIS FILE

# harness/publisher_beacons.py
"""
Publisher: sends one or more fake car beacons over UDP.
Port: 5005
Default message (if no env set):
  {"id":"veh_123","pos":[10.0,5.0],"speed":4.0,"ts":<now_ms>}
Environment variables (all optional):
- BEACON_DISABLE="1" -> send nothing and exit
- BEACON_MESSAGES='[{"id":"veh_123","pos":[10,5],"speed":4.0}]'  (JSON list; ts auto-filled)
- BEACON_INTERVAL_MS="50"   delay between messages
- BEACON_SLEEP_BEFORE_MS="1000"  initial delay before first send
"""

'''
So basically this is the dimulator that pretends to be a car and sends beacon messgaes.
In this case, a beacon is nothing but a message broadcasted by a vehicle to communicate its status. And in
this problem, a beacon contains:
- id: the id of the vehicle
- pos: the position of the vehicle
- speed: the speed of the vehicle
- ts: the timestamp of the beacon i.e. when the message was sent
And the beacon is sent over UDP to the neighbor_node.py script.
'''
import os, socket, json, time

HOST = "127.0.0.1"
PORT = 5005

def now_ms() -> int:
    # This is the function responsible for creating the timestamp
    return int(time.time() * 1000)

def main():
    # If the BEACON_DISABLE environment variable is set to 1, the script will exit
    if os.getenv("BEACON_DISABLE") == "1":
        return

    # Defaults
    msgs = [{"id": "veh_123", "pos": [10.0, 5.0], "speed": 4.0}] #fallback
    try:
        # If the BEACON_MESSAGES environment variable is set, the script will use the messages in the variable. I think this is to let the test scripts manipulate 
        # the beacons. Neef to check the test scripts to see how they are used.
        if "BEACON_MESSAGES" in os.environ:
            msgs = json.loads(os.environ["BEACON_MESSAGES"])
            # why is it checling for list? So the beacon is actually a list of dictionaries. 
            assert isinstance(msgs, list)
    except Exception:
        msgs = [{"id": "veh_123", "pos": [10.0, 5.0], "speed": 4.0}]

    interval_ms = int(os.getenv("BEACON_INTERVAL_MS", "50"))
    sleep_before_ms = int(os.getenv("BEACON_SLEEP_BEFORE_MS", "1000"))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # creates a basic udp socket
    try:
        time.sleep(sleep_before_ms / 1000.0) # the inital delay
        for i, m in enumerate(msgs):
            if "ts" not in m:
                m = {**m, "ts": now_ms()} # generates timestamp
            payload = json.dumps(m).encode("utf-8") # converts the dict to json
            sock.sendto(payload, (HOST, PORT)) #sends via UDP to port 5005. This is the port that the neighbor_node.py script is listening to.
            print(f"Sent message: {payload.decode()} to {HOST}:{PORT}", flush=True) # sneds what was sent (converts the bytes to string for display) (flush = True means print to stdout Didn't know this!!)
            if i != len(msgs) - 1:
                time.sleep(interval_ms / 1000.0) # delay between messages until the last message
    finally:
        sock.close()

if __name__ == "__main__":
    main()