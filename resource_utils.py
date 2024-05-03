import subprocess
import torch

def get_total_gpu_memory():
    gpu_memory_bytes = torch.cuda.get_device_properties(0).total_memory
    gpu_memory_gb = round(gpu_memory_bytes / (2**30))
    return gpu_memory_gb

def get_available_vram():
    try:
        _output_to_list = lambda x: x.decode('ascii').split('\n')[:-1]
        
        ACCEPTABLE_AVAILABLE_MEMORY = 1024
        COMMAND = "nvidia-smi --query-gpu=memory.free --format=csv"
        memory_free_info = _output_to_list(subprocess.check_output(COMMAND.split()))[1:]
        memory_free_values = [int(x.split()[0]) for i, x in enumerate(memory_free_info)]
        return memory_free_values
    except Exception as e:
        print('"nvidia-smi" is probably not installed. ', e)
        
        
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
