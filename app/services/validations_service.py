import torch

def check_cuda_warning():
    if torch.cuda.is_available():
        print("CUDA is available and will be used")
    else:
        print("CPU will be used because CUDA is not available")
