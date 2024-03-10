# 基于 getCaseResult 提供的处理单个 case 的能力，本文件对所有的 case 进行处理

import getCaseResult
import os
import re
import glob



def Check(cases):
    for case in cases:
        types = ["case_results_cpu2d", "case_results_gpu2d"]
        for type in types:
            path = f"{case}/{type}"
            if os.path.exists(path):
                folders = os.listdir(path)
                for folder in folders:
                    file_path = f"{case}/{type}/{folder}"
                    # folder = cpu2d_skip0_Auto_mgs16_1_regrid8
                    # name = folder[6:]
                    case_res = getCaseResult.Result()
                    match = re.search(r'skip(\d+)', folder)
                    if match:
                        skip = match.group(1)
                        case_res.skip = int(skip)

                    match = re.search(r'(auto|none)', folder, re.IGNORECASE)
                    if match:
                        cycling = match.group(0)
                        case_res.cycling = cycling
                    match = re.search(r'_(\d+)_', folder)
                    if match:
                        max_level = match.group(1)
                        case_res.max_level = int(max_level)         
                    
                    match = re.search(r'mgs(\d+)', folder)
                    if match:
                        mgs = match.group(1)
                        case_res.max_grid_size = int(mgs)
                    
                    match = re.search(r'regrid(\d+)', folder)
                    if match:
                        regrid = match.group(1)
                        case_res.regrid_int = int(regrid)             
                    
                    pattern = f"{file_path}/input*"
                    input_files = glob.glob(pattern)
                    getCaseResult.CheckInput(input_files[0],case_res)


def Get(cases):
    cases_res = {}
    for case in cases:
        print("###################################################################################################################")
        print(f"-----------------------------------------    {case}     -------------------------------------------------")

        # [Result, Result....., Result32]
        res = getCaseResult.CollectData(case)
        

        # 原始数据
        # print(len(res))
        # getResult.Print(res)

        # # 按 cpu_time 排序
        getCaseResult.AdjustResult(res, "cpu_time")
        print("cpu_time 排序")
        getCaseResult.Print(res)
        # # gpu_time 排序
        # getCaseResult.AdjustResult(res, "gpu_time")
        # print("gpu_time 排序")
        # getCaseResult.Print(res)
        # # cycling 排序
        # getResult.AdjustResult(res, "cycling")
        # print("cycling 排序")
        # getResult.Print(res)
        
        # getResult.CompareAndShow(res, "max_grid_size")
        # getResult.CompareAndShow(res, "max_grid_size", "gpu")
        # getResult.CompareAndShow(res, "cycling")
        # getResult.CompareAndShow(res, "cycling", "gpu")
        # getResult.CompareAndShow(res, "max_level")
        # getResult.CompareAndShow(res, "max_level", "gpu")
        # getCaseResult.CompareAndShow(res, "regrid_int")
        # getCaseResult.CompareAndShow(res, "regrid_int", "gpu")
        # getCaseResult.CompareAndShow(res, "skip")
        # getCaseResult.CompareAndShow(res, "skip", "gpu")
        
        
        # getResult.TopFunc(res)

        cases_res[case] = res
    return cases_res

# cases_check = os.listdir(os.getcwd())
# cases_check = ["LidDrivenCavity"]
# Check(cases_check)

cases_get = ["LidDrivenCavity", "FlowPastCylinder"] #  "Bubble" , ，"Bubble", "ConvectedVortex", "DoubleShearLayer", 
cases_res = Get(cases_get)



# ans = getResult.Get(cases_res["LidDrivenCavity"], {"skip" : [1], "cycling" : ['None'], "max_grid_size": [8], "max_level": [2], "regrid_int": [4]})
# getResult.Print(ans)


# 提取前十个最主要的函数
# TopFunc(res)

# 不同 case 的前十个函数的交集等


# 单个函数, 每个case的调用情况
# GetFuncOnEveryCase(res, "scalar_diffusion_update")




