# ocUpdates 

ocUpdates is an app that aims to provide continious service updates on the status of diverse aspects of OC Tranpo's operations. It also aims to improve upon already available tools and receive continious updates with new features.

---

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## App Installation

We currently do not support any local installs as a majority of the data we collect for real-time information comes from OC Transpo's api, so we need a continous network connection. We apologize for any inconvience this may cause.

## Development Installation
> Make sure you have [Python](https://www.python.org/downloads/) installed.
> Make sure you have [NodeJS](https://nodejs.org/en/download) installed.

1. Install the ``shared`` package in editable mode from the project root.
    ```bash
    pip install -e ./shared
    ```
2. Install and run the backend (follow the instructions in the backend/README.md).
3. Install and run the frontend (follow the instructions in the frontend/README.md)<br>

> PSST! You're using one terminal instance each for the frontend and backend!

## Usage

You can access this tool via either our discord bot or website.
- [Discord bot](https://www.ocupdates.com)
- [Website](https://www.ocupdates.com)

## Features

Status updates:
- Detours with their estimated length until completed
- Route cancellations with the trip number
- Station maintenance
- Delays with departing trip with arrival estimates (Depends on available data)

Trip planning:
- Trips with multiple destinations (With customizable arrival and departure times for each destination)
- Filtering to avoid trips using specific routes
- Estimated ETA and fare cost with detailed fare window explanations
- View postions of buses on multiple routes simultaneously
- Adjust minimum and maximum allowable times between transfers
- Set preferred routes
- Adjust walking and cycling speed for more accurate total trip times

Other:
- Route reliability and trip scores (from other users)

Please note that we do not currently support trips and updates from the STO at this time.

## Contributing

If you would like to contribute to the project by requesting features or reporting bugs, please use the [Issues](https://github.com/F14m3head/ocupdates/issues) tab or send us an email.

## License

This project uses the MIT License. For further information please refer to the [MIT License](https://choosealicense.com/licenses/mit/).

## Contact

Here are the different ways you can reach us (We can answer you in both French and English)
- [support@ocupdates.com](mailto:support@ocupdates.com)
