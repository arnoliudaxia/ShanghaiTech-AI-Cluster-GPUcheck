"""
This script fetches GPU utilization data from a specified URL and classifies the GPU models 
by their usage across different nodes. The output highlights nodes with 0% GPU usage, 
indicating idle GPUs that are potentially available for use.
该脚本从指定的 URL 获取 GPU 利用率数据，并根据不同节点的使用情况对 GPU 模型进行分类。
输出会突出显示 GPU 使用率为 0% 的节点、

Author: Arnoliu
Date: 20240921
"""
from colorama import Fore, Style
import requests
from bs4 import BeautifulSoup
from collections import defaultdict

def get_webpage_content(url):
    try:
        # 发送HTTP GET请求到指定的URL
        response = requests.get(url)
        
        # 检查请求是否成功（状态码200表示成功）
        if response.status_code == 200:
            # 将网页内容解析为BeautifulSoup对象
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 返回解析后的内容
            return soup
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def parse_gpu_info(soup):
    results = []
    nodes = soup.find_all('h4')
    
    for node in nodes:
        node_name = node.get_text().split()[0]
        table = node.find_next('table', class_='table table-striped table-condensed')
        if table:
            gpus = table.find_all('tr')[1:]  # Skip the header row
            for gpu in gpus:
                gpu_name = gpu.find_all('td')[1].get_text(strip=True)
                gpu_usage = gpu.find_all('td')[3].find('div', class_='progress-bar')['style'].split(':')[-1].strip()
                
                results.append({
                    'Node Name': node_name,
                    'GPU Model': gpu_name,
                    'GPU Usage': gpu_usage
                })
    
    return results

def classify_by_gpu_model(gpu_info):
    classified_info = defaultdict(list)
    
    for info in gpu_info:
        gpu_model = info['GPU Model']
        gpu_usage = info['GPU Usage']
        
        if gpu_usage == '0%':
            classified_info[gpu_model].append(info['Node Name'])
    
    return classified_info

url = "http://10.15.89.177:8899/gpu"  # 替换为你想要解析的URL
soup = get_webpage_content(url)
name2slujrm={
    "NVIDIA A40":"NVIDIAA40",
    "NVIDIA GeForce RTX 2080 Ti":"NVIDIAGeForceRTX2080Ti",
    "NVIDIA TITAN RTX":"NVIDIATITANRTX",
    "NVIDIA TITAN V":"NVIDIATITANV",
    "NVIDIA TITAN X (Pascal)":"NVIDIATITANXPascal",
    "Tesla M40 24GB":"TeslaM4024GB",
    "NVIDIA GeForce GTX 1080":"NVIDIAGeForceGTX1080",
}

if soup:
    gpu_info = parse_gpu_info(soup)
    classified_info = classify_by_gpu_model(gpu_info)
   
    print(Fore.GREEN + "=====空闲节点列表====")
    print(Style.RESET_ALL)  
    for gpu_model, nodes in classified_info.items():
        print(f"GPU Model: {Fore.YELLOW} {gpu_model if gpu_model not in name2slujrm else name2slujrm[gpu_model]}")
        print(Style.RESET_ALL)
        print(f"Nodes with 0% GPU Usage: {', '.join(nodes)}\n")