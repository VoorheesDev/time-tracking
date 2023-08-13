## Overview
<p align="justify">
The main goal of the project is obtaining time-tracking information using clockify API.
For now the script is able to retrieve all time entries for a user on each workspace.

To use this project you need to register on [clockify.me](https://clockify.me/) and generate an API key.
</p>



## Installation
In order to test this project on your local machine, do the following:
#### Clone the repo
```bash
git clone https://github.com/VoorheesDev/time-tracking.git
cd time-tracking
```

#### Create and activate a virtual environment
+ For <b>Linux</b>:
```bash
python3 -m venv venv
source venv/bin/activate
```

+ For <b>Windows</b>:
```bash
python -m venv venv
.\venv\Scripts\activate
```

#### Install requirements
```bash
pip install -r requirements/base.txt
```

## Runtime Environment

Environmental data is set up via .ENV file. Create ".env" file in the "time-tracking" directory next to the "main.py" module. The file must include the following info:

```env
API_KEY=
```

## Usage
Run the script by using the following command:
```bash
python main.py
```
