# Gertec TC506M Sync

A program to help the sysadmin to sync Gertec TC506M data across the servers.

## Requirements
- [Python 3]
- [Fabric 3] - Remote routines
- [JsonSchema] - config.json validation
- [cx_Freeze] - Exe GUI Builder

## Usage
- The server_images/ directory must be in the same place that the fabfile.py or gertec_tc506m_sync.exe (console mode/GUI mode);
- Copy the server_images/lab/ directory and paste inside server_images/ under the respective place name - 
	This helps when you need to remember the last synced content with that place;
- Inside the directory, change the values inside the config.json to your servers credentials. You can register as many servers as you want;
```
	{
	    "user": "root",
	    "hosts": [
	        "127.0.0.1"
	    ],
	    "passwords": {
	        "root@127.0.0.1": "123456"
	    },
	    "host_port": 8600,
	    "image_dir": "tc506",
	    "host_image_path": "/var/www/"
	}
```
	- User will be global to all the servers;
	- Hosts list;
	- Hosts' passwords dict;
	- Host port that your tc506 directory will be accessed;
	- Which name your tc506 dir will have in the server;
	- Where your tc506 dir will be put; (Usually in the httpd htdocs);
- Inside the tc506/ directory, you will put a valid tc506/ structure (video, audio, img, php files);
- To regenerate .exe, execute (with the packages listed in setup.py installed on your computer):
    ```python setup.py build```
- To run the GUI without generate the exe file:
``` python gertec_tc506m_sync.py ```
- To run inside console (inside the same directory than the fabfile.py with the dependencies installed):
    ``` fab goto:{dir_name_inside_server_images_directory} sync_servers ```

## TO DO
- [ ] Proper multilanguage support;
- [ ] Realtime content sync into terminal frame inside GUI;
- [ ] Multimedia optimization before send to the servers to ensure that uploaded media is valid/has proper
quality for the device;
- [ ] Configuration inside the software;
- [ ] Files management inside the software;

[Python 3]: <https://www.python.org/downloads/>
[Fabric 3]: <https://pypi.org/project/Fabric3/>
[JsonSchema]: <https://pypi.org/project/jsonschema/>
[cx_Freeze]: <https://pypi.org/project/cx_Freeze/>