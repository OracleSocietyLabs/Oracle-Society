
import threading, time, random
from relay_server import serve, world

if __name__ == "__main__":
    t = threading.Thread(target=serve, kwargs={"host":"127.0.0.1", "port":8011}, daemon=True)
    t.start()
    print("[demo] relay started on http://127.0.0.1:8011")
    areas = list(world.areas.keys()); dims = ["security","prosperity","control","culture","ecology"]
    while True:
        a = random.choice(areas); d = random.choice(dims); delta = random.choice([-5,-3,-1,1,2,3,5])
        world.area_bump(a, d, delta)
        time.sleep(1.0)
