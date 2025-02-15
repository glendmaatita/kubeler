import yaml, os, sys, subprocess, shutil, jinja2
from .models.kubeler import Kubeler

tmp_dir = "/tmp/kubeler"

class Installer:
    def __init__(self, installer, kube_config):
        self.installer = installer
        self.kube_config = kube_config

        # get the directory path of the installer and kube_config
        self.installer_dir_path = os.path.dirname(installer)
        self.kube_config_path = os.path.dirname(kube_config)

        # create tmp dir if not exists
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

    def install(self):
        kubeler = self.load_config()
        
        # process init
        init_cmd = kubeler.init.cmd
        for command in init_cmd:
            cmd = command.split()
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
            for line in process.stdout:
                print(line, end="")
                sys.stdout.flush()
            process.wait()

        # process steps
        steps = kubeler.group.steps
        for step in steps:
            # extract step information
            step_name = step.name
            dir = os.path.join(self.installer_dir_path, step.dir)
            files = step.files
            vars = step.vars

            # if files is not defined in installer.yaml, load all files in the directory
            if files == None:
                files = self.load_files_in_dir(dir)
                
            for file in files:
                file_path = os.path.join(dir, file)
                config_path = os.path.join(tmp_dir, file)

                # set execution dir. It will be in tmp folder if vars is defined
                execution_dir = dir
                if vars != None:
                    # copy files for execution
                    shutil.copy(file_path, config_path) 

                    # create dictionary of variables
                    vars_dict = {var.name: var.value for var in vars}
                    # using jinja, replace variables in file
                    with open(config_path, "r") as config_file:
                        template_content = config_file.read()
                        template = jinja2.Template(template_content)
                        rendered_yaml = template.render(vars_dict)

                        with open(config_path, "w") as config_file:
                            config_file.write(rendered_yaml)
                    
                    # update dir variable
                    execution_dir = tmp_dir
                
                # get commands defined in the file
                commands = self.load_file(file_path)
                for command in commands:
                    print("Executing command: ", command)
                    cmd = command.split()
                    process = subprocess.Popen(cmd, cwd=execution_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, universal_newlines=True)
                    for line in process.stdout:
                        print(line, end="")
                        sys.stdout.flush()
                    process.wait()

                # if config_path exists, restore the file
                if os.path.exists(config_path):
                    os.remove(config_path)
                
    # if there some files in the directory, load them
    def load_files_in_dir(self, dir):
        files = []
        for file in os.listdir(dir):
            if os.path.isfile(os.path.join(dir, file)):
                files.append(file)
        return files

    # load commands on each files    
    def load_file(self, file_path):
        commands = []
        with open(file_path, "r") as file:
            for line in file:
                if line.startswith("#cmd:"):
                    command = line.split(":", 1)[1].strip()
                    commands.append(command)
        return commands

    #  load the configuration file and parse to Kubeler model
    def load_config(self) -> Kubeler:
        data = self.open_config()
        kubeler = Kubeler(**data)

        # handle reference variables
        for step in kubeler.group.steps:
            if step.vars != None:
                for var in step.vars:
                    if var.value.startswith("ref."):
                        ref_var = var.value.split("ref.")[1]
                        ref_vars = ref_var.split(".")
                        step_name = ref_vars[0]
                        var_name = ref_vars[2]
                        for step in kubeler.group.steps:
                            if step.vars != None:
                                if (step.name == step_name):
                                    for ref in step.vars:
                                        if ref.name == var_name:
                                            var.value = ref.value
        return kubeler

    # open the configuration file    
    def open_config(self):
        with open(self.installer, 'r') as stream:
            try:
                data = yaml.safe_load(stream)
                return data
            except yaml.YAMLError as exc:
                raise ValueError("Failed to load configuration")