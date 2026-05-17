from cakrawala_radar import TrajectorySimulator


sim = TrajectorySimulator()
track = sim.generate_archipelago_route("OBJ-JKT-NAT", "jakarta_natuna", steps=12)

for point in track[:3]:
    print(point)
