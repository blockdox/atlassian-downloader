# atlassian-downloader
Download Atlassian content into local files

This tool downloads the Atlassian Confluence pages in your account as HTML files, and also creates a specification file
which the [Cofluence Export](https://github.com/cledouarec/confluence-export) tool can read in order to download
your Confluence pages as a consolidated PDF

## Installing

Create a virtual environment, then run:

```shell
pip install -r requirements.txt
```

## Configuration

Copy .env.example to .env and enter your credentials

## Downloading your pages as HTML

Run `python download_confluence.py` with no arguments.

## Downloading your pages as PDF

* Install Confluence Export into your virtual 
* Locate the `download_spec.json` file in the download directory your configured above.
* Run it in the directory of your _.env_ file, using a command like the one below, adjusting to the path of your download spec:

```shell
confluence-export download_spec.json
```
