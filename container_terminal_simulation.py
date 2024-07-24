import simpy
import random

# Constants
AVG_TIME_BETWEEN_ARRIVALS = 5 * 60  
NUM_CONTAINERS = 150
TIME_PER_CONTAINER = 3  
TRUCK_CYCLE_TIME = 6  
SIMULATION_TIME = 10000  


class ContainerTerminal:
    def __init__(self, env):
        self.env = env
        self.berths = simpy.Resource(env, capacity=2)
        self.cranes = simpy.Resource(env, capacity=2)
        self.trucks = simpy.Resource(env, capacity=3)
    
    def berth_vessel(self, vessel):
        with self.berths.request() as request:
            yield request
            print(f"{self.env.now}: {vessel} berthed")
            yield self.env.process(self.unload_vessel(vessel))
            print(f"{self.env.now}: {vessel} completed unloading and left the berth")

    def unload_vessel(self, vessel):
        for i in range(NUM_CONTAINERS):
            with self.cranes.request() as crane_req:
                yield crane_req
                print(f"{self.env.now}: {vessel} crane started unloading container {i + 1}")
                yield self.env.timeout(TIME_PER_CONTAINER)
                yield self.env.process(self.transport_container(vessel, i + 1))

    def transport_container(self, vessel, container_id):
        with self.trucks.request() as truck_req:
            yield truck_req
            print(f"{self.env.now}: {vessel} truck transporting container {container_id}")
            yield self.env.timeout(TRUCK_CYCLE_TIME)
            print(f"{self.env.now}: {vessel} truck back")


def vessel_generator(env, terminal):
    vessel_id = 0
    while True:
        yield env.timeout(random.expovariate(1 / AVG_TIME_BETWEEN_ARRIVALS))
        vessel_id += 1
        env.process(terminal.berth_vessel(f"Vessel_{vessel_id}"))


env = simpy.Environment()
terminal = ContainerTerminal(env)
env.process(vessel_generator(env, terminal))
env.run(until=SIMULATION_TIME)
