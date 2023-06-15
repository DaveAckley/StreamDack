from setuptools import setup
import datetime
stamp = datetime.datetime.now()
stamp = stamp.replace(year=stamp.year-2022)
version = stamp.strftime('%Y.%m.%d.%H%M')
setup(
    name='StreamDack',
    version=version,
    entry_points={
        'console_scripts': [
            'StreamDack=main:run'
        ]
    }
)
