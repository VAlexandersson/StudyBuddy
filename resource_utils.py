import os
import signal
import torch
from pynvml import nvmlInit, nvmlShutdown, NVMLError, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo, nvmlDeviceGetComputeRunningProcesses, nvmlSystemGetProcessName



def get_available_vram(unit: str = 'G'):
    try:
        nvmlInit()
        handle = nvmlDeviceGetHandleByIndex(0)
        memory_info = nvmlDeviceGetMemoryInfo(handle)
        nvmlShutdown()
        available_vram = round(memory_info.free / (2 ** {'B': 0, 'K': 10, 'M': 20, 'G': 30}.get(unit, 30)), 3)
        return available_vram
        
    except NVMLError as error:
        print(f'Failed to get available VRAM: {error}')

def get_gpu_processes_usage():
    try:
        nvmlInit()
        handle = nvmlDeviceGetHandleByIndex(0)
        procs = nvmlDeviceGetComputeRunningProcesses(handle)
        gpu_usage_values = [{"pid": proc.pid, 'memory_usage': proc.usedGpuMemory, 'name': nvmlSystemGetProcessName(proc.pid)} for proc in procs]
        nvmlShutdown()
        return gpu_usage_values
    except NVMLError as error:
        print(f'Failed to get GPU process usage: {error}')

def get_total_vram():
    nvmlInit()
    handle = nvmlDeviceGetHandleByIndex(0)
    gpu_memory_bytes = nvmlDeviceGetMemoryInfo(handle).total
    nvmlShutdown()
    gpu_memory_gb = round(gpu_memory_bytes / (2**30), 3)
    return gpu_memory_gb

def kill_gpu_processes(gpu_usage_values, verbose: bool = False):
    for process in gpu_usage_values:
        try:
            pid = process['pid']
            os.kill(pid, signal.SIGKILL)
            if(verbose):
                print(f"Killed process {pid}")
        except OSError:
            print(f"Failed to kill process {process['pid']}")
        
        
def get_model_num_params(model: torch.nn.Module):
    return sum([param.numel() for param in model.parameters()])

def get_model_mem_size(model: torch.nn.Module):
    """
    Get how much memory a PyTorch model takes up.

    See: https://discuss.pytorch.org/t/gpu-memory-that-model-uses/56822
    """
    # Get model parameters and buffer sizes
    mem_params = sum([param.nelement() * param.element_size() for param in model.parameters()])
    mem_buffers = sum([buf.nelement() * buf.element_size() for buf in model.buffers()])

    # Calculate various model sizes
    model_mem_bytes = mem_params + mem_buffers # in bytes
    model_mem_mb = model_mem_bytes / (1024**2) # in megabytes
    model_mem_gb = model_mem_bytes / (1024**3) # in gigabytes

    return {"model_mem_bytes": model_mem_bytes,
            "model_mem_mb": round(model_mem_mb, 2),
            "model_mem_gb": round(model_mem_gb, 2)}
