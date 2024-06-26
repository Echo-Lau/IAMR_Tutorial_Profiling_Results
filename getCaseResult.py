# All the functionality provided in this document is intended to process the results of calculations for a single case
 
import os
import pandas as pd
import re
from datetime import datetime
import glob
import sys
import saveFile
import io



class Result:
    def __init__(self) -> None:
        self.name = ""
        self.dim = ""

        self.skip:int = -1 
        self.cycling:str = ""
        self.max_level:int = -1
        self.max_grid_size:int = -1
        self.regrid_int:int = -1

        self.cpu_time:float = -1
        self.cpu_step:int = -1
        self.cpu_function_name = []
        self.cpu_function_percent = []

        self.gpu_time:float = -1 
        self.gpu_step:int = -1
        self.gpu_function_name = []
        self.gpu_function_percent = []
        self.gpu_memory = -1 

    def __str__(self):
        return f"{self.skip} {self.cycling} {self.max_level} {self.max_grid_size} {self.regrid_int} {self.cpu_time} {self.gpu_step} {self.gpu_time} {self.cpu_step}"

    def __repr__(self):
        return f"{self.skip} {self.cycling} {self.max_level} {self.max_grid_size} {self.regrid_int} {self.cpu_time} {self.cpu_step} {self.gpu_time} {self.cpu_step}"
    
    def __eq__(self, other):
        if isinstance(other, Result):
            return self.skip == other.skip and self.cycling == other.cycling and self.max_grid_size == other.max_grid_size and self.max_level == other.max_level and self.regrid_int == other.regrid_int
        return False
    
    def Update(self, other):
        if self.cpu_time < 0 : 
            self.cpu_time = other.cpu_time
            self.cpu_step = other.cpu_step
            self.cpu_function_name = other.cpu_function_name
            self.cpu_function_percent = other.cpu_function_percent
        if self.gpu_time < 0 : 
            self.gpu_time = other.gpu_time
            self.gpu_step = other.gpu_step
            self.gpu_function_name = other.gpu_function_name
            self.gpu_function_percent = other.gpu_function_percent
            self.gpu_memory = other.gpu_memory

        
def CheckInput(path_input, case_res):
    flag = True
    with open(path_input, 'r') as file:
        while(True):
            line = file.readline()
            list_para = ["skip", "max_grid_size", "max_level", "cycling", "regrid_int"]
            for para in list_para: 
                if para in line and "=" in line:
                    line.strip()
                    if not line.startswith("#"):
                        pattern = re.compile(r'=(.*?)#')
                        match = pattern.search(line)
                        if match:
                            value = match.group(1).strip()
                            if not value == str(getattr(case_res,para)):
                                print("\033[0;31mERROR: Parameters and filenames are different\033[0m")
                                print(f"path : {path_input}")  
                                print(f"line : {line}")
                                flag = False
                    else:
                        print("\033[0;31mERROR:  comment error\033[0m")
                        print(f"path : {path_input}")
                        print(f"line : {line}")
                        flag = False
            if line == '':
                break

    return flag            

 
# Print the list [Result1, Result2, ... ]
def Print(list_result):
    header = ["name", "dim", "skip_level_projector", "cycling", "max_level", "max_grid_size", "regrid_int", "cpu_time/s", "cpu_step", "gpu_time/s", "gpu_memory/MB", "gpu step"]
    table = []
    for v in list_result:
        # cpu2d_skip0_Auto_mgs16_1_regrid8
        row = []
        row.append(v.name)
        row.append(v.dim)
        row.append(v.skip)
        row.append(v.cycling)
        row.append(v.max_level)
        row.append(v.max_grid_size)
        row.append(v.regrid_int)
        row.append(v.cpu_time)
        row.append(v.cpu_step)
        row.append(v.gpu_time)
        row.append(v.gpu_memory)
        row.append(v.gpu_step)
        table.append(row)
            
    df = pd.DataFrame(table, columns= header, index=range(1, len(table)+1))    
    if not df.empty:
        # print("###################################################################################################################")
        print("-------------------------------------------------------------------------------------------------------------------")
        print(df)    

        # df.to_csv(f'table_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv', index=False)

