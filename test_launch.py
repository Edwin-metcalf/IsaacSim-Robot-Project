from isaacsim import SimulationApp
app = SimulationApp({'headless': True})

import isaacsim.core.api as api
print(dir(api))

app.close()
