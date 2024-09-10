from glob import glob
import re
path = "/home/lion/Documents/TU/PLA/ppa-ss24-twipr_gui/scioi_hardware_manager/scioi_hardware_manager/extensions/websockets/"

def generate_docs(file_path):
    # read the whole content of the file
    with open(file_path, 'r') as file:
        content = file.read()
    class_txt = content.split("def")[0].split("class")[1]
    class_name = class_txt.split("(")[0]
    class_description = content.split("def")[0].split('"""')[1]
    output_string = f"# {class_name}\n\n{class_description}\n\n"
    output_string += "## Functions:\n\n"
    # split the contnent at def ...(...): using regex
    functions = re.split("def ", content)
    for i,function in enumerate(functions):
        if i == 0:
            continue
        function_name = re.split(r"\(", function)[0]
        if function_name[0] == "_":
            function_name = "privat " + function_name
        else:
            function_name = "public " + function_name
        comment = re.split('"""', function)[1]
        discritption = comment.split(":")[0]
        parameters = comment.split(":param")[1:]
        parameter_dict = {}
        for parameter in parameters:
            parameter_name = parameter.split(":")[0]
            parameter_description = parameter.split(":")[1].split("\n")[0]
            parameter_dict[parameter_name] = parameter_description
        output_string += f"### {function_name}\n\n{discritption}\n\n"
        # check if the parameter_dict is not empty
        if len(parameter_dict) > 0:
            output_string += "#### Parameters:\n\n"
        for parameter_name, parameter_description in parameter_dict.items():
            parameter_name = parameter_name.replace(" ","")
            output_string += f"- **{parameter_name}:** {parameter_description}\n"
        output_string += "\n---\n"
    output_file_path = file_path.replace(".py", ".md")
    with open(output_file_path, 'w') as file:
        file.write(output_string)
    pass
# Get the list of all python files in the directory
files = glob(f"{path}/**/*.py", recursive=True)
for i, file in enumerate(files):
    if "generate_docs" in file or "init" in file:
        continue
    generate_docs(file)