def Save(list_result):
    output_name = f'table_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt'
    sys.stdout = open(output_name, 'w')
    Print(list_result)
    sys.stdout = sys.__stdout__

def Collect(case, dim):
        flag_checkInput = True
        res = []

        types = []
        if dim == "2d":
            types = ["case_results_cpu2d", "case_results_gpu2d"]
        if dim == "3d":
            types = ["case_results_cpu3d", "case_results_gpu3d"]

        for type in types:
            path = f"{case}/{type}"
            if os.path.exists(path):
                # folds = ['cpu2d_skip0_Auto_mgs16_1_regrid4', ...]
                folders = os.listdir(path)
                for folder in folders:
                    file_path = f"{case}/{type}/{folder}"
                    files = os.listdir(file_path)
                    
                    case_res = Result()
                    
                    case_res.name = case
                    case_res.dim = dim

                    # get parameters
                    patterns = {
                        'skip(\d+)': 'skip',
                        '(auto|none)': 'cycling',
                        '_(\d+)_': 'max_level',
                        'mgs(\d+)': 'max_grid_size',
                        'regrid(\d+)': 'regrid_int'
                    }
                    for pattern, attribute in patterns.items():
                        match = re.search(pattern, folder, re.IGNORECASE)
                        if match:
                            # value  = int(match.group(1))
                            value = match.group(1)
                            if value.isdigit():
                                value = int(value)
                    
                            setattr(case_res, attribute, value)
      
                    
                    pattern = f"{file_path}/input*"
                    input_files = glob.glob(pattern)
                    if not CheckInput(input_files[0],case_res):
                        flag_checkInput = False


                    # get total time step fuction function percent  memory for cpu and gpu

                    # with open(f"{file_path}/log.txt", 'r') as file:
                    #     while(True):
                    #         line = file.readline()
                    #         if "Total Timers" in line:
                    #             numbers = [float(s) for s in line.split() if s.replace('.', '', 1).isdigit()]
                    #             if "cpu" in type:
                    #                 setattr(case_res, "cpu_time", numbers[0])
                    #                 break
                    #             if "gpu" in type:
                    #                 setattr(case_res, "gpu_time", numbers[0])
                    #                 break
                    
                    #         if line == '':
                    #             break                    
                    
                    # with open(f"{file_path}/log.txt", 'r') as file:                      
                    #         found_start = False
                    #         flag = 2
                    #         for line in file:
                    #             if "Function Name" in line:
                    #                 flag -= 1 
                    #                 if flag == 0:
                    #                     found_start = True
                    #                 continue
                    #             elif "=====" in line: 
                    #                 break
                    #             if found_start:
                    #                 line_data = line.split()
                    #                 if "cpu" in type:
                    #                       getattr(case_res, "cpu_function_name").append(line_data[0])
                    #                       getattr(case_res, "cpu_function_percent").append(line_data[len(line_data)-2])                     
                    #                 if "gpu" in type:
                    #                     setattr(case_res, "gpu_time", numbers[0])
                    #                     break                                        

                    
                    if "cpu" in type:
                        # get cpu_steps

                        for file in files:
                            match = re.match(r"chk(\d+)", file)
                            if match:
                                case_res.cpu_step = max(int(match.group(1)), case_res.cpu_step)

                        with open(f"{file_path}/log.txt", 'r') as file:
                            while(True):
                                line = file.readline()
                                if "Total Timers" in line:
                                    numbers = [float(s) for s in line.split() if s.replace('.', '', 1).isdigit()]
                                    case_res.cpu_time = numbers[0]
                                    break
                                
                                if line == '':
                                    break
                        
                        with open(f"{file_path}/log.txt", 'r') as file:                      
                                found_start = False
                                flag = 2
                                for line in file:
                                    if "Function Name" in line:
                                        flag -= 1 
                                        if flag == 0:
                                            found_start = True
                                        continue
                                    elif "=====" in line: 
                                        break
                                    if found_start:
                                        line_data = line.split()
                                        case_res.cpu_function_name.append(line_data[0])
                                        case_res.cpu_function_percent.append(line_data[len(line_data)-2])
                    
                    if "gpu" in type:
                        for file in files:
                            match = re.match(r"chk(\d+)", file)
                            if match:
                                case_res.gpu_step = max(int(match.group(1)), case_res.gpu_step)       

                        with open(f"{file_path}/log.txt", 'r') as file:
                            while(True):
                                line = file.readline()
                                if "Total Timers" in line:
                                    numbers = [float(s) for s in line.split() if s.replace('.', '', 1).isdigit()]
                                    case_res.gpu_time = numbers[0]
                                    break
                                if line == '':
                                    break
                        
                        with open(f"{file_path}/log.txt", 'r') as file:
                            while(True):
                                line = file.readline()
                                if "[The         Arena] space allocated" in line:
                                    numbers = [float(s) for s in line.split() if s.replace('.', '', 1).isdigit()]
                                    case_res.gpu_memory = numbers[0]
                                    break
                                if line == '':
                                    break                        
                        with open(f"{file_path}/log.txt", 'r') as file:                      
                                found_start = False
                                flag = 2
                                for line in file:
                                    if "Function Name" in line:
                                        flag -= 1 
                                        if flag == 0:
                                            found_start = True
                                        continue
                                    elif "=====" in line: 
                                        break
                                    if found_start:
                                        line_data = line.split()
                                        case_res.gpu_function_name.append(line_data[0])
                                        case_res.gpu_function_percent.append(line_data[len(line_data)-2])
                                        
                    found = False
                    for item in res:
                        if item == case_res:
                            item.Update(case_res)
                            found = True
                            break
                    if not found:
                        res.append(case_res)
                
        if not flag_checkInput:
            print("已退出")
            exit()
        return res

