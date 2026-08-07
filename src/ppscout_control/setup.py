from setuptools import find_packages, setup

package_name = 'ppscout_control'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='thales',
    maintainer_email='thalesasoares02@hotmail.com',
    description='High-level Python control API and CLI tools for the Scout Mini base and Piper arm',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'drive = ppscout_control.cli.drive:main',
            'arm_pose = ppscout_control.cli.arm_pose:main',
            'gripper = ppscout_control.cli.gripper:main',
            'demo = ppscout_control.cli.demo:main',
        ],
    },
)
