#!/bin/bash

# Activate virtual environment
echo "Activating virtual environment..."
source gpio/bin/activate

# Synchronize the system clock
echo "Synchronizing system clock..."
sudo chronyc -a makestep

# Launch the PWM Python script
echo "Starting Start_pwm.py..."
python Start_pwm.py