def CollectData(case_path):
    """
    1. read the result log of all the parameter combinations under a certain case folder, and extract the key information, such as cpu_time, gpu_time, function and time...
    2. provide check input function to make sure the result folder name is the same as the parameters used in the actual case.
    3. the input parameter is the case folder path, it can be the current file path: "lidDrivenCavity", or any other path "... /... /result/lidDrivenCavity".
    3. return: returns a list = [Result1, Result2, ... Result32] to access the results
    """
    case = os.path.basename(case_path)
    res = []
    res.append(Collect(case,"2d"))
    res.append(Collect(case,"3d"))
    return res
    

def Get(vec_res, factors = {}):    
    vec_factor = {
        "skip" : [0 , 1],
        "cycling" : ["Auto", "None"],
        "max_level" : [1, 2],
        "max_grid_size" : [8, 16],
        "regrid_int" : [4, 8],
    }    
    for k, v in factors.items():
        vec_factor[k] = v
    # import pdb; pdb.set_trace()
    ans = []

    for skip in vec_factor["skip"]:
        for cycling in vec_factor["cycling"]:
            for max_level in vec_factor["max_level"]:
                for max_grid_size in vec_factor["max_grid_size"]:
                    for regrid_int in vec_factor["regrid_int"]:
                        for item in vec_res:
                            if( item.skip == skip and
                                item.cycling == cycling and
                                item.max_level == max_level  and
                                item.max_grid_size == max_grid_size and 
                                item.regrid_int == regrid_int ):
                                ans.append(item)
    return ans
  
