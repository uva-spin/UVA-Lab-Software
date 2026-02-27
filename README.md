# Startup

## Website Server (`/uvaspin`)

The website is hosted on `twist`. Navigate to twist and enter the `/uvaspin` directory. To start the server, run 

```npm run build``` 

(if you've made any edits to the code, otherwise skip this step). 

The website is managed by the daemon process manager [pm2](https://pm2.keymetrics.io/). To start, type:

```pm2 start uvaspin```

The website processed is run under the name `uvaspin`. 

If no process is currently being ran (i.e., no process with the name `uvaspin` exists), you can create the process by running `pm2` with the app script being `/uvaspin/main.jsx

Here is a list of commands for managing the website:

```
$ pm2 restart app_name
$ pm2 reload app_name
$ pm2 stop app_name
$ pm2 delete app_name
```

More information on pm2 documentation can be found [here](https://pm2.keymetrics.io/docs/usage/quick-start/).

The file structure for the website is as follows:

```
uvaspin
├── html
│   └── lab42
└── src
    ├── assets --> For any images/styles/videos/etc.
    │   ├── css
    │   └── images
    ├── components --> Buttons, slides, banners, etc. 
    │   └── ui
    ├── constants --> Any sort of constants data (hash tables, etc., NOT config info)
    ├── containers --> Containers for components
    ├── pages
    │   ├── home
    │   ├── lab36
    │   ├── lab42
    │   └── shared --> Shared react components
    └── utils --> Used right now for plotting, db querying, etc.
```

## DAQ  (`/daq`)

This portion is ran solely on the DAQ tower's computer in the lab. Ideally, this will be switched over to being controlled entirely from twist, so it won't be necessary to run two seperate codes in different locations.

```
daq
├── acquisition --> Code that continously run acquistion
├── core --> functions for database pipelining, insertation, connection, and schema data
├── devices --> Scripts for each individual DAQ device to get data
└── testing --> Testing scripts for each device
```

In the current state, the DAQ portion of the code *must* be ran on the DAQ tower's computer. 

To run, all you need to do is navigate to `/daq` and run

```run.py```

An interface on the terminal with information about device acqusition statuses is displayed and updated continously. 