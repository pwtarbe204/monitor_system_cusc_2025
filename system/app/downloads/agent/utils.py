from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Constants
# URL = os.getenv('SERVER', 'http://192.168.1.9:5000/')

# Global metrics
TEST = 0
tb_ram = []
tb_cpu = []

def reset_metrics():
    """Reset global metrics."""
    global TEST, tb_ram, tb_cpu
    TEST = 0
    tb_ram.clear()
    tb_cpu.clear()