from setuptools import setup, find_packages

setup(
    name="medical-symptoms-agent",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "Flask==2.3.3",
        "python-dotenv==1.0.0",
        "requests==2.31.0",
        "Pillow==10.0.1",
    ],
    python_requires=">=3.8",
)
