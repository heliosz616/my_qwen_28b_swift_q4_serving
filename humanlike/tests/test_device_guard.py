import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from device_guard import parse_devices,resolve_devices,NVIDIA,AMD

def test_missing_external_gpu_cannot_select_integrated():
    available={'CUDA0':NVIDIA,'Vulkan0':NVIDIA,'Vulkan1':'AMD Radeon(TM) 860M Graphics'}
    with pytest.raises(ValueError,match='missing'):
        resolve_devices('CUDA0,Vulkan1',available)

def test_external_gpu_index_change_is_resolved_by_identity():
    available={'CUDA0':NVIDIA,'Vulkan0':NVIDIA,'Vulkan1':'AMD Radeon(TM) 860M Graphics','Vulkan2':AMD}
    selected,identities=resolve_devices('CUDA0,Vulkan1',available)
    assert selected=='CUDA0,Vulkan2'
    assert resolve_devices(selected,available,identities)[0]==selected

def test_duplicate_gpu_and_explicit_integrated_are_rejected():
    available={'CUDA0':NVIDIA,'Vulkan0':NVIDIA,'Vulkan1':AMD,'Vulkan2':'AMD Radeon(TM) 860M Graphics'}
    with pytest.raises(ValueError):resolve_devices('CUDA0,Vulkan0',available,explicit=True)
    with pytest.raises(ValueError):resolve_devices('CUDA0,Vulkan2',available,explicit=True)
    assert resolve_devices('Vulkan1,CUDA0',available,explicit=True)[0]=='Vulkan1,CUDA0'

def test_inventory_parser_and_ambiguous_identity():
    output=f'Available devices:\n  CUDA0: {NVIDIA} (8150 MiB, 7043 MiB free)\n  Vulkan2: {AMD} (16368 MiB, 15123 MiB free)'
    assert parse_devices(output)=={'CUDA0':NVIDIA,'Vulkan2':AMD}
    with pytest.raises(ValueError,match='ambiguous'):
        resolve_devices('CUDA0,Vulkan1',{'CUDA0':NVIDIA,'Vulkan1':AMD,'Vulkan2':AMD})
