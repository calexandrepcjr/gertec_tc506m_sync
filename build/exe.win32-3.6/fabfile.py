from os import listdir
from sys import exit
import json
import jsonschema
from fabric.api import *
from fabric.contrib.files import *


"""
    Normal use: fab load_config:{subdir_of_server_images} sync_servers
    E.g.: You have lab/ inside server_images/ (server_images/lab/) with
    the tc506/ and config.json there, so just execute - fab load_config:lab sync_servers
"""


# GLOBAL VARIABLES

LOCAL_SERVER_IMAGES_DIR = 'server_images/'
BASIC_SERVER_IMAGE_STRUCTURE = ['tc506', 'config.json']
IGNORED_MEDIAS = ['notfound.bmp', 'preco.bmp']
CONF_JSON_SCHEMA = {
    "$schema": "http://json-schema.org/draft-03/schema",
    "id": "http://jsonschema.net",
    "type": "object",
    "additionalProperties": False,
    "required": True,
    "properties": {
        "user": {
            "type": "string",
            "required": True
        },
        "hosts": {
            "type": "array",
            "required": True
        },
        "passwords": {
            "type": "object",
            "required": True
        },
        "host_port": {
            "type": "number",
            "required": True
        },
        "image_dir": {
            "type": "string",
            "required": True
        },
        "host_image_path": {
            "type": "string",
            "required": True
        }
    }
}

# END GLOBAL VARIABLES


def host_type():
    run('uname -s', shell=False, pty=False)


def host_ip():
    run('hostname -i', shell=False, pty=False)


def check_file_exists(filename, quietRun=True):
    output = run("""if [ -e %s ]
    then
        echo 'True'
    else
        echo 'False'
    fi""" % filename, shell=False, pty=False, quiet=quietRun)
    return output == 'True'


def check_file_permissions(filename, permission_octal=777, quietRun=True):
    output = run("""if [ $(stat -c "%s" %s) == %d ]
    then
        echo 'True'
    else
        echo 'False'
    fi""" % ('%a', filename, permission_octal), shell=False, pty=False, quiet=quietRun)
    return output == 'True'


def check_process_inits_on_start(procName):
    output = run("""if [ -e /etc/rc.d/rc.%s ]
    then
        echo 'True'
    else
        echo 'False'
    fi""" % procName, shell=False, pty=False, quiet=True)
    return output == 'True'


def check_process_is_running(command):
    output = run(command, shell=False, pty=False, quiet=True)
    return output.find('already running') != -1


def is_http_fully_configured():
    main_text_error = "Httpd service is not available, configure first before sync the PDVs: "
    if check_file_exists('/etc/httpd/httpd.conf', True) and check_file_exists('/etc/rc.d/rc.httpd', True):
        print("Httpd is installed in this server")
        if check_file_permissions('/etc/rc.d/rc.httpd', 755):
            print("Httpd process is with proper permissions (755)")
        else:
            run("chmod 755 /etc/rc.d/rc.httpd", shell=False, pty=False)
        if check_process_inits_on_start('httpd'):
            print("Httpd is starting on init")
        else:
            raise EnvironmentError(main_text_error + "Httpd is not starting on init")
        if check_process_is_running('apachectl'):
            print("Httpd is running")
        else:
            print("Httpd is not running")
        return True
    else:
        raise EnvironmentError(main_text_error + "Httpd is not installed in this server (httpd.conf or rc.httpd are not present)")


def validate_file_structure(directory, schema):
    if len(set(directory).intersection(schema)) < len(schema):
        raise ValueError(f"Place must be a valid directory, containing {', '.join(schema)} files")


def validate_json(data, schema):
    try:
        jsonschema.validate(data, schema)
        print('Configuration File (config.json): OK')
    except jsonschema.exceptions.ValidationError as ve:
        raise ValueError('Bad Configuration File (config.json): ' + str(ve))


def load_config(place='lab'):
    try:
        server_images_list = listdir(LOCAL_SERVER_IMAGES_DIR)
        if place not in server_images_list:
            raise FileNotFoundError('Place must be a valid with proper structure in server_images directory')
        server_image_structure = listdir(f'{LOCAL_SERVER_IMAGES_DIR}/{place}')
        validate_file_structure(server_image_structure, BASIC_SERVER_IMAGE_STRUCTURE)
        with open(f'{LOCAL_SERVER_IMAGES_DIR}/{place}/config.json') as json_conf_file:
            server_image_conf = json.load(json_conf_file)
        validate_json(server_image_conf, CONF_JSON_SCHEMA)
        env.update(server_image_conf)
        env.path = f'{LOCAL_SERVER_IMAGES_DIR}/{place}/{env.image_dir}/'
    except Exception as e:
        print("# Failed to sync - " + str(e) + " #")
        exit(1)


