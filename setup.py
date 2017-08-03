from setuptools import setup, find_packages
import versioneer

setup(
    name="lammps_tools",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=[
        'matplotlib',
        'numpy',
    ],
    include_package_data=True,
    packages=find_packages(),
    scripts=[
            'bin/lmp_avgs_to_tsv.py',
            'bin/lmp_log_to_tsv.py',
            'bin/lmp_plot_chunks.py',
            'bin/tsv_eq_trends.py'
    ]
)
