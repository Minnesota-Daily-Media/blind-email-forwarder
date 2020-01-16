# Blind Email Forwarder

The Blid Email Forwarder is an open-source software platform that uses a Gmail mailbox as a temporary holding space to forward emails based off of an annoymous address.

## Requirements

This software requires Python 3, as well as a single Gmail account that will have all mail forwarded to it.

Additionally, OAuth2 credentials will need to be created to authorize the Gmail account with this software.

## Installation

Use pip to install all dependencies included within requirements.txt

```bash
pip install -r requirements.txt
```

## Usage

This software can be called using CRON, using some other scheduling application, or manually.

```bash
python main.py
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)