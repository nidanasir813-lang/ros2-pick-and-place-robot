from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'pick_and_place'

setup(
    name=package_name,
    version='1.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'worlds'),
            glob('worlds/*.wbt')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Nida Nasir',
    maintainer_email='nidanasir813@gmail.com',
    description='Autonomous pick-and-place robotic arm simulation using ROS2 Jazzy and Webots',
    license='MIT',
    entry_points={
        'console_scripts': [
            'arm_controller = pick_and_place.arm_controller:main',
            'webots_bridge  = pick_and_place.webots_bridge:main',
        ],
    },
)
