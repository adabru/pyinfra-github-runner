# pyinfra github runner

## Overview

This project uses [pyinfra](https://pyinfra.com/) to setup a self-hosted github runner on an arch server with ssh access. Configuration settings are managed using a `.env` file. You need python 3.x.

## Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/adabru/pyinfra-github-runner.git
   cd pyinfra-github-runner
   ```

2. Create and activate a virtual environment:

   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:

   ```sh
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory of the project and add your configuration settings:

   ```env
   # Example .env file
   KEY=value
   ```

## Usage

1. Load environment variables:

   ```sh
   source .env
   ```

2. Run pyinfra:
   ```sh
   pyinfra deploy.py
   ```

## Configuration

- All configuration settings should be added to the `.env` file.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```

```