def list_files():
    paths_to_check = ['video', 'audio', 'img']
    main_dir = {}
    for path in paths_to_check:
        main_dir[path] = listdir(env.path + path)
    return main_dir


"""
    Function made to the user, when receiving new consulta.php files from gertec doesn't bother to change in
    any place besides the directory itself. The script will find the most actual routine by the filename
"""
def find_consulta_last_version():
    env.consultas_files = []
    for file in listdir(env.path):
        if file.startswith('consulta') and file.endswith('.php'):
            env.consultas_files.insert(0, file)


def create_medias_and_playlists(files):
    if not isinstance(files, dict):
        raise ValueError('Files must be a dictionary of files coming from the env.path')
    media_tags_text = ''
    playlists_text = '\t<playlist id="list1">\n'
    for type, files in files.items():
        count = 1
        for file in files:
            if file in IGNORED_MEDIAS:
                continue
            file_bits = open(env.path + type + '/' + file, 'rb').read()
            md5_checksum = hashlib.md5(file_bits).hexdigest()
            id = type+str(count)
            media_tags_text += f'\t<media id="{id}" dest="INT_MEM" src="http://{env.host}:{env.host_port}/{env.image_dir}/{type}/{file}" md5="{md5_checksum}"/>\n'
            if type == 'img':
                playlists_text += f'\t\t<image id="{id}" duration="5"/>\n'
            elif type == 'video':
                playlists_text += f'\t\t<video id="{id}" loopCount="1"/>\n'
            count += 1
    playlists_text += '\t</playlist>\n'
    return {'medias': media_tags_text, 'playlists': playlists_text}


def create_media_manager_file():
    files = list_files()
    medias_and_playlists = create_medias_and_playlists(files)
    with open(env.path + "media_manager.xml", "w") as media_manager_xml:
        media_manager_xml.write("<?xml version='1.0'?>\n")
        media_manager_xml.write("<media_manager media-version='0.1.0'>\n")
        media_manager_xml.write("<medias>\n")
        media_manager_xml.write(medias_and_playlists['medias'])
        media_manager_xml.write("</medias>\n")
        media_manager_xml.write("<playlists>\n")
        media_manager_xml.write(medias_and_playlists['playlists'])
        media_manager_xml.write("</playlists>\n")
        media_manager_xml.write("<presence-sensor playlistId='list1'/>\n")
        media_manager_xml.write('<grid mode="daily">\n')
        media_manager_xml.write('\t<default playlistId="list1"/>\n')
        media_manager_xml.write('\t<everyday>\n')
        media_manager_xml.write('\t\t<program playlistId="list1" start="05:00" end="23:59"/>\n')
        media_manager_xml.write('\t</everyday>\n')
        media_manager_xml.write('</grid>\n')
        media_manager_xml.write("</media_manager>\n")


def create_price_checker_file():
    find_consulta_last_version()
    with open(env.path + "price_checker.xml", "w") as price_checker_xml:
        price_checker_xml.write("<price_checker version='0.1.0'>\n")
        price_checker_xml.write("\t<urls>\n")
        count = 0
        # To ensure that the start of the price_checker consulting will always be the current server
        all_hosts = env.hosts
        for host in all_hosts:
            if host == env.host:
                all_hosts[count] = env.hosts[0]
                all_hosts[0] = env.host
                break
            count += 1
        count = 1
        for host in all_hosts:
            price_checker_xml.write(f"\t\t<url id='url{count}' value='http://{host}:{env.host_port}/{env.image_dir}/{env.consultas_files[0]}?codigo=&lt;barcode&gt;'/>\n")
            count += 1
        price_checker_xml.write("\t</urls>\n")
        price_checker_xml.write("</price_checker>")


def sync_servers():
    try:
        is_http_fully_configured()
        create_media_manager_file()
        create_price_checker_file()
        with cd(env.host_image_path):
            if check_file_exists(f"{env.image_dir}/"):
                has_backup = False
                if check_file_exists(f"{env.image_dir}_backup/"):
                    has_backup = True
                    run(f"mv {env.image_dir}_backup/ {env.image_dir}_backup_old/", shell=False, pty=False)
                run(f"mv {env.image_dir}/ {env.image_dir}_backup/", shell=False, pty=False)
                if has_backup:
                    run(f"rm -rf {env.image_dir}_backup_old/", shell=False, pty=False)
            put(env.path, '.', mode=777)
            run(f"chmod -R 777 {env.image_dir}/", shell=False, pty=False)
    except Exception as e:
        print("# Failed to sync - " + str(e) + " #")
        exit(1)
