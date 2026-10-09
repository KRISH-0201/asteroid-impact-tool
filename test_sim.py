import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from main import AsteroidLauncher  # type: ignore

def test_simulation():
    launcher = AsteroidLauncher()
    try:
        results = launcher.launch_asteroid(
            asteroid_type='stone',
            diameter=100.0,
            speed=17.0,
            angle=45.0,
            latitude=40.7128,
            longitude=-74.0060,
            altitude=100.0
        )
        print("Simulation successful.")
        print("Energy MT:", results['impact_basic']['energy_megatons'])
    except Exception as e:
        print(f"Simulation failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simulation()
