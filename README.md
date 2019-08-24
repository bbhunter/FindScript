# FindScript
A tool that scrapes Google and Github to find files with a given extension from a given url.

## How it works

You give FindScript a URL and it queries a google search, regex the results URLs out of it, gets the source code of the resulted URLs and tries to find your desired files in it. Simultaneously, it does the same with Github. It queries a Github code search, gets the content of each of the results and tries to find your desired files in them. <br/>
It saved me a ton of since going throgh the results manually can take ages.

## Dependencies

FindScript uses [PyGithub](https://github.com/PyGithub/PyGithub) and [colorama](https://github.com/tartley/colorama). <br/>
`pip3 install -r requirements.txt`
<br/> <br/>
You will also need to create a Github Token with no permissions to effectively use the Github API. You can do that here: https://github.com/settings/tokens. Save the token and replace `YOUR_TOKEN_HERE` with your token. 

## Usage

```
$ python3 FindScript.py -h

  ______ _           _  _____           _       _   
 |  ____(_)         | |/ ____|         (_)     | |  
 | |__   _ _ __   __| | (___   ___ _ __ _ _ __ | |_ 
 |  __| | | '_ \ / _` |\___ \ / __| '__| | '_ \| __|
 | |    | | | | | (_| |____) | (__| |  | | |_) | |_ 
 |_|    |_|_| |_|\__,_|_____/ \___|_|  |_| .__/ \__|
                                         | |        
                                         |_| 
Version: 1.1
By 0x41CoreDump


usage: FindScript.py [-h] -u URL [--include-unresolvable] [-e EXTENSION]
                     [-gop GOOGLE_PAGES] [-gip GITHUB_PAGES] [-o OUTPUT]

Scrape Scripts From Google And Github

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     The Target Domain
  --include-unresolvable
                        Include Non Resolvable URLs To The List
  -e EXTENSION, --extension EXTENSION
                        What Extension To Look For, Default: js
  -gop GOOGLE_PAGES, --google_pages GOOGLE_PAGES
                        How Many Google Pages To Search, Default: 15
  -gip GITHUB_PAGES, --github_pages GITHUB_PAGES
                        How Many Github Pages To Search, Default: 5
  -o OUTPUT, --output OUTPUT

```

