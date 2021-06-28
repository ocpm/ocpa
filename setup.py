from setuptools import setup

import ocpa
setup(
    name = ocpa.__name__,
    packages = [
        'ocpa', 'ocpa.algo', 'ocpa.objects', 'ocpa.util', 'ocpa.visualization',
        'ocpa.algo.discovery', 'ocpa.algo.discovery.mvp', 'ocpa.algo.discovery.ocpn', 'ocpa.algo.discovery.mvp.projection', 'ocpa.algo.discovery.mvp.projection.versions', 'ocpa.algo.discovery.ocpn.versions', 
        'ocpa.algo.evaluation', 'ocpa.algo.evaluation.precision',
        'ocpa.objects.log', 'ocpa.objects.log.converter', 'ocpa.objects.log.converter.versions', 'ocpa.objects.log.importer.mdl', 'ocpa.objects.log.importer.ocel', 'ocpa.objects.log.importer.ocel.versions', 'ocpa.objects.log.util', 'ocpa.objects.oc_petri_net', 
        'ocpa.util', 
        'ocpa.visualization', 'ocpa.visualization.oc_petri_net', 'ocpa.visualization.oc_petri_net.util', 'ocpa.visualization.oc_petri_net.versions'
        ],
    py_modules=[ocpa.__name__],
    include_package_data=True,
    version = ocpa.__version__,      
    license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    description = ocpa.__doc__.strip(),   
    author=ocpa.__author__,
    author_email=ocpa.__author_email__,
    url = 'https://github.com/gyunamister/ocpa',   # Provide either the link to your github or to your website
    install_requires=[            # I get to this in a second
            "pm4py>=2.2.0",
            "setuptools",
            "jsonschema",
        ],
    # classifiers=[
    # 'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    # 'Intended Audience :: Developers',      # Define that your audience are developers
    # 'Topic :: Software Development :: Build Tools',
    # 'License :: OSI Approved :: MIT License',   # Again, pick a license
    # 'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    # 'Programming Language :: Python :: 3.4',
    # 'Programming Language :: Python :: 3.5',
    # 'Programming Language :: Python :: 3.6',
    # ],
)
