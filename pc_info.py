import psutil
import wmi

def get_computer_info():
    w = wmi.WMI()

    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage("C:").percent
    total_disk = int(psutil.disk_usage("C:").total / (2**30))
    space = int(psutil.disk_usage("C:").free / (2**30))

    ram_usage = f"{ram_usage} %"
    disk_usage = f"{disk_usage} %"
    total_disk = f"{total_disk} GB"
    space = f"{space} GB"

    cpu_name = w.Win32_Processor()[0].name
    core = psutil.cpu_count(logical=False)
    gpu_info = w.Win32_VideoController()
    gpu = []
    for i in gpu_info:
        gpu.append(i.Name)

    return disk_usage, ram_usage, total_disk, space, gpu, cpu_name, core