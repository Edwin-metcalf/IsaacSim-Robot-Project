from isaacsim import SimulationApp
app = SimulationApp({'headless': True})

import subprocess
result = subprocess.run(['find', '/usr/local/lib', '-name', '*.py', '-exec', 'grep', '-1', 'RMPFlow', '{}', ';'], capture_output=True, text=True)
print(result.stdout[:3000])

app.close()
