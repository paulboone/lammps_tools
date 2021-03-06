from setuptools import setup, find_packages
import versioneer

setup(
    name="lammps_tools",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    install_requires=[
        'matplotlib',
        'numpy',
        'scipy',
    ],
    include_package_data=True,
    packages=find_packages(),
    scripts=[
            'bin/lammpstrj_to_npy.py',
            'bin/lmp_avgs_to_tsv.py',
            'bin/lmp_log_to_tsv.py',
            'bin/lmp_chunks_to_tsv.py',
            'bin/lmp_data_to_tsv.py',
            'bin/lmp_data_to_xyz.py',
            'bin/npytraj_diffusivity.py',
            'bin/tsv_plot_chunks.py',
            'bin/tsv_eq_trends.py',
            'bin/tsv_stats.py',
            'bin/tsv_plot_cols_vs_time.py',
            'bin/tsv_plot_stacked_bar.py'
    ]
)