def CompareAndShow(vec_res, factor, processor = "cpu"):
    
    vec = {
        "skip" : [0, 1],
        "cycling": ["Auto", "None"],
        "max_grid_size" : [8, 16],
        "max_level" : [1, 2],
        "regrid_int" : [4, 8]
    }
    
    vec_compare = []
    for x in vec[factor]:
        temp = Get(vec_res, {factor : [x]})
        vec_compare.append(temp)
    
    ans = 0
    error = 0
    items_true = []
    items_false = []
    min_delta_cpu_time = float('inf'); max_delta_cpu_time = 0
    min_delta_gpu_time = float('inf'); max_delta_gpu_time = 0
    for i in range(len(vec_compare[0])):
        v0 = vec_compare[0]
        v1 = vec_compare[1]
        
        min_delta_cpu_time = min(min_delta_cpu_time, abs(v0[i].cpu_time - v1[i].cpu_time))
        max_delta_cpu_time = max(max_delta_cpu_time, abs(v0[i].cpu_time - v1[i].cpu_time))
        
        min_delta_gpu_time = min(min_delta_gpu_time, abs(v0[i].gpu_time - v1[i].gpu_time))
        max_delta_gpu_time = max(max_delta_gpu_time, abs(v0[i].gpu_time - v1[i].gpu_time))

        if processor == "cpu":
            if (v0[i].cpu_time == -1 or v1[i].cpu_time == -1):
                error += 1
            if (v0[i].cpu_time >  v1[i].cpu_time):
                ans+=1
                temp = []
                temp.append(v0[i])
                temp.append(v1[i])
                items_true.append(temp)
            else:
                temp = []
                temp.append(v0[i])
                temp.append(v1[i])
                items_false.append(temp)
        elif processor == "gpu":
            if (v0[i].gpu_time == -1 or v1[i].gpu_time == -1):
                error += 1
            if (v0[i].gpu_time >  v1[i].gpu_time):
                ans+=1
                temp = []
                temp.append(v0[i])
                temp.append(v1[i])
                items_true.append(temp)
            else:
                temp = []
                temp.append(v0[i])
                temp.append(v1[i])
                items_false.append(temp)

    
    # 其他参数相同，比较 {factor}, 共有 {total} 种情况，其中 {factor} : {vec[factor][0]} slower than  {vec[factor][1]}  = 共有 {ans} 种
    # error表示该例子没有得到time， time == -1 
    print("####################################################################################################################")
    print(f"{processor} || total : 16, error : {error} || {factor:<{15}} : {vec[factor][0]:>{8}} slower than {vec[factor][1]:<{8}} : {ans:>{8}}  ")
    print(f"min_delta_cpu_time: {min_delta_cpu_time}")
    print(f"max_delta_cpu_time: {max_delta_cpu_time}")
    print(f"min_delta_gpu_time: {min_delta_gpu_time}")
    print(f"max_delta_gpu_time: {max_delta_gpu_time}")


    # # 打印详细信息
    print(f"The following are all examples for {factor} : {vec[factor][0]} slower than {vec[factor][1]}")
    for items in items_true:
        Print(items)

    print(f"The following are all examples for {factor} : {vec[factor][0]} faster than {vec[factor][1]}")
    for items in items_false:
        Print(items)

def AdjustResult(list_result, para):
    if len(list_result) != 0:
        print(f"sort by {para}")
        # sort by parameter
        if para == 'cpu_time':
            list_result.sort(key=lambda x: x.cpu_time)
        elif para == 'gpu_time':
            list_result.sort(key=lambda x: x.gpu_time)
        elif para == 'max_grid_size':
            list_result.sort(key=lambda x: (x.max_grid_size, x.cpu_time, x.gpu_time))  
        elif para == "cycling":
            list_result.sort(key=lambda x: (x.cycling, x.cpu_time, x.gpu_time))  
        Print(list_result)

def TopFunc(list_result,n=3, cpu_print = True, gpu_print = True):

    for v in list_result:
        print(f"{v.skip} {v.cycling} {v.max_level} {v.max_grid_size} {v.regrid_int}      || skip cycling max_level max_grid_size regid_int")
        if cpu_print:
            for i in range(n):
                if(len(v.cpu_function_name) != 0):
                    print(f"cpu {v.cpu_function_name[i]}  {v.cpu_function_percent[i]}%")
        if gpu_print:
            for i in range(n):
                if(len(v.gpu_function_name) != 0):
                    print(f"gpu {v.gpu_function_name[i]}  {v.gpu_function_percent[i]}%")            
        print("")

def GetFuncOnEveryCase(dictionary, str):
    for k, v in dictionary.items():
        print(k)
        case_res = []
        for name, ele in v.items():
            funcInfo = ele[2]
            for kv in funcInfo:
                for key, value in kv.items():
                    if str in key:
                        temp = []
                        temp.append(name)
                        temp.append(value)
                        case_res.append(temp)
                        break
        print(case_res)


# 给参数，找到一个结果。展示一个结果。展示一个结果的memory。对比两个case，对比两个case，展示对比

# def AdjustResult(dictionary, factor):
    
#     return




# 不同 case 的前十个函数的交集等
# 单个函数, 每个case的调用情况
# GetFuncOnEveryCase(res, "scalar_diffusion_update")


