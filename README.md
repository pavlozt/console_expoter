# console_exporter

An interactive command prompt tool designed for generating metrics. It is utilized for debugging notifications, creating complex rules, and more.

Program exports set of `demo_*` metrics to URI `http://0.0.0.0:8000/metrics`

The program structure is intentionally left simple so that it can be easily expanded.


## Available commands

 - gauge - Gaudge testing loop.
 - hist - Histogram testing loop.
 - sum - Summary testing loop.
 - count - Counter testing loop.
 - exit - Exit command

## Requirements

To make everything work, some modern techniques are used. Therefore, it is necessary to install a set of modules related to asynchronous input output.
The modules are installed as usual via [requirements.txt](requirements.txt) file.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
