# Pelstix Digital0cean-autoscaler
# Dynamic Scaling of DigitalOcean Droplets

This Python script allows for the dynamic scaling of DigitalOcean Droplets based on CPU usage. It monitors the CPU usage of a specified Droplet and scales the number of instances up or down as needed.

## Requirements

- Python 3.x
- `requests` library: Install it using `pip install requests`
- `psutil` library: Install it using `pip install psutil`
- `python-dotenv` library: Install it using `pip install python-dotenv` (for managing environment variables)

## Getting Started

1. Clone the repository:

   ```bash
   git clone https://github.com/pelstix/Digital0cean-autoscaler.git
   cd Digital0cean-autoscaler

Some Configurations to bear in mind

cpu_threshold: The CPU usage threshold for scaling (default is set to 70%).
load_balancer_id: The ID of the DigitalOcean Load Balancer to manage.
max_instances: The maximum number of instances you want to scale to.
min_instances: The minimum number of instances you want to scale to.



