"""Resolve the two required physical GPUs by identity, never by a stale Vulkan index."""
import re

NVIDIA='NVIDIA GeForce RTX 5060 Laptop GPU'
AMD='AMD Radeon RX 9070'
DEFAULT_IDENTITIES={'CUDA0':NVIDIA,'Vulkan0':NVIDIA,'Vulkan1':AMD}

def parse_devices(output):
    result={}
    for line in output.splitlines():
        match=re.match(r'\s*(CUDA\d+|Vulkan\d+):\s+(.+?)\s+\(\d+ MiB,',line)
        if match:result[match[1]]=match[2]
    return result

def resolve_devices(requested,available,identities=None,explicit=False):
    identities=identities or DEFAULT_IDENTITIES
    selected=[];resolved={}
    for old in requested.split(','):
        old=old.strip()
        expected=available.get(old) if explicit else identities.get(old)
        if expected not in (NVIDIA,AMD):
            raise ValueError(f'Unsupported or unknown GPU identity for {old}: {expected!r}; required RTX 5060 + RX 9070')
        family=re.sub(r'\d+$','',old)
        matches=[device for device,name in available.items() if name==expected and device.startswith(family)]
        if len(matches)!=1:
            raise ValueError(f'Required GPU {expected!r} on {family} is missing or ambiguous. Check eGPU power/USB4; refusing an integrated-GPU fallback. Available: {available}')
        selected.append(matches[0]);resolved[matches[0]]=expected
    if len(selected)!=2 or set(resolved.values())!={NVIDIA,AMD}:
        raise ValueError('Exactly one RTX 5060 and one RX 9070 are required; duplicate physical GPUs are forbidden')
    return ','.join(selected),resolved
